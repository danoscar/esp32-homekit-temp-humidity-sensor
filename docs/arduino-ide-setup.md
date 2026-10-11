# Arduino IDE setup

How to install everything needed to compile the sketch and flash it to the ESP32 devkit. Written for Arduino IDE 2.x on macOS; Windows and Linux differ only in the port name and driver notes.

## 1. Install the IDE

Download **Arduino IDE 2.x** from <https://www.arduino.cc/en/software> and install it.

## 2. Install the ESP32 board package

1. Open **Tools > Board > Boards Manager** (or click the board icon in the left bar).
2. Search for `esp32`.
3. Install **esp32 by Espressif Systems**. Use the latest version; the HomeSpan documentation recommends keeping this package up to date.

If it doesn't appear in the search results, add Espressif's index first: **Arduino IDE > Settings** (**File > Preferences** on Windows and Linux), paste this into *Additional boards manager URLs*, click OK, then search again:

```
https://espressif.github.io/arduino-esp32/package_esp32_index.json
```

## 3. Install the libraries

Open **Tools > Manage Libraries** (or the library icon in the left bar) and install:

| Library to search for | Author | Why |
|---|---|---|
| **HomeSpan** | HomeSpan | Implements the HomeKit protocol so the ESP32 appears in the Home app |
| **Adafruit SHT31 Library** | Adafruit | Reads the SHT3x temperature and humidity sensor |
| **Adafruit BusIO** | Adafruit | Required by the Adafruit library. The IDE offers to install it with the SHT31 library: choose **Install all** |

`Wire` (I2C) and `WiFi` are part of the ESP32 board package, so there is nothing else to install.

If you use an SHT40 instead, install **Adafruit SHT4x Library** and change the `sht31.*` calls in the sketch to the SHT4x equivalents.

## 4. Open the sketch

**File > Open**, then choose `firmware/HomeKitTempSensor/HomeKitTempSensor.ino`. Keep it inside the folder of the same name; the IDE requires the folder to match the file name.

## 5. Choose the board settings

Connect the devkit with a USB cable that carries data, then set:

| Menu (under Tools) | Value |
|---|---|
| Board | **ESP32 Dev Module** |
| Port | The USB serial port that appears when you plug the board in (on macOS, `/dev/cu.usbserial-…`) |
| Partition Scheme | **Huge APP (3MB No OTA/1MB SPIFFS)** |
| Upload Speed | **115200** |

Leave the other menus at their defaults.

The partition scheme is required. The sketch is about 1.4 MB and the default scheme only leaves about 1.3 MB for the app, so compiling fails with `Sketch too big`.

## 6. Compile and upload

1. Click the tick (**Verify**) to compile. Fix any missing-library errors by going back to step 3.
2. Click the arrow (**Upload**). If the upload can't connect, hold **BOOT**, tap **EN** once, release BOOT, and start the upload again.
3. Open **Tools > Serial Monitor**, set it to **115200 baud** and the line ending to **Newline**. You should see the firmware version and HomeSpan's status messages.

## 7. After flashing

- The on-board LED **blinks** until the ESP32 is on Wi-Fi and stays **solid** once it is connected.
- Enter your Wi-Fi details through the `HomeSpan-Setup` hotspot (password `homespan`) or by typing `W` in the Serial Monitor, then pair in the Home app with the default code `466-37-726`. The steps are in the main [README](../README.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Sketch too big` | Set Partition Scheme to **Huge APP (3MB No OTA/1MB SPIFFS)** |
| `Unable to verify flash chip connection`, often right after `Changing baud rate to 921600` | Set Upload Speed to **115200**, confirm the menu actually shows it, then use the BOOT and EN sequence above. Try another cable plugged straight into the computer, and close any open Serial Monitor |
| No port in the Port menu | Use a data-capable cable. If the board still doesn't appear, install the driver for its USB chip (CH340 on the HW-394) and replug it |
| `HomeSpan.h: No such file or directory` | Install the **HomeSpan** library (step 3) |
| `Adafruit_SHT31.h: No such file or directory` | Install **Adafruit SHT31 Library** and **Adafruit BusIO** (step 3) |
| Serial Monitor prints `SHT31/40 not found at 0x44` | Check the SDA and SCL wiring. If the breakout's address pin is pulled high the address is `0x45`; change it in `sht31.begin(0x44)` |
| Garbage characters in the Serial Monitor | Set the baud rate to 115200 |

To test the board and cable without the IDE, install [esptool](https://github.com/espressif/esptool) and run `esptool --chip esp32 --port <your port> --baud 115200 read-mac`. If that works, the board, cable and drivers are fine and the problem is in the IDE settings.
