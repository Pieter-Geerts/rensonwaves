"""Binary sensor platform for Renson WAVES integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RensonWavesCoordinator
from . import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    coordinator: RensonWavesCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WifiConnectedBinarySensor(coordinator, entry),
        DecisionRoomBoostEnabledBinarySensor(coordinator, entry),
        SilentEnabledBinarySensor(coordinator, entry),
        BreezeEnabledBinarySensor(coordinator, entry),
    ]

    async_add_entities(entities)


class RensonWavesBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for Renson WAVES binary sensors."""

    def __init__(
        self,
        coordinator: RensonWavesCoordinator,
        entry: ConfigEntry,
        unique_key: str,
        name: str,
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['serial']}_{unique_key}"
        self._attr_device_name = entry.title
        self._attr_name = name


class WifiConnectedBinarySensor(RensonWavesBinarySensorBase):
    """WiFi connected binary sensor."""

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "wifi_connected", "WiFi Connected")

    @property
    def is_on(self) -> bool:
        status = self.coordinator.data.get("wifi_status", {}).get("status", "")
        return str(status).lower() == "connected"


class DecisionRoomBoostEnabledBinarySensor(RensonWavesBinarySensorBase):
    """Decision room boost enabled binary sensor."""

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "decision_boost_enabled", "Boost Enabled")

    @property
    def is_on(self) -> bool:
        return bool(
            self.coordinator.data.get("decision_room", {})
            .get("boost", {})
            .get("enable")
        )


class SilentEnabledBinarySensor(RensonWavesBinarySensorBase):
    """Silent mode enabled binary sensor."""

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "silent_enabled", "Silent Mode")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("decision_silent", {}).get("enable"))


class BreezeEnabledBinarySensor(RensonWavesBinarySensorBase):
    """Breeze enabled binary sensor."""

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "breeze_enabled", "Breeze Mode")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("decision_breeze", {}).get("enable"))
