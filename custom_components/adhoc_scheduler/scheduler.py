"""Scheduler module for adhoc scheduler."""
from dataclasses import dataclass
from datetime import datetime as datetime_sys, timedelta
from functools import partial
import logging

from homeassistant.core import (
    CALLBACK_TYPE,
    Context,
    HassJob,
    HomeAssistant,
    ServiceCall,
)
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.script import Script
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util, ulid as ulid_util

from .const import (
    CONF_ACTION,
    CONF_DELAY,
    CONF_DELAY_FROM,
    CONF_ID,
    CONF_NAME,
    CONF_TRIGGER_TIME,
    DOMAIN,
    EVENT_ACTION_EXECUTED,
    SCHEDULER_STORAGE_KEY,
    SCHEDULER_STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class Action:
    """Class for keeping track of an item in inventory."""

    id: str
    name: str
    script: Script
    action_conf: dict
    fire_time: datetime_sys
    orig_context: dict
    unschedule_fn: CALLBACK_TYPE | None = None

    @property
    def delay(self) -> timedelta:
        """Calculate Delay."""
        return self.fire_time - dt_util.utcnow()

    def to_dict(self):
        """Convert dataClass to Dict."""
        return {
            "id": self.id,
            "name": self.name,
            "orig_context": self.orig_context,
            "action_conf": self.action_conf,
            "fire_time": self.fire_time.timestamp(),
        }


class Scheduler:
    """Scheduler class."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the scheduler."""
        self.hass: HomeAssistant = hass
        self.scheduled_actions: dict[str, Action] = {}
        self._store = Store[dict[str, dict]](
            hass,
            SCHEDULER_STORAGE_VERSION,
            SCHEDULER_STORAGE_KEY,
        )

    async def async_load(self) -> None:
        """Load saved actions."""
        stored = await self._store.async_load()
        if stored is None:
            return

        for value in stored:
            fire_time = value.get("fire_time")
            fire_time = dt_util.utc_from_timestamp(fire_time)

            script = Script(self.hass, value["action_conf"], value["name"], DOMAIN)

            action = Action(
                id=value["id"],
                fire_time=fire_time,
                orig_context=value["orig_context"],
                name=value["name"],
                action_conf=value["action_conf"],
                script=script,
            )

            self.scheduled_actions[action.id] = action
            await self._schedule_action(action)

    async def _save_actions(self):
        """Write Actions to file to restore on Startup."""
        actions_dict = [action.to_dict() for action in self.scheduled_actions.values()]
        await self._store.async_save(actions_dict)

    async def _unschedule_action_by_id(self, action_id: str):
        """Unschedule Action via its ID."""
        if action_id not in self.scheduled_actions:
            _LOGGER.info(
                "Action %s is not in the list of scheduled actions.", action_id
            )
            return

        existing_action = self.scheduled_actions[action_id]
        await self._unschedule_action(existing_action)
        self.scheduled_actions.pop(action_id)

        await self._save_actions()

    async def _unschedule_action(self, action: Action):
        """Remove action from hass loop."""
        if action.unschedule_fn is not None:
            action.unschedule_fn()

            _LOGGER.info(
                "Unscheduled %s and removed from HASS Job list.",
                action.name,
            )
        else:
            _LOGGER.info(
                "%s doesn't appear to be scheduled.",
                action.name,
            )

    async def _schedule_action(self, action: Action):
        """Add Action to hass loop.

        Fires immeditly if action fire_time was in the past.
        """
        job = HassJob(
            partial(self.execute_action, action=action), cancel_on_shutdown=True
        )

        action.unschedule_fn = async_call_later(
            hass=self.hass, delay=action.delay, action=job
        )

        _LOGGER.info(
            "Scheduled %s to run at %s seconds from now",
            action.name,
            action.delay.total_seconds(),
        )

    async def delete_schedule(self, call: ServiceCall):
        """Delete a schedule."""
        config = call.data
        action_id = config.get(CONF_ID)

        await self._unschedule_action_by_id(action_id)

        _LOGGER.info("Deleted Schedule: %s", action_id)

    async def add_schedule(self, call: ServiceCall):
        """Add a schedule."""
        config = call.data

        action_conf = config.get(CONF_ACTION)
        name = config.get(CONF_NAME)
        if name is None:
            name = f"action_{len(self.scheduled_actions) + 1}"

        action_id = config.get(CONF_ID)
        if action_id is None:
            action_id = ulid_util.ulid()

        if action_id in self.scheduled_actions:
            await self._unschedule_action_by_id(action_id)

        script = Script(self.hass, action_conf, name, DOMAIN)
        orig_context = call.context.as_dict()

        if (fire_time := config.get(CONF_TRIGGER_TIME)) is None:
            # if we don't have a trigger time, then we're dealing with a Delay.

            delay_from = config.get(CONF_DELAY_FROM)
            if delay_from is None:
                delay_from = dt_util.utcnow()
            else:
                delay_from = dt_util.as_utc(delay_from)

            fire_time = delay_from + config[CONF_DELAY]

        fire_time = dt_util.as_utc(fire_time)

        action = Action(
            id=action_id,
            name=name,
            script=script,
            fire_time=fire_time,
            orig_context=orig_context,
            action_conf=action_conf,
        )

        self.scheduled_actions[action.id] = action
        await self._save_actions()

        await self._schedule_action(action)

        _LOGGER.info("Added Schedule: %s", action.id)

    async def execute_action(self, *args, action: Action, **kwargs):
        """Execute the provided action."""

        user_id = (
            None if action.orig_context is None else action.orig_context["user_id"]
        )
        trigger_context = Context(user_id=user_id)

        if action.script is None:
            action.script = Script(self.hass, action.action_conf, action.name, DOMAIN)

        self.hass.bus.async_fire(
            EVENT_ACTION_EXECUTED,
            {"id": action.id, "name": action.name},
            context=trigger_context,
        )

        await action.script.async_run(context=trigger_context)

        self.scheduled_actions.pop(action.id)
        await self._save_actions()

        _LOGGER.info("Ran scheduled Script: %s:%s", action.id, action.name)
