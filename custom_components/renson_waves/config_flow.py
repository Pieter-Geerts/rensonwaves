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
