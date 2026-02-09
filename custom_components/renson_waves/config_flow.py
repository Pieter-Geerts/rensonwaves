"""Config flow for Renson WAVES integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import RensonWavesClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "renson_waves"


class RensonWavesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renson WAVES."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the connection
            client = RensonWavesClient(
                host=user_input[CONF_HOST],
                port=user_input.get(CONF_PORT, 80),
            )
            
            try:
                data = await client.async_get_constellation()
                await client.async_close()
                
                if not data:
                    errors["base"] = "cannot_connect"
                else:
                    # Extract device name from response
                    device_name = data.get("global", {}).get("device_name", {}).get("value", "WAVES Device")
                    serial = data.get("global", {}).get("serial", {}).get("value", "unknown")
                    
                    return self.async_create_entry(
                        title=device_name,
                        data={
                            CONF_HOST: user_input[CONF_HOST],
                            CONF_PORT: user_input.get(CONF_PORT, 80),
                            "serial": serial,
                        },
                    )
            except Exception as err:
                _LOGGER.error("Error connecting to WAVES device: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=80): int,
                }
            ),
            errors=errors,
            description_placeholders={},
        )

    async def _create_entry_from_host(self, host: str, port: int | None = 80) -> FlowResult:
        """Create a config entry by contacting the device at host:port.

        Returns a FlowResult (create entry or abort).
        """
        client = RensonWavesClient(host=host, port=port or 80)

        try:
            data = await client.async_get_constellation()
            await client.async_close()
        except Exception as err:  # noqa: BLE001 - broad catch to convert to flow abort
            _LOGGER.debug("Discovery contact failed for %s:%s: %s", host, port, err)
            return self.async_abort(reason="cannot_connect")

        if not data:
            return self.async_abort(reason="cannot_connect")

        device_name = data.get("global", {}).get("device_name", {}).get("value", "WAVES Device")
        serial = data.get("global", {}).get("serial", {}).get("value", "unknown")

        # Abort if this host is already configured
        self._async_abort_entries_match({CONF_HOST: host})

        return self.async_create_entry(
            title=device_name,
            data={
                CONF_HOST: host,
                CONF_PORT: port or 80,
                "serial": serial,
            },
        )

    async def async_step_zeroconf(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle zeroconf discovery.

        discovery_info typically contains `host`, `port` and service properties.
        """
        host = discovery_info.get("host") or discovery_info.get("hostname")
        port = discovery_info.get("port", 80)

        if not host:
            # Try addresses list
            addresses = discovery_info.get("addresses") or []
            host = addresses[0] if addresses else None

        if not host:
            _LOGGER.debug("Zeroconf discovery without host: %s", discovery_info)
            return self.async_abort(reason="no_devices_found")

        return await self._create_entry_from_host(host, port)

    async def async_step_ssdp(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle SSDP discovery.

        SSDP discovery_info may include `ssdp_location` or `host`.
        """
        host = discovery_info.get("host")
        port = discovery_info.get("port")

        if not host:
            location = discovery_info.get("ssdp_location") or discovery_info.get("location")
            if location:
                parsed = urlparse(location)
                host = parsed.hostname
                port = parsed.port or port

        if not host:
            _LOGGER.debug("SSDP discovery without host: %s", discovery_info)
            return self.async_abort(reason="no_devices_found")

        return await self._create_entry_from_host(host, port)
