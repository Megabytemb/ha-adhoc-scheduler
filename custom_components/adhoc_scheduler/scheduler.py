"""Scheduler module for adhoc scheduler."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
import logging

from homeassistant.core import Context, HassJob, HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.script import Script
from homeassistant.helpers.storage import Store
from homeassistant.util import ulid as ulid_util

from .const import (
    CONF_ACTION,
    CONF_DELAY,
    CONF_DELAY_FROM,
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
    fire_time: datetime
    orig_context: dict

    @property
    def delay(self) -> timedelta:
        """Calculate Delay."""
        return self.fire_time - datetime.now()

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
        self.hass = hass
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
            fire_time = datetime.fromtimestamp(fire_time)

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

    async def _schedule_action(self, action: Action):
        """Add Action to hass loop."""
        job = HassJob(
            partial(self.execute_action, action=action), cancel_on_shutdown=True
        )

        async_call_later(hass=self.hass, delay=action.delay, action=job)

        _LOGGER.info(
            "Scheduled %s to run at %s seconds from now",
            action.name,
            action.delay.total_seconds(),
        )

    async def add_schedule(self, call: ServiceCall):
        """Add a schedule."""
        config = call.data

        action_conf = config.get(CONF_ACTION)
        name = config.get(CONF_NAME)
        if name is None:
            name = f"action_{len(self.scheduled_actions) + 1}"

        script = Script(self.hass, action_conf, name, DOMAIN)
        orig_context = call.context.as_dict()

        action_id = ulid_util.ulid()

        if (fire_time := config.get(CONF_TRIGGER_TIME)) is None:
            # if we don't have a trigger time, then we're dealing with a Delay.

            delay_from = config.get(CONF_DELAY_FROM, datetime.now())

            fire_time = delay_from + config[CONF_DELAY]

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

        _LOGGER.info("Added Schedule.")

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
