"""Data coordinator for Renson WAVES integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .client import RensonWavesClient

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


class RensonWavesCoordinator(DataUpdateCoordinator):
    """Coordinator for Renson WAVES data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Renson WAVES",
            update_interval=SCAN_INTERVAL,
        )
        
        self.client = RensonWavesClient(
            host=entry.data["host"],
            port=entry.data.get("port", 80),
        )
        self.entry = entry

    async def async_set_room_boost(
        self,
        room: str,
        enable: bool = True,
        level: float = 21.0,
        timeout: int = 900,
        remaining: int = 0,
    ) -> bool:
        """Wrapper to set a room boost via the client and refresh data.

        Returns True on success.
        """
        try:
            result = await self.client.async_set_room_boost(
                room=room,
                enable=enable,
                level=level,
                timeout=timeout,
                remaining=remaining,
            )

            if result:
                # Refresh coordinator data after a successful change
                await self.async_request_refresh()

            return result
        except Exception as err:
            _LOGGER.error("Error setting room boost for %s: %s", room, err)
            return False

    async def async_set_room_boost_default(
        self,
        enable: bool = True,
        level: float = 21.0,
        timeout: int = 900,
        remaining: int = 0,
    ) -> bool:
        """Set room boost without specifying a room.

        Returns True on success.
        """
        try:
            result = await self.client.async_set_room_boost_default(
                enable=enable,
                level=level,
                timeout=timeout,
                remaining=remaining,
            )

            if result:
                await self.async_request_refresh()

            return result
        except Exception as err:
            _LOGGER.error("Error setting default room boost: %s", err)
            return False

    async def async_set_decision_silent(self, payload: dict[str, Any]) -> bool:
        """Set silent mode configuration.

        Returns True on success.
        """
        try:
            result = await self.client.async_set_decision_silent(payload)

            if result:
                await self.async_request_refresh()

            return result
        except Exception as err:
            _LOGGER.error("Error setting silent mode: %s", err)
            return False

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data from device."""
        try:
            data = await self.client.async_get_constellation()
            
            if not data:
                raise UpdateFailed("Failed to fetch data from WAVES device")

            results = await asyncio.gather(
                self.client.async_get_global_uptime(),
                self.client.async_get_wifi_status(),
                self.client.async_get_decision_room(),
                self.client.async_get_decision_silent(),
                self.client.async_get_decision_breeze(),
                return_exceptions=True,
            )

            keys = [
                "global_uptime",
                "wifi_status",
                "decision_room",
                "decision_silent",
                "decision_breeze",
            ]

            for key, result in zip(keys, results):
                if isinstance(result, Exception):
                    _LOGGER.debug("Optional endpoint %s failed: %s", key, result)
                    data[key] = {}
                else:
                    data[key] = result or {}

            return data
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with WAVES device: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        await self.client.async_close()
        await super().async_shutdown()
