"""Data coordinator for Renson WAVES integration."""
from __future__ import annotations

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

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data from device."""
        try:
            data = await self.client.async_get_constellation()
            
            if not data:
                raise UpdateFailed("Failed to fetch data from WAVES device")
            
            return data
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with WAVES device: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        await self.client.async_close()
        await super().async_shutdown()
