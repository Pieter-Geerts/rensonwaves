"""The Renson WAVES integration."""
from __future__ import annotations

import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import RensonWavesCoordinator

_LOGGER: logging.Logger = logging.getLogger(__name__)

DOMAIN: Final = "renson_waves"
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.FAN,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Renson WAVES from a config entry."""
    
    coordinator = RensonWavesCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services for room boost control
    async def _handle_start_room_boost(call):
        """Handle service call to start a room boost."""
        room = call.data.get("room")
        if room is None:
            _LOGGER.error("start_room_boost called without 'room' in data")
            return

        level = call.data.get("level", 21.0)
        timeout = call.data.get("timeout", 900)
        remaining = call.data.get("remaining", 0)

        await coordinator.async_set_room_boost(
            room=room, enable=True, level=level, timeout=timeout, remaining=remaining
        )

    async def _handle_stop_room_boost(call):
        """Handle service call to stop a room boost."""
        room = call.data.get("room")
        if room is None:
            _LOGGER.error("stop_room_boost called without 'room' in data")
            return

        await coordinator.async_set_room_boost(room=room, enable=False)

    async def _handle_set_room_boost_default(call):
        """Handle service call to set default room boost."""
        enable = call.data.get("enable", True)
        level = call.data.get("level", 21.0)
        timeout = call.data.get("timeout", 900)
        remaining = call.data.get("remaining", 0)

        await coordinator.async_set_room_boost_default(
            enable=enable,
            level=level,
            timeout=timeout,
            remaining=remaining,
        )

    async def _handle_set_silent_mode(call):
        """Handle service call to set silent mode configuration."""
        payload = call.data.get("payload")
        if not isinstance(payload, dict):
            current = coordinator.data.get("decision_silent", {}) if coordinator.data else {}
            payload = {
                "enable": call.data.get("enable", current.get("enable", False)),
                "reduction": call.data.get("reduction", current.get("reduction", 0)),
            }

            for day in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]:
                if day in call.data:
                    payload[day] = call.data[day]
                elif day in current:
                    payload[day] = current[day]

        await coordinator.async_set_decision_silent(payload)

    hass.services.async_register(
        DOMAIN,
        "start_room_boost",
        _handle_start_room_boost,
        schema=None,
    )

    hass.services.async_register(
        DOMAIN,
        "stop_room_boost",
        _handle_stop_room_boost,
        schema=None,
    )

    hass.services.async_register(
        DOMAIN,
        "set_room_boost_default",
        _handle_set_room_boost_default,
        schema=None,
    )

    hass.services.async_register(
        DOMAIN,
        "set_silent_mode",
        _handle_set_silent_mode,
        schema=None,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
