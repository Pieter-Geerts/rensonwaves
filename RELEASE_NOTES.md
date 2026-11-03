# v1.0.2 - Sensor and reliability improvements

- Added a fan Power sensor using `SensorDeviceClass.POWER` and watts (`W`).
- Corrected the absolute humidity unit from `g/kg` to `g/m³`.
- Retried transient WAVES connection failures and serialized requests to reduce connection resets.
- Documented boost and silent-mode services.
- Documented the device API limitation for multiple fans in the same room.

# v1.0.1 - HACS compliance fixes

Fix HACS validation issues:
- Added missing `logo.png` to brand assets folder
- Ensured proper placement of documentation field in `manifest.json`

# v1.0.0 - Initial release

Initial import of the Renson WAVES Home Assistant integration.

Changes:

Features added in this release:

- Add `async_set_room_boost` client method and coordinator wrapper.
- Register HA services: `renson_waves.start_room_boost` and `renson_waves.stop_room_boost`.

Notes:

- Fan control endpoints are not implemented — read-only for now.
- Consider adding `hacs.json` to repository root for HACS metadata.
