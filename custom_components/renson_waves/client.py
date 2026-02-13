"""API client for Renson WAVES device."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
import typing

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

    async def async_get_constellation(self) -> dict[str, typing.Any]:
        """Get complete device configuration."""
        return await self._async_request("/v1/constellation")

    async def async_get_sensors(self) -> dict[str, typing.Any]:
        """Get sensor data."""
        return await self._async_request("/v1/constellation/sensor")

    async def async_get_actuators(self) -> dict[str, typing.Any]:
        """Get actuator data."""
        return await self._async_request("/v1/constellation/actuator")

    async def async_get_global_uptime(self) -> dict[str, typing.Any]:
        """Get device uptime."""
        return await self._async_request("/v1/global/uptime")

    async def async_get_wifi_status(self) -> dict[str, typing.Any]:
        """Get WiFi client status."""
        return await self._async_request("/v1/wifi/client/status")

    async def async_get_decision_room(self) -> dict[str, typing.Any]:
        """Get decision room data."""
        return await self._async_request("/v1/decision/room")

    async def async_get_decision_silent(self) -> dict[str, typing.Any]:
        """Get silent mode configuration."""
        return await self._async_request("/v1/decision/silent")

    async def async_get_decision_breeze(self) -> dict[str, typing.Any]:
        """Get breeze mode configuration."""
        return await self._async_request("/v1/decision/breeze")

    async def _async_request(
        self, endpoint: str, method: str = "GET", **kwargs: typing.Any
    ) -> dict[str, typing.Any]:
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

    async def async_set_room_boost(
        self,
        room: str,
        enable: bool = True,
        level: float = 21.0,
        timeout: int = 900,
        remaining: int = 0,
    ) -> bool:
        """Send a PUT request to set room boost.

        Example endpoint: PUT /v1/decision/room/{room}/boost
        Body: {"enable": true, "level": 21.0, "timeout": 900, "remaining": 0}
        Returns True on success (HTTP 200/204), False otherwise.
        """
        endpoint = f"/v1/decision/room/{room}/boost"
        payload = {
            "enable": enable,
            "level": float(level),
            "timeout": int(timeout),
            "remaining": int(remaining),
        }

        if self.session is None:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.put(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status in (200, 204):
                    _LOGGER.debug("Successfully set room boost for %s", room)
                    return True
                _LOGGER.error("Failed to set room boost %s: HTTP %s", room, resp.status)
                return False
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout setting room boost for %s", room)
            return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error setting room boost for %s: %s", room, err)
            return False
        except Exception as err:
            _LOGGER.exception("Unexpected error setting room boost for %s: %s", room, err)
            return False

    async def async_set_room_boost_default(
        self,
        enable: bool = True,
        level: float = 21.0,
        timeout: int = 900,
        remaining: int = 0,
    ) -> bool:
        """Set room boost without specifying a room.

        Example endpoint: PUT /v1/decision/room/boost
        Body: {"enable": true, "level": 21.0, "timeout": 900, "remaining": 0}
        """
        payload = {
            "enable": enable,
            "level": float(level),
            "timeout": int(timeout),
            "remaining": int(remaining),
        }

        if self.session is None:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}/v1/decision/room/boost"

        try:
            async with self.session.put(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status in (200, 204):
                    _LOGGER.debug("Successfully set default room boost")
                    return True
                _LOGGER.error("Failed to set default room boost: HTTP %s", resp.status)
                return False
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout setting default room boost")
            return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error setting default room boost: %s", err)
            return False
        except Exception as err:
            _LOGGER.exception("Unexpected error setting default room boost: %s", err)
            return False

    async def async_set_decision_silent(self, payload: dict[str, typing.Any]) -> bool:
        """Set silent mode configuration via PUT /v1/decision/silent."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}/v1/decision/silent"

        try:
            async with self.session.put(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status in (200, 204):
                    _LOGGER.debug("Successfully set silent mode")
                    return True
                _LOGGER.error("Failed to set silent mode: HTTP %s", resp.status)
                return False
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout setting silent mode")
            return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error setting silent mode: %s", err)
            return False
        except Exception as err:
            _LOGGER.exception("Unexpected error setting silent mode: %s", err)
            return False
