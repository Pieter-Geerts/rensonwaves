"""API client for Renson WAVES device."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class RensonWavesClient:
    """Client for communicating with Renson WAVES device."""

    def __init__(self, host: str, port: int = 80) -> None:
        """Initialize the client."""
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.session: aiohttp.ClientSession | None = None

    async def async_get_constellation(self) -> dict[str, Any]:
        """Get complete device configuration."""
        return await self._async_request("/v1/constellation")

    async def async_get_sensors(self) -> dict[str, Any]:
        """Get sensor data."""
        return await self._async_request("/v1/constellation/sensor")

    async def async_get_actuators(self) -> dict[str, Any]:
        """Get actuator data."""
        return await self._async_request("/v1/constellation/actuator")

    async def _async_request(
        self, endpoint: str, method: str = "GET", **kwargs: Any
    ) -> dict[str, Any]:
        """Make a request to the device."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, timeout=aiohttp.ClientTimeout(total=10), **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    _LOGGER.error(
                        "Error from WAVES device %s: HTTP %s", 
                        self.host, 
                        response.status
                    )
                    return {}
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to WAVES device %s", self.host)
            return {}
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error to WAVES device %s: %s", self.host, err)
            return {}
        except Exception as err:
            _LOGGER.error("Unexpected error from WAVES device %s: %s", self.host, err)
            return {}

    async def async_close(self) -> None:
        """Close the session."""
        if self.session:
            await self.session.close()
