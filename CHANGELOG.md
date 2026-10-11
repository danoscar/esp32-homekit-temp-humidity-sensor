# Changelog

All notable changes to this project are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

Version numbers cover the whole project (firmware, wiring and enclosure). The firmware version is also set in `FW_VERSION` at the top of the sketch and in the `VERSION` file; keep the three in step.

## [Unreleased]

### Added
- MIT licence (`LICENSE`) and a Licence section in the README
- Prototype photos in `docs/images/` (metadata stripped) and a Prototype section in the README

### Verified
- v0.3.0 firmware flashed to hardware; the status LED blinks while waiting for Wi-Fi and stays solid once connected

### To do before 1.0.0
- Confirm it pairs with Apple Home
- Confirm readings against a reference thermometer
- Print the modified lid and confirm the sensor board clicks in and the devkit fits the base

## [0.3.0] - 2026-10-11

### Added
- Housing based on the MakerWorld "ESP Smart Home Case | Parametric | Antenna" by i-BoxIt, with a sensor mount added to the lid: snap-in hooks and locating pegs for an SHT3x-DIS breakout, and a vent opening under the sensor chip. Provided as a script (`hardware/enclosure/add_sht3x_mount.py`) that builds the modified lid from the case file you download, because the MakerWorld licence does not allow redistributing the case files
- `docs/arduino-ide-setup.md`: step-by-step Arduino IDE setup listing the board package and libraries, board settings and troubleshooting
- Housing README with attribution, assumptions and printing notes

### Changed
- README: bill of materials and wiring notes updated for the SHT3x-DIS breakout (right-angle header, pin order SCL, SDA, GND, VCC); housing section rewritten; Arduino section now links to the setup guide
- `.gitignore` blocks `hardware/enclosure/*.stl` so case files can't be committed by accident

### Removed
- The generic screw-together enclosure (`sensor_case.scad`, `case_base.stl`, `case_lid.stl`), replaced by the MakerWorld-based housing. It remains available in the history at tag `v0.1.0`

## [0.2.0] - 2026-10-11

### Changed
- On-board LED (GPIO2) now blinks while the device is waiting for Wi-Fi and stays on once connected; it goes back to blinking if Wi-Fi drops. This replaces HomeSpan's built-in status LED patterns, which are no longer enabled (`setStatusPin` removed)

## [0.1.0] - 2026-10-11

First tagged version. Hardware and firmware are drafted but not yet verified end to end.

### Added
- HomeSpan firmware for an ESP32-WROOM-32 devkit with an SHT31 on I2C (SDA GPIO21, SCL GPIO22), publishing temperature and humidity to Apple Home as separate tiles
- Wi-Fi credentials entered at setup time and stored on the device, via the `HomeSpan-Setup` hotspot or the Serial Monitor `W` command; none are hard-coded
- BOOT button as HomeSpan's control button
- Reading and publishing every 15 minutes (`READ_INTERVAL_MS`), plus one reading at boot
- Firmware version printed at boot and reported through HomeSpan (`FW_VERSION`)
- Wiring diagram (PNG and SVG) with pin positions checked against the HW-394 header order
- Two-part printable enclosure (OpenSCAD source and STLs) with a USB-C cutout, vent grille and four M3 screw bosses
- README with bill of materials, wiring, Arduino IDE settings, Wi-Fi setup, pairing and upload troubleshooting

### Notes
- Arduino IDE needs the **Huge APP (3MB No OTA/1MB SPIFFS)** partition scheme; the default scheme is too small for HomeSpan
- Not yet compiled in this exact form: compile it once and record the result here



