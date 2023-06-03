"""Describe logbook events."""
from homeassistant.components.logbook import (
    LOGBOOK_ENTRY_ICON,
    LOGBOOK_ENTRY_MESSAGE,
    LOGBOOK_ENTRY_NAME,
)
from homeassistant.core import callback

from .const import DOMAIN, EVENT_ACTION_EXECUTED, NAME


@callback
def async_describe_events(hass, async_describe_event):
    """Describe logbook events."""

    @callback
    def async_describe_logbook_event(event):
        """Describe a logbook event."""

        name = event.data["name"]
        message = f"executed action {name}"

        return {
            LOGBOOK_ENTRY_NAME: NAME,
            LOGBOOK_ENTRY_MESSAGE: message,
            LOGBOOK_ENTRY_ICON: "mdi:timelapse",
        }

    async_describe_event(DOMAIN, EVENT_ACTION_EXECUTED, async_describe_logbook_event)
