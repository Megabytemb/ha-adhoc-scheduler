"""Sensor platform for adhoc_scheduler."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import NAME

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="adhoc_scheduler",
        name="Integration Sensor",
        icon="mdi:format-quote-close",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up the sensor platform."""
    async_add_devices(
        IntegrationBlueprintSensor(
            config_entry=entry,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class IntegrationBlueprintSensor(SensorEntity):
    """adhoc_scheduler Sensor class."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        self.entity_description = entity_description
        self._config_entry = config_entry
        self._name = NAME
        self._attr_unique_id = f"{config_entry.entry_id}-tts"

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        return 5
