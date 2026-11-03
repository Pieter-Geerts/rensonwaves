# Renson WAVES Home Assistant Integration

[![Buy me a coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/pietergeerts)

A Home Assistant integration for Renson WAVES ventilation devices.

## Features

- **Sensor Support**: Temperature, Humidity, Absolute Humidity, AVOC (VOC), Pressure, Signal Strength, and fan Power
- **Fan Control**: View fan speed and control ventilation through room boost
- **Local Polling**: Fetches data directly from the device on your local network
- **HACS Compatible**: Install directly from Home Assistant Community Store

## Installation

### Via HACS (Recommended)

1. Go to HACS > Integrations
2. Click the three dots menu and select "Custom repositories"
3. Add: `https://github.com/Pieter-Geerts/rensonwaves`
4. Select "Integration" category
5. Click "Install"
6. Restart Home Assistant
7. Go to Settings > Devices & Services > Create Integration
8. Search for "Renson WAVES"

### Manual Installation

1. Clone the repository to your `custom_components` directory:
   ```bash
   git clone https://github.com/Pieter-Geerts/rensonwaves.git \
   ~/.homeassistant/custom_components/renson_waves
   ```
2. Restart Home Assistant

## Configuration

After installation, add the integration through the UI:

1. Go to Settings > Devices & Services
2. Click "Create Integration"
3. Search for "Renson WAVES"
4. Enter the device IP address (default port: 80)
5. The integration will validate the connection and auto-discover device information

## Supported Sensors

| Sensor            | Unit | Type            |
| ----------------- | ---- | --------------- |
| Temperature       | °C   | Temperature     |
| Humidity          | %    | Humidity        |
| Absolute Humidity | g/m³ | Humidity        |
| Fan Power         | W    | Power           |
| AVOC (VOC)        | ppm  | Air Quality     |
| Pressure          | Pa   | Pressure        |
| Signal Strength   | dBm  | Signal Strength |

## Known Limitations

- **Room-based fan control**: Boost commands target a WAVES room identifier. Multiple fans reported for one room cannot be controlled independently.
- **Manual speed control**: Speed requests are translated to the device's room boost level.

## API Endpoints Used

- `GET /v1/constellation` - Complete device configuration
- `GET /v1/constellation/sensor` - Sensor data
- `GET /v1/constellation/actuator` - Actuator data
- `GET /v1/global/uptime` - Device uptime
- `GET /v1/wifi/client/status` - WiFi status
- `GET /v1/decision/room` - Decision room state
- `PUT /v1/decision/room/boost` - Default room boost control
- `GET /v1/decision/silent` - Silent mode configuration
- `PUT /v1/decision/silent` - Silent mode configuration update
- `GET /v1/decision/breeze` - Breeze mode configuration

## Services

All services are available under the `renson_waves` domain.

### `start_room_boost`

Starts a boost for a room. `room` is the numeric room identifier reported by the
WAVES API; `level` (0–200), `timeout` (seconds), and `remaining` (seconds) are
optional.

```yaml
action: renson_waves.start_room_boost
data:
  room: 0
  level: 100
  timeout: 900
```

### `stop_room_boost`

Stops the boost for a room.

```yaml
action: renson_waves.stop_room_boost
data:
  room: 0
```

### `set_room_boost_default`

Sets the device-wide fallback boost settings when a room-specific boost endpoint
is not available. It accepts `enable`, `level`, `timeout`, and `remaining`.

### `set_silent_mode`

Updates silent-mode settings. Supply either a complete `payload` object or one or
more of `enable`, `reduction`, and weekday schedule objects.

## Fan control limitation

WAVES boost control is room-based. If a device reports multiple ventilation fans
for the same room identifier, the device API cannot distinguish them through the
room boost endpoint, so they cannot be boosted independently by this integration.

## Troubleshooting

### Integration won't connect

- Ensure the WAVES device is on the same network
- Check the device IP address is correct
- Verify the device is responding to HTTP requests on port 80

### Sensors not showing values

- Check that the coordinator has refreshed data (should happen every 30 seconds)
- Look for errors in the Home Assistant logs

### Missing control endpoints

If you discover additional endpoints for fan control, please open an issue or PR!

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## Disclaimer

This project is not affiliated with or endorsed by Renson. I am not an employee of Renson. If there are any concerns, please contact me and I will address them.

## License

MIT License - See LICENSE file for details

## Support

For issues, feature requests, or questions, please open an issue on GitHub.
