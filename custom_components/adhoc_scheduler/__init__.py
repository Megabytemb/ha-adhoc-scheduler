"""Custom integration to integrate adhoc_scheduler with Home Assistant.

For more details about this integration, please refer to
https://github.com/Megabytemb/ha-adhoc-scheduler
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_START, Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    DELETA_SCHEDULE_SERVICE_SCHEMA,
    DOMAIN,
    SCHEDULE_SERVICE_SCHEMA,
    SERVICE_DELETE_SCHEDULE,
    SERVICE_SCHEDULE,
)
from .scheduler import Scheduler

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    scheduler = hass.data[DOMAIN]["scheduler"] = Scheduler(hass)

    async def _async_startup(event):
        """Init on startup."""
        await scheduler.async_load()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    async def async_handle_schedule_service(call: ServiceCall):
        await scheduler.add_schedule(call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SCHEDULE,
        async_handle_schedule_service,
        schema=SCHEDULE_SERVICE_SCHEMA,
    )

    async def async_handle_delete_schedule_service(call: ServiceCall):
        await scheduler.delete_schedule(call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_SCHEDULE,
        async_handle_delete_schedule_service,
        schema=DELETA_SCHEDULE_SERVICE_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
