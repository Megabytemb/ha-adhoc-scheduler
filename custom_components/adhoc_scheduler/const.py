"""Constants for adhoc_scheduler."""
from logging import Logger, getLogger

import voluptuous as vol

from homeassistant.const import CONF_DELAY, CONF_ID, CONF_NAME, CONF_TRIGGER_TIME
import homeassistant.helpers.config_validation as cv

LOGGER: Logger = getLogger(__package__)

################################
# Do not change! Will be set by release workflow
INTEGRATION_VERSION = "0.3.1"  # x-release-please-version
################################

NAME = "Adhoc Scheduler"
DOMAIN = "adhoc_scheduler"

CONF_ACTION = "action"
CONF_ACTIONS = "actions"
CONF_DELAY_FROM = "delay_from"

SERVICE_SCHEDULE = "schedule"
SERVICE_DELETE_SCHEDULE = "delete_schedule"

EVENT_ACTION_EXECUTED = DOMAIN + "_action_executed"

SCHEDULER_STORAGE_VERSION = 1
SCHEDULER_STORAGE_KEY = f"{DOMAIN}_actions"

SCHEDULE_SERVICE_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Optional(CONF_NAME): str,
            vol.Optional(CONF_ID): str,
            vol.Optional(CONF_ACTION): cv.SCRIPT_SCHEMA,
            vol.Optional(CONF_ACTIONS): cv.SCRIPT_SCHEMA,
            vol.Optional(CONF_DELAY): cv.positive_time_period_template,
            vol.Optional(CONF_TRIGGER_TIME): cv.datetime,
            vol.Optional(CONF_DELAY_FROM): cv.datetime,
        }
    ),
    cv.has_at_least_one_key(CONF_TRIGGER_TIME, CONF_DELAY),
    cv.has_at_least_one_key(CONF_ACTION, CONF_ACTIONS),
    # Verify that we don't have both
    lambda value: value
    if not (CONF_ACTION in value and CONF_ACTIONS in value)
    else (_ for _ in ()).throw(
        vol.Invalid(f"Cannot specify both '{CONF_ACTION}' and '{CONF_ACTIONS}'")
    ),
)

DELETA_SCHEDULE_SERVICE_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required(CONF_ID): str,
        }
    )
)
