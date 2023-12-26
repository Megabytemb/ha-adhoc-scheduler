"""Constants for adhoc_scheduler."""
from logging import Logger, getLogger

import voluptuous as vol

from homeassistant.const import CONF_DELAY, CONF_NAME, CONF_TRIGGER_TIME
import homeassistant.helpers.config_validation as cv

LOGGER: Logger = getLogger(__package__)

################################
# Do not change! Will be set by release workflow
INTEGRATION_VERSION = "0.1.3"  # x-release-please-version
################################

NAME = "Adhoc Scheduler"
DOMAIN = "adhoc_scheduler"

CONF_ACTION = "action"
CONF_DELAY_FROM = "delay_from"

SERVICE_SCHEDULE = "schedule"

EVENT_ACTION_EXECUTED = DOMAIN + "_action_executed"

SCHEDULER_STORAGE_VERSION = 1
SCHEDULER_STORAGE_KEY = f"{DOMAIN}_actions"

SCHEDULE_SERVICE_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Optional(CONF_NAME): str,
            vol.Required(CONF_ACTION): cv.SCRIPT_SCHEMA,
            vol.Optional(CONF_DELAY): cv.positive_time_period_template,
            vol.Optional(CONF_TRIGGER_TIME): cv.datetime,
            vol.Optional(CONF_DELAY_FROM): cv.datetime,
        }
    ),
    cv.has_at_least_one_key(CONF_DELAY, CONF_TRIGGER_TIME),
)
