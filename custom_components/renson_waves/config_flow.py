"""Config flow for Renson WAVES integration."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.service_info.ssdp import SsdpServiceInfo
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .client import RensonWavesClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "renson_waves"
CONF_FAN_ROOM = "fan_room"
FAN_ROOM_AUTO = "auto"


class RensonWavesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renson WAVES."""

    VERSION = 1

    _discovered_host: str | None = None
    _discovered_port: int = 80
    _discovered_name: str = "WAVES Device"
    _discovered_serial: str | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return RensonWavesOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = int(user_input.get(CONF_PORT, 80))
            probe = await self._async_probe_device(host, port)

            if probe is None:
                errors["base"] = "cannot_connect"
            else:
                device_name, serial = probe

                if serial is not None:
                    await self.async_set_unique_id(serial)
                    self._abort_if_unique_id_configured(
                        updates={CONF_HOST: host, CONF_PORT: port, "serial": serial}
                    )
                else:
                    self._async_abort_entries_match({CONF_HOST: host})

                return self.async_create_entry(
                    title=device_name,
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        "serial": serial or "unknown",
                    },
                )

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

    async def _async_probe_device(
        self, host: str, port: int
    ) -> tuple[str, str | None] | None:
        """Probe device and return (device_name, serial)."""
        client = RensonWavesClient(host=host, port=port)
        try:
            data = await client.async_get_constellation()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Failed to probe WAVES device at %s:%s: %s", host, port, err)
            return None
        finally:
            await client.async_close()

        if not data:
            return None

        global_data = data.get("global", {})
        if not isinstance(global_data, dict):
            global_data = {}

        name_data = global_data.get("device_name", {})
        if not isinstance(name_data, dict):
            name_data = {}

        serial_data = global_data.get("serial", {})
        if not isinstance(serial_data, dict):
            serial_data = {}

        device_name = str(name_data.get("value", "WAVES Device"))
        serial_value = serial_data.get("value")
        serial = str(serial_value).strip() if serial_value is not None else None
        if serial in (None, "", "unknown"):
            serial = None

        return device_name, serial

    async def _async_prepare_discovery(self, host: str, port: int) -> ConfigFlowResult:
        """Prepare a discovered device and move to confirmation step."""
        probe = await self._async_probe_device(host, port)
        if probe is None:
            return self.async_abort(reason="cannot_connect")

        device_name, serial = probe

        if serial is not None:
            await self.async_set_unique_id(serial)
            self._abort_if_unique_id_configured(
                updates={CONF_HOST: host, CONF_PORT: port, "serial": serial}
            )
        else:
            await self._async_handle_discovery_without_unique_id()
            self._async_abort_entries_match({CONF_HOST: host})

        self._discovered_host = host
        self._discovered_port = port
        self._discovered_name = device_name
        self._discovered_serial = serial
        self.context["title_placeholders"] = {"name": device_name}
        self._set_confirm_only()
        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup for discovered device."""
        if self._discovered_host is None:
            return self.async_abort(reason="no_devices_found")

        if user_input is not None:
            return self.async_create_entry(
                title=self._discovered_name,
                data={
                    CONF_HOST: self._discovered_host,
                    CONF_PORT: self._discovered_port,
                    "serial": self._discovered_serial or "unknown",
                },
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self._discovered_name,
                "host": self._discovered_host,
                "port": str(self._discovered_port),
            },
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        host = discovery_info.host
        port = discovery_info.port or 80
        return await self._async_prepare_discovery(host, port)

    async def async_step_ssdp(
        self, discovery_info: SsdpServiceInfo
    ) -> ConfigFlowResult:
        """Handle SSDP discovery."""
        host: str | None = None
        port = 80

        location = discovery_info.ssdp_location
        if location:
            parsed = urlparse(location)
            host = parsed.hostname
            if parsed.port is not None:
                port = parsed.port

        if host is None:
            _LOGGER.debug("SSDP discovery without host: %s", discovery_info)
            return self.async_abort(reason="no_devices_found")

        return await self._async_prepare_discovery(host, port)


class RensonWavesOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Renson WAVES integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def _async_get_room_candidates(self) -> list[str]:
        """Get candidate room identifiers from the device constellation."""
        host = self._config_entry.data.get(CONF_HOST)
        port = self._config_entry.data.get(CONF_PORT, 80)

        if not host:
            return []

        client = RensonWavesClient(host=host, port=port)
        try:
            data = await client.async_get_constellation()
            if not data:
                return []

            room_values: set[str] = set()

            def _collect_room(value: Any) -> None:
                if value is None:
                    return
                if isinstance(value, (list, tuple)):
                    if value:
                        room_values.add(str(value[0]))
                    return
                room_values.add(str(value))

            for group in ("actuator", "sensor"):
                group_data = data.get(group, {})
                if not isinstance(group_data, dict):
                    continue

                for item in group_data.values():
                    if isinstance(item, dict):
                        _collect_room(item.get("room"))

            def _sort_key(value: str) -> tuple[int, str]:
                return (0, f"{int(value):010d}") if value.isdigit() else (1, value)

            return sorted(room_values, key=_sort_key)
        except Exception as err:
            _LOGGER.debug("Failed to load room candidates for options flow: %s", err)
            return []
        finally:
            await client.async_close()

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_room = str(
            self._config_entry.options.get(
                CONF_FAN_ROOM,
                FAN_ROOM_AUTO,
            )
        )
        rooms = await self._async_get_room_candidates()
        options = [FAN_ROOM_AUTO, *rooms]

        if current_room not in options:
            options.append(current_room)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_FAN_ROOM, default=current_room
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key=CONF_FAN_ROOM,
                    )
                )
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
