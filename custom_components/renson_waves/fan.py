"""Fan platform for Renson WAVES integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RensonWavesCoordinator
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up fan entities."""
    coordinator: RensonWavesCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Get actuator data from coordinator
    if coordinator.data:
        actuators = coordinator.data.get("actuator", {})
        
        for actuator_id, actuator_data in actuators.items():
            actuator_type = actuator_data.get("type")
            
            if actuator_type == "ventilation fan":
                entities.append(
                    VentilationFan(coordinator, entry, actuator_id, actuator_data)
                )
    
    async_add_entities(entities)


class VentilationFan(CoordinatorEntity, FanEntity):
    """Ventilation fan entity."""

    _attr_supported_features = FanEntityFeature.SET_SPEED

    def __init__(
        self,
        coordinator: RensonWavesCoordinator,
        entry: ConfigEntry,
        actuator_id: str,
        actuator_data: dict[str, Any],
    ) -> None:
        """Initialize fan."""
        super().__init__(coordinator)
        self.actuator_id = actuator_id
        self.actuator_data = actuator_data
        self._attr_unique_id = f"{entry.data['serial']}_fan_{actuator_id}"
        self._attr_name = actuator_data.get("name", f"fan_{actuator_id}")

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        actuators = self.coordinator.data.get("actuator", {})
        actuator = actuators.get(self.actuator_id, {})
        params = actuator.get("parameter", {})
        pwm = params.get("pwm", {}).get("value", 0)
        return pwm > 0

    @property
    def speed(self) -> int:
        """Return current speed."""
        actuators = self.coordinator.data.get("actuator", {})
        actuator = actuators.get(self.actuator_id, {})
        params = actuator.get("parameter", {})
        pwm = params.get("pwm", {}).get("value", 0)
        # Convert PWM (0-100) to percentage
        return int(pwm)

    @property
    def speed_range(self) -> tuple[int, int]:
        """Return speed range."""
        return (0, 100)

    @property
    def percentage(self) -> int | None:
        """Return current percentage."""
        return self.speed

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on fan."""
        if percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            await self.async_set_percentage(50)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off fan."""
        await self.async_set_percentage(0)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed."""
        # If asked to stop the fan (0%), map this to disabling the room boost
        # by sending the expected payload to the device via the coordinator.
        if percentage == 0:
            # Determine room identifier: prefer explicit mapping if present,
            # fall back to actuator name or actuator id.
            room = None
            # actuator_data may contain a 'room' key depending on device data
            if isinstance(self.actuator_data, dict):
                room = self.actuator_data.get("room")
                if room is None:
                    room = self.actuator_data.get("name")

            if room is None:
                room = self.actuator_id

            _LOGGER.debug("Stopping fan; setting room boost disable for '%s'", room)

            # Send disable payload: enable=false, level=0.0, timeout=0, remaining=0
            result = await self.coordinator.async_set_room_boost(
                room=room, enable=False, level=0.0, timeout=0, remaining=0
            )

            if not result:
                _LOGGER.error("Failed to stop fan / disable room boost for '%s'", room)
            return

        # Non-zero percentage control is currently not implemented.
        _LOGGER.warning(
            "Manual fan speed (%s%%) control not implemented. "
            "Only stop (0%%) is supported at the moment.",
            percentage,
        )
