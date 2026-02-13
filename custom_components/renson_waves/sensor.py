"""Sensor platform for Renson WAVES integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
    UnitOfPressure,
)
from homeassistant.core import HomeAssistant
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
    """Set up sensor entities."""
    coordinator: RensonWavesCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Get sensor data from coordinator
    if coordinator.data:
        sensors = coordinator.data.get("sensor", {})
        
        for sensor_id, sensor_data in sensors.items():
            sensor_type = sensor_data.get("type")
            sensor_name = sensor_data.get("name", f"sensor_{sensor_id}")
            
            if sensor_type == "temp":
                entities.append(
                    TemperatureSensor(coordinator, entry, sensor_id, sensor_data)
                )
            elif sensor_type == "rh":
                entities.append(
                    HumiditySensor(coordinator, entry, sensor_id, sensor_data)
                )
            elif sensor_type == "ah":
                entities.append(
                    AbsoluteHumiditySensor(coordinator, entry, sensor_id, sensor_data)
                )
            elif sensor_type == "avoc":
                entities.append(
                    VOCSensor(coordinator, entry, sensor_id, sensor_data)
                )
            elif sensor_type == "press":
                entities.append(
                    PressureSensor(coordinator, entry, sensor_id, sensor_data)
                )
            elif sensor_type == "rssi":
                entities.append(
                    SignalStrengthSensor(coordinator, entry, sensor_id, sensor_data)
                )

    # Extra sensors from additional endpoints
    entities.extend(
        [
            UptimeSensor(coordinator, entry),
            WifiSsidSensor(coordinator, entry),
            WifiIpSensor(coordinator, entry),
            WifiMacSensor(coordinator, entry),
            DecisionRoomMinimumSensor(coordinator, entry),
            DecisionRoomNominalSensor(coordinator, entry),
            DecisionRoomBoostLevelSensor(coordinator, entry),
            DecisionRoomBoostRemainingSensor(coordinator, entry),
            SilentReductionSensor(coordinator, entry),
            BreezeTempThresholdSensor(coordinator, entry),
        ]
    )
    
    async_add_entities(entities)


class RensonWavesSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Renson WAVES sensors."""

    def __init__(
        self,
        coordinator: RensonWavesCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        sensor_data: dict[str, Any],
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.sensor_id = sensor_id
        self.sensor_data = sensor_data
        self._attr_unique_id = f"{entry.data['serial']}_{sensor_id}"
        self._attr_device_name = entry.title


class TemperatureSensor(RensonWavesSensorBase):
    """Temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Temperature"

    @property
    def native_value(self) -> float | None:
        """Return temperature value."""
        sensors = self.coordinator.data.get("sensor", {})
        sensor = sensors.get(self.sensor_id, {})
        params = sensor.get("parameter", {})
        temp = params.get("temperature", {}).get("value")
        return float(temp) if temp is not None else None


class HumiditySensor(RensonWavesSensorBase):
    """Relative humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Humidity"

    @property
    def native_value(self) -> float | None:
        """Return humidity value."""
        sensors = self.coordinator.data.get("sensor", {})
        sensor = sensors.get(self.sensor_id, {})
        params = sensor.get("parameter", {})
        humidity = params.get("humidity", {}).get("value")
        return float(humidity) if humidity is not None else None


class AbsoluteHumiditySensor(RensonWavesSensorBase):
    """Absolute humidity sensor."""

    _attr_native_unit_of_measurement = "g/kg"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Absolute Humidity"

    @property
    def native_value(self) -> float | None:
        """Return absolute humidity value."""
        sensors = self.coordinator.data.get("sensor", {})
        sensor = sensors.get(self.sensor_id, {})
        params = sensor.get("parameter", {})
        humidity = params.get("humidity", {}).get("value")
        return float(humidity) if humidity is not None else None


class VOCSensor(RensonWavesSensorBase):
    """Volatile Organic Compound sensor."""

    _attr_native_unit_of_measurement = "ppm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "VOC"

    @property
    def native_value(self) -> float | None:
        """Return VOC value."""
        sensors = self.coordinator.data.get("sensor", {})
        sensor = sensors.get(self.sensor_id, {})
        params = sensor.get("parameter", {})
        raw = params.get("raw", {}).get("value")
        return float(raw) if raw is not None else None


class PressureSensor(RensonWavesSensorBase):
    """Pressure sensor."""

    _attr_device_class = SensorDeviceClass.PRESSURE
    _attr_native_unit_of_measurement = UnitOfPressure.PA
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Pressure"

    @property
    def native_value(self) -> float | None:
        """Return pressure value."""
        sensors = self.coordinator.data.get("sensor", {})
        sensor = sensors.get(self.sensor_id, {})
        params = sensor.get("parameter", {})
        pressure = params.get("pressure", {}).get("value")
        return float(pressure) if pressure is not None else None


class SignalStrengthSensor(RensonWavesSensorBase):
    """RSSI / WiFi signal strength sensor."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = "dBm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Signal Strength"

    @property
    def native_value(self) -> float | None:
        """Return RSSI value."""
        sensors = self.coordinator.data.get("sensor", {})
        sensor = sensors.get(self.sensor_id, {})
        params = sensor.get("parameter", {})
        rssi = params.get("rssi", {}).get("value")
        return float(rssi) if rssi is not None else None


class RensonWavesExtraSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for extra Renson WAVES sensors."""

    def __init__(
        self,
        coordinator: RensonWavesCoordinator,
        entry: ConfigEntry,
        unique_key: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['serial']}_{unique_key}"
        self._attr_device_name = entry.title


class UptimeSensor(RensonWavesExtraSensorBase):
    """Device uptime sensor."""

    _attr_name = "Uptime"
    _attr_native_unit_of_measurement = "s"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "uptime")

    @property
    def native_value(self) -> int | None:
        uptime = self.coordinator.data.get("global_uptime", {}).get("uptime")
        return int(uptime) if uptime is not None else None


class WifiSsidSensor(RensonWavesExtraSensorBase):
    """WiFi SSID sensor."""

    _attr_name = "WiFi SSID"

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "wifi_ssid")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("wifi_status", {}).get("ssid")


class WifiIpSensor(RensonWavesExtraSensorBase):
    """WiFi IP sensor."""

    _attr_name = "WiFi IP"

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "wifi_ip")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("wifi_status", {}).get("IP")


class WifiMacSensor(RensonWavesExtraSensorBase):
    """WiFi MAC sensor."""

    _attr_name = "WiFi MAC"

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "wifi_mac")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("wifi_status", {}).get("MAC")


class DecisionRoomMinimumSensor(RensonWavesExtraSensorBase):
    """Decision room minimum sensor."""

    _attr_name = "Decision Minimum"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "decision_minimum")

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get("decision_room", {}).get("minimum")
        return float(value) if value is not None else None


class DecisionRoomNominalSensor(RensonWavesExtraSensorBase):
    """Decision room nominal sensor."""

    _attr_name = "Decision Nominal"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "decision_nominal")

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get("decision_room", {}).get("nominal")
        return float(value) if value is not None else None


class DecisionRoomBoostLevelSensor(RensonWavesExtraSensorBase):
    """Decision room boost level sensor."""

    _attr_name = "Boost Level"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "decision_boost_level")

    @property
    def native_value(self) -> float | None:
        value = (
            self.coordinator.data.get("decision_room", {})
            .get("boost", {})
            .get("level")
        )
        return float(value) if value is not None else None


class DecisionRoomBoostRemainingSensor(RensonWavesExtraSensorBase):
    """Decision room boost remaining sensor."""

    _attr_name = "Boost Remaining"
    _attr_native_unit_of_measurement = "s"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "decision_boost_remaining")

    @property
    def native_value(self) -> int | None:
        value = (
            self.coordinator.data.get("decision_room", {})
            .get("boost", {})
            .get("remaining")
        )
        return int(value) if value is not None else None


class SilentReductionSensor(RensonWavesExtraSensorBase):
    """Silent mode reduction sensor."""

    _attr_name = "Silent Reduction"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "silent_reduction")

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get("decision_silent", {}).get("reduction")
        return float(value) if value is not None else None


class BreezeTempThresholdSensor(RensonWavesExtraSensorBase):
    """Breeze temperature threshold sensor."""

    _attr_name = "Breeze Temperature Threshold"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RensonWavesCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "breeze_temp_threshold")

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get("decision_breeze", {}).get("temp_threshold")
        return float(value) if value is not None else None
