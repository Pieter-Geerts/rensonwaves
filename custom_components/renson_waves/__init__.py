"""The Renson WAVES integration."""
from __future__ import annotations

import logging
from typing import Final

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .coordinator import RensonWavesCoordinator

_LOGGER: logging.Logger = logging.getLogger(__name__)

DOMAIN: Final = "renson_waves"
DAY_KEYS: Final[list[str]] = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def _coerce_room(value: object) -> str:
    """Normalize room value from service payload."""
    if value is None:
        raise vol.Invalid("room is required")

    if isinstance(value, str):
        room = value.strip()
        if not room:
            raise vol.Invalid("room cannot be empty")
        return room

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(int(value))

    raise vol.Invalid("room must be a string or number")


def _validate_set_silent_mode_payload(data: dict) -> dict:
    """Ensure at least one input key is provided for set_silent_mode."""
    if not data:
        raise vol.Invalid("At least one field must be provided")
    return data


SERVICE_START_ROOM_BOOST_SCHEMA: Final = vol.Schema(
    {
        vol.Required("room"): vol.All(vol.Any(str, int, float), _coerce_room),
        vol.Optional("level", default=21.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=200)),
        vol.Optional("timeout", default=900): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        vol.Optional("remaining", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
    }
)

SERVICE_STOP_ROOM_BOOST_SCHEMA: Final = vol.Schema(
    {
        vol.Required("room"): vol.All(vol.Any(str, int, float), _coerce_room),
    }
)

SERVICE_SET_ROOM_BOOST_DEFAULT_SCHEMA: Final = vol.Schema(
    {
        vol.Optional("enable", default=True): cv.boolean,
        vol.Optional("level", default=21.0): vol.All(vol.Coerce(float), vol.Range(min=0, max=200)),
        vol.Optional("timeout", default=900): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        vol.Optional("remaining", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
    }
)

SERVICE_SET_SILENT_MODE_SCHEMA: Final = vol.All(
    vol.Schema(
        {
            vol.Optional("payload"): dict,
            vol.Optional("enable"): cv.boolean,
            vol.Optional("reduction"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
            vol.Optional("monday"): dict,
            vol.Optional("tuesday"): dict,
            vol.Optional("wednesday"): dict,
            vol.Optional("thursday"): dict,
            vol.Optional("friday"): dict,
            vol.Optional("saturday"): dict,
            vol.Optional("sunday"): dict,
        }
    ),
    _validate_set_silent_mode_payload,
)

SERVICES: Final[list[str]] = [
    "start_room_boost",
    "stop_room_boost",
    "set_room_boost_default",
    "set_silent_mode",
]
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
    async def _handle_start_room_boost(call: ServiceCall) -> None:
        """Handle service call to start a room boost."""
        room = call.data.get("room")

        level = call.data.get("level", 21.0)
        timeout = call.data.get("timeout", 900)
        remaining = call.data.get("remaining", 0)

        await coordinator.async_set_room_boost(
            room=room, enable=True, level=level, timeout=timeout, remaining=remaining
        )

    async def _handle_stop_room_boost(call: ServiceCall) -> None:
        """Handle service call to stop a room boost."""
        room = call.data.get("room")

        await coordinator.async_set_room_boost(room=room, enable=False)

    async def _handle_set_room_boost_default(call: ServiceCall) -> None:
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

    async def _handle_set_silent_mode(call: ServiceCall) -> None:
        """Handle service call to set silent mode configuration."""
        payload = call.data.get("payload")
        if not isinstance(payload, dict):
            current = coordinator.data.get("decision_silent", {}) if coordinator.data else {}
            payload = {
                "enable": call.data.get("enable", current.get("enable", False)),
                "reduction": call.data.get("reduction", current.get("reduction", 0)),
            }

            for day in DAY_KEYS:
                if day in call.data:
                    payload[day] = call.data[day]
                elif day in current:
                    payload[day] = current[day]

        await coordinator.async_set_decision_silent(payload)

    hass.services.async_register(
        DOMAIN,
        "start_room_boost",
        _handle_start_room_boost,
        schema=SERVICE_START_ROOM_BOOST_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "stop_room_boost",
        _handle_stop_room_boost,
        schema=SERVICE_STOP_ROOM_BOOST_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "set_room_boost_default",
        _handle_set_room_boost_default,
        schema=SERVICE_SET_ROOM_BOOST_DEFAULT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "set_silent_mode",
        _handle_set_silent_mode,
        schema=SERVICE_SET_SILENT_MODE_SCHEMA,
    )

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
            for service in SERVICES:
                if hass.services.has_service(DOMAIN, service):
                    hass.services.async_remove(DOMAIN, service)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
