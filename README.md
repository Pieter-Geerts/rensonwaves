# Renson WAVES Home Assistant Integration

A Home Assistant integration for Renson WAVES ventilation devices.

## Features

- **Sensor Support**: Temperature, Humidity, Absolute Humidity, AVOC (VOC), Pressure, Signal Strength
- **Fan Control**: View fan speed and control ventilation (when control endpoints are available)
- **Local Polling**: Fetches data directly from the device on your local network
- **HACS Compatible**: Install directly from Home Assistant Community Store

## Installation

### Via HACS (Recommended)

1. Go to HACS > Integrations
2. Click the three dots menu and select "Custom repositories"
3. Add: `https://github.com/yourgithub/ha-renson-waves`
4. Select "Integration" category
5. Click "Install"
6. Restart Home Assistant
7. Go to Settings > Devices & Services > Create Integration
8. Search for "Renson WAVES"

### Manual Installation

1. Clone the repository to your `custom_components` directory:
   ```bash
   git clone https://github.com/yourgithub/ha-renson-waves.git \
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

| Sensor | Unit | Type |
|--------|------|------|
| Temperature | °C | Temperature |
| Humidity | % | Humidity |
| Absolute Humidity | g/kg | Humidity |
| AVOC (VOC) | ppm | Air Quality |
| Pressure | Pa | Pressure |
| Signal Strength | dBm | Signal Strength |

## Known Limitations

- **Fan Control**: Currently read-only. Full control requires discovering the POST/PUT endpoints
- **Manual Speed Control**: Not yet implemented (requires control endpoints)

## API Endpoints Used

- `GET /v1/constellation` - Complete device configuration
- `GET /v1/constellation/sensor` - Sensor data
- `GET /v1/constellation/actuator` - Actuator data

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

## License

MIT License - See LICENSE file for details

## Support

For issues, feature requests, or questions, please open an issue on GitHub.
