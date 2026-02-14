"""Fan platform for Renson WAVES integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
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

    _attr_supported_features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF

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
        serial = entry.data.get("serial", entry.entry_id)
        self._attr_unique_id = f"{serial}_fan_{actuator_id}"
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
    def percentage(self) -> int | None:
        """Return current percentage."""
        actuators = self.coordinator.data.get("actuator", {})
        actuator = actuators.get(self.actuator_id, {})
        params = actuator.get("parameter", {})
        pwm = params.get("pwm", {}).get("value", 0)
        return int(pwm)

    def _resolve_room_identifier(self) -> str:
        """Resolve room identifier used by room boost endpoint."""
        room = None
        if isinstance(self.actuator_data, dict):
            room = self.actuator_data.get("room")
            if room is None:
                room = self.actuator_data.get("name")

        if room is None:
            room = self.actuator_id

        return str(room)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on fan.

        WAVES currently exposes room boost style control; non-zero percentage is
        accepted but mapped to boost enable with default payload.
        """
        if percentage == 0:
            await self.async_turn_off()
            return

        room = self._resolve_room_identifier()
        result = await self.coordinator.async_set_room_boost(
            room=room,
            enable=True,
        )
        if not result:
            raise HomeAssistantError(f"Failed to turn on fan for room '{room}'")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off fan."""
        room = self._resolve_room_identifier()
        _LOGGER.debug("Turning off fan for room '%s'", room)
        result = await self.coordinator.async_set_room_boost(
            room=room,
            enable=False,
            level=0.0,
            timeout=0,
            remaining=0,
        )
        if not result:
            raise HomeAssistantError(f"Failed to turn off fan for room '{room}'")
