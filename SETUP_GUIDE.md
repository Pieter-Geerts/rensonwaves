# Renson WAVES Home Assistant Integration - Setup Guide

## Directory Structure

```
ha-renson-waves/
├── custom_components/
│   └── renson_waves/
│       ├── __init__.py              # Main integration setup
│       ├── manifest.json             # Integration metadata
│       ├── client.py                 # API client
│       ├── coordinator.py            # Data coordinator
│       ├── config_flow.py            # Configuration UI
│       ├── sensor.py                 # Sensor entities
│       ├── fan.py                    # Fan entities
│       ├── strings.json              # Translations
│       └── README.md                 # Integration documentation
├── .github/
│   └── workflows/                    # GitHub Actions (optional)
├── README.md                         # Repository README
├── LICENSE                           # MIT License
└── hacs.json                         # HACS metadata
```

## Setup Instructions

### 1. Prepare Your Repository

```bash
# Create the project structure
mkdir -p ha-renson-waves/custom_components/renson_waves

# Copy all files into place
# Files have been created in /home/claude/renson_waves/
```

### 2. Create Additional Files for HACS

Create `hacs.json` in the root directory:

```json
{
  "name": "Renson WAVES",
  "homeassistant": "2024.1.0",
  "documentation": "https://github.com/yourgithub/ha-renson-waves",
  "issue_tracker": "https://github.com/yourgithub/ha-renson-waves/issues",
  "requirements": ["aiohttp>=3.8.0"]
}
```

Create `LICENSE` (MIT License):

```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE OR ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 3. Create GitHub Repository

1. Create a new repository on GitHub
2. Name it: `ha-renson-waves`
3. Clone it locally
4. Copy the `custom_components` folder and other files
5. Push to GitHub

### 4. Update Manifest

Edit `manifest.json`:
- Replace `yourgithub` with your GitHub username
- Update `documentation` and `issue_tracker` URLs

### 5. Register with HACS

1. Go to https://github.com/hacs/default
2. Fork the repository (if you want automatic updates via HACS)
3. Or manually register in HACS by adding your repo URL

## Testing the Integration

### Local Testing (before publishing)

1. Copy `custom_components/renson_waves/` to your Home Assistant `custom_components/` directory
2. Restart Home Assistant
3. Go to Settings > Devices & Services
4. Click "Create Integration" and search for "Renson WAVES"

### Testing Script

Create `test_integration.py`:

```python
import asyncio
from custom_components.renson_waves.client import RensonWavesClient

async def test():
    client = RensonWavesClient("192.168.1.100")  # Replace with your device IP
    
    # Test constellation endpoint
    data = await client.async_get_constellation()
    print("Constellation:", data)
    
    # Test sensors
    sensors = await client.async_get_sensors()
    print("Sensors:", sensors)
    
    # Test actuators
    actuators = await client.async_get_actuators()
    print("Actuators:", actuators)
    
    await client.async_close()

asyncio.run(test())
```

## Next Steps

### Implement Fan Control

The fan entity currently shows read-only data. To add control:

1. **Discover control endpoints** - Use a tool like Burp Suite or Postman to test:
   - `POST /v1/constellation/actuator/0` (to set PWM)
   - `PUT /v1/constellation/actuator/0/parameter/pwm` (possible endpoint)

2. **Update the client** - Add a method to set PWM:

```python
async def async_set_pwm(self, actuator_id: int, pwm: float) -> bool:
    """Set PWM value for actuator."""
    endpoint = f"/v1/constellation/actuator/{actuator_id}"
    # Make POST/PUT request with new PWM value
```

3. **Update fan.py** - Implement `async_set_percentage()`

### Add More Features

- Energy monitoring (if available)
- Fault detection
- Preset modes (low, medium, high)
- Integration with other Renson devices

## Version History

- **1.0.0** - Initial release with sensor support and read-only fan status

## Support

For issues with this integration, please open an issue on GitHub with:
- Device model and firmware version
- Home Assistant version
- Description of the issue
- Relevant logs from Home Assistant
