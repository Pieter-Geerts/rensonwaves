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

    _attr_supported_features = (
        FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF | FanEntityFeature.SET_SPEED
    )

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
        pwm_value = params.get("pwm", {}).get("value", 0)
        try:
            pwm = int(float(pwm_value))
        except Exception:
            pwm = 0
        # Ensure we return a 0-100 percentage
        return max(0, min(100, pwm))

    async def async_added_to_hass(self) -> None:
        """Log entity support on add for debugging."""
        await super().async_added_to_hass()
        _LOGGER.debug(
            "VentilationFan added: entity_id=%s supported_features=%s",
            self.entity_id,
            self.supported_features,
        )

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

        # If a percentage is provided, prefer setting percentage (speed)
        if percentage is not None:
            await self.async_set_percentage(percentage)
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

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed percentage (0-100).

        The WAVES API expects a `level` value; map 0-100%% to the device scale.
        Observed API captures contain levels up to 200.0, so map percentage -> level by scaling to 200.
        """
        if percentage is None:
            return

        if percentage == 0:
            await self.async_turn_off()
            return

        pct = max(0, min(100, int(percentage)))
        # Map 0-100% to device level 0-200 (observed in API captures)
        level = float(pct) * 2.0

        room = self._resolve_room_identifier()
        _LOGGER.debug(
            "Setting fan for room '%s' to %s%% -> level=%s", room, pct, level
        )
        result = await self.coordinator.async_set_room_boost(
            room=room, enable=True, level=level
        )
        if not result:
            raise HomeAssistantError(
                f"Failed to set fan percentage for room '{room}' to {pct}%"
            )
