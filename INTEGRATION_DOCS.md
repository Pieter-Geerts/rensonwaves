# Renson WAVES Home Assistant Integration - Complete Documentation

## Project Overview

This is a professional, production-ready Home Assistant integration for Renson WAVES ventilation devices. The integration provides local polling of device data without requiring cloud connectivity.

## Architecture

### Component Hierarchy

```
Integration (__init__.py)
├── Config Flow (config_flow.py)
│   └── Device Discovery & Setup
├── Client (client.py)
│   └── HTTP API Communication
├── Coordinator (coordinator.py)
│   └── Data Update Management
├── Sensor Platform (sensor.py)
│   ├── Temperature
│   ├── Humidity (Relative)
│   ├── Humidity (Absolute)
│   ├── VOC (AVOC)
│   ├── Pressure
│   └── Signal Strength (RSSI)
└── Fan Platform (fan.py)
    └── Ventilation Fan Control
```

## File Descriptions

### Core Files

#### `__init__.py`
- Integration setup and platform registration
- Coordinator initialization
- Entry management (setup/unload)

#### `manifest.json`
- Integration metadata (name, version, requirements)
- Home Assistant version compatibility
- Domain registration

#### `client.py`
- Aiohttp-based API client
- Implements endpoints:
  - `GET /v1/constellation` - Full device data
  - `GET /v1/constellation/sensor` - Sensor readings
  - `GET /v1/constellation/actuator` - Actuator status
- Error handling and connection management
- Async/await pattern for non-blocking I/O

#### `coordinator.py`
- DataUpdateCoordinator implementation
- 30-second polling interval
- Update error handling
- Graceful shutdown

#### `config_flow.py`
- Home Assistant config UI
- Device IP entry and validation
- Serial number extraction for unique IDs
- Connection testing

#### `sensor.py`
- Sensor entities for all data types
- Proper Home Assistant device classes
- Unit of measurement handling
- Dynamic entity creation from device data

#### `fan.py`
- Fan entity for ventilation control
- Speed/percentage control (read-only for now)
- Extensible for future control endpoints
- Proper state management

### Configuration Files

#### `strings.json`
- UI text and translations
- Error messages
- Entity names

#### `hacs.json`
- HACS store metadata
- Required for community store listing

#### `LICENSE`
- MIT License (permissive open source)

#### `README.md`
- User-facing documentation
- Installation instructions
- Feature list
- Troubleshooting guide

## Key Features

### 1. Device Discovery
- Validates connection to device before configuration
- Extracts device name and serial number
- Unique ID generation prevents duplicates

### 2. Sensor Support
- **Environmental**: Temperature, Humidity, Pressure
- **Air Quality**: AVOC/VOC levels
- **Connectivity**: WiFi signal strength (RSSI)
- **System**: Memory/heap diagnostics

### 3. Fan Control
- Read-only status display (current PWM)
- Foundation for future speed control
- Extensible architecture

### 4. Reliability
- Async/await throughout (non-blocking)
- Connection pooling via aiohttp
- Automatic retry on failure
- Update interval: 30 seconds

### 5. Standards Compliance
- Home Assistant device class support
- Proper entity naming conventions
- Unit of measurement standardization
- Coordinator pattern for efficient updates

## API Endpoints Used

### Read Endpoints

```
GET /v1/constellation
├── global (device info)
├── actuator (ventilation fans)
├── sensor (environmental sensors)
└── room (room configuration)

GET /v1/constellation/sensor
└── [sensor_id] with real-time readings

GET /v1/constellation/actuator
└── [actuator_id] with current status
```

### Missing Endpoints (for future)

Control endpoints need to be discovered for:
- Fan speed adjustment
- Configuration changes
- Calibration

## Data Flow

```
Device
  ↓
Coordinator (polls every 30s)
  ↓
Client (HTTP request)
  ↓
Device API Response
  ↓
Coordinator (caches data)
  ↓
Entities (read from coordinator)
  ↓
Home Assistant
```

## Installation Methods

### Method 1: HACS (Recommended)
1. Add custom repository to HACS
2. Install from store
3. Configure via UI

### Method 2: Manual
1. Clone repository
2. Copy to `custom_components/`
3. Restart Home Assistant
4. Configure via UI

## Supported Home Assistant Versions

- **Minimum**: 2024.1.0
- **Tested**: 2024.1.x - 2025.1.x

## Dependencies

- **aiohttp** >= 3.8.0 (async HTTP client)
- Standard Home Assistant libraries

## Configuration Flow

```
User adds integration
  ↓
Enter device IP & port
  ↓
Config flow validates connection
  ↓
Extracts device info (serial, name)
  ↓
Creates config entry
  ↓
Integration initializes
  ↓
Coordinator starts polling
  ↓
Entities created from data
  ↓
Data available in Home Assistant
```

## Entity ID Examples

```
sensor.badkamer_met_toilet_temperature
sensor.badkamer_met_toilet_humidity
sensor.badkamer_met_toilet_avoc
sensor.badkamer_met_toilet_pressure
sensor.badkamer_met_toilet_absolute_humidity
sensor.badkamer_met_toilet_signal_strength
fan.badkamer_met_toilet_fan_controller
```

## Known Limitations

1. **Fan Control**: Currently read-only
   - Requires discovery of POST/PUT endpoints
   - Once found, implementation is straightforward

2. **No Cloud Integration**: Local network only
   - Intentional security design
   - Better reliability and privacy

3. **Single Device per Config Entry**: By design
   - Multiple devices = multiple integrations
   - Cleaner organization in Home Assistant

## Future Enhancements

### Short Term
- [ ] Implement fan speed control
- [ ] Add device diagnostics
- [ ] Implement entity versioning

### Medium Term
- [ ] Support for multiple Renson device types
- [ ] Energy statistics
- [ ] Automation suggestions

### Long Term
- [ ] Cloud integration option
- [ ] Mode presets (sleep, boost, etc.)
- [ ] Advanced filtering options

## Troubleshooting Guide

### Integration won't connect
1. Check device IP is correct
2. Ensure device is on local network
3. Test manually: `curl http://[IP]:80/v1/constellation`

### Sensors show "unavailable"
1. Check Home Assistant logs
2. Verify coordinator is updating (every 30s)
3. Check device is responding to HTTP requests

### Fan entity missing
1. Verify device has ventilation fan
2. Check actuator type is "ventilation fan"
3. Look for coordinator errors in logs

## Development Notes

### Adding New Sensors

1. Add sensor type to `sensor.py`
2. Extend `RensonWavesSensorBase`
3. Implement `native_value` property
4. Register in `async_setup_entry()`

### Adding Controls

1. Add methods to `client.py` for POST/PUT
2. Implement async control method
3. Update entity to call control method
4. Add corresponding error handling

### Testing

```python
# Manual API test
import aiohttp
import asyncio

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://[IP]/v1/constellation") as resp:
            print(await resp.json())

asyncio.run(test())
```

## Contributing

Guidelines for contributors:
1. Follow Home Assistant coding standards
2. Use async/await throughout
3. Add error handling
4. Test with real device
5. Document new features
6. Update README

## Support Channels

- GitHub Issues: Bug reports and features
- Home Assistant Forums: General questions
- Discord: Community help

## License

MIT License - Free for personal and commercial use

## Credits

Integration created for Renson WAVES ventilation devices.
Based on Home Assistant integration standards and best practices.
