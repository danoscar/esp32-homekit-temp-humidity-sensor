# Changelog

All notable changes to this project are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

Version numbers cover the whole project (firmware, wiring and enclosure). The firmware version is also set in `FW_VERSION` at the top of the sketch and in the `VERSION` file; keep the three in step.

## [Unreleased]

### To do before 1.0.0
- Flash the firmware to a real board and confirm it pairs with Apple Home
- Confirm readings against a reference thermometer
- Print the enclosure and confirm the devkit and sensor fit
- Add a licence

## [0.1.0] - 2026-10-11

First tagged version. Hardware and firmware are drafted but not yet verified end to end.

### Added
- HomeSpan firmware for an ESP32-WROOM-32 devkit with an SHT31 on I2C (SDA GPIO21, SCL GPIO22), publishing temperature and humidity to Apple Home as separate tiles
- Wi-Fi credentials entered at setup time and stored on the device, via the `HomeSpan-Setup` hotspot or the Serial Monitor `W` command; none are hard-coded
- BOOT button as HomeSpan's control button and the on-board LED as its status light
- Reading and publishing every 15 minutes (`READ_INTERVAL_MS`), plus one reading at boot
- Firmware version printed at boot and reported through HomeSpan (`FW_VERSION`)
- Wiring diagram (PNG and SVG) with pin positions checked against the HW-394 header order
- Two-part printable enclosure (OpenSCAD source and STLs) with a USB-C cutout, vent grille and four M3 screw bosses
- README with bill of materials, wiring, Arduino IDE settings, Wi-Fi setup, pairing and upload troubleshooting

### Notes
- Arduino IDE needs the **Huge APP (3MB No OTA/1MB SPIFFS)** partition scheme; the default scheme is too small for HomeSpan
- Not yet compiled in this exact form: compile it once and record the result here



