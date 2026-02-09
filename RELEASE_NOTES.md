# v1.0.0 - Initial release

Initial import of the Renson WAVES Home Assistant integration.

Changes:


Features added in this release:
- Add `async_set_room_boost` client method and coordinator wrapper.
- Register HA services: `renson_waves.start_room_boost` and `renson_waves.stop_room_boost`.


Notes:

- Fan control endpoints are not implemented — read-only for now.
- Consider adding `hacs.json` to repository root for HACS metadata.
