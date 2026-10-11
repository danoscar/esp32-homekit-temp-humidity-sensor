/*
 * ESP32 Wi-Fi Temperature & Humidity Sensor — native Apple Home via HomeSpan
 * ---------------------------------------------------------------------
 * USB-C powered, always on. Reads an SHT31/SHT40 over I2C and publishes
 * temperature + humidity to HomeKit as two sensor tiles.
 *
 * Hardware: ESP32-WROOM-32 devkit (stock), SHT31 or SHT40 on I2C.
 *
 * ---------------------------------------------------------------------
 * ARDUINO IDE SETUP
 * ---------------------------------------------------------------------
 * Board package : "esp32" by Espressif Systems (Boards Manager)
 * Board         : ESP32 Dev Module
 * Partition     : Tools > Partition Scheme > "Huge APP (3MB No OTA/1MB SPIFFS)"
 *                 (HomeSpan builds are ~1.4 MB; the default scheme only has
 *                 ~1.3 MB for the app and fails with "Sketch too big".)
 * Libraries     : HomeSpan, Adafruit SHT31 Library
 *                 (SHT40? use "Adafruit SHT4x" and swap the sht31.* calls)
 *
 * ---------------------------------------------------------------------
 * FIRST-TIME WI-FI SETUP — no SSID/password is stored in this sketch
 * ---------------------------------------------------------------------
 * Credentials are entered once and saved to flash (NVS). Two ways:
 *
 *  A) Setup hotspot (needs no cable after flashing)
 *     This sketch calls enableAutoStartAP(), so when no Wi-Fi credentials
 *     are stored the board starts a hotspot automatically:
 *       SSID "HomeSpan-Setup", password "homespan".
 *     Join it from a phone or laptop and pick your home network from the
 *     page that opens. Hold the BOOT button for ~3 s to enter HomeSpan's
 *     command mode if you ever need the hotspot again (see README).
 *
 *  B) Serial Monitor (115200 baud, line ending "Newline")
 *     Type  W  and follow the prompts: it scans, you choose a network and
 *     enter the password, it saves and restarts.
 *
 * ---------------------------------------------------------------------
 * STATUS LED (on-board LED, GPIO2)
 * ---------------------------------------------------------------------
 *   Blinking  = not connected to Wi-Fi yet (connecting, or waiting for setup)
 *   Solid on  = connected to Wi-Fi and running
 *   If Wi-Fi drops the LED goes back to blinking until it reconnects.
 *   (This is the sketch's own LED logic; HomeSpan's built-in status LED is
 *   not used, so there is no conflict on the pin.)
 *
 * ---------------------------------------------------------------------
 * PAIRING WITH APPLE HOME
 * ---------------------------------------------------------------------
 *   Home app > + > Add Accessory > choose "Temp Sensor" > enter the code
 *   Default setup code: 466-37-726  (change it with  S <8 digits>  in the
 *   Serial Monitor; only a hash is stored, so a lost code can't be read
 *   back — set a new one instead).
 *   iOS shows a warning that the accessory is not Apple-certified. That is
 *   expected for HomeSpan; accept it to continue.
 */

#include "HomeSpan.h"
#include <WiFi.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"

// ---------- Version (keep in step with /VERSION and CHANGELOG.md) ----------
#define FW_VERSION  "0.3.0"

// ---------- Pins ----------
#define PIN_SDA      21
#define PIN_SCL      22
#define PIN_CONTROL   0   // BOOT button — HomeSpan control button
#define PIN_LED       2   // on-board LED (labelled D2), active high

// ---------- Timing ----------
#define LED_BLINK_MS  300                           // blink half-period while waiting for Wi-Fi
#define READ_INTERVAL_MS  (15UL * 60UL * 1000UL)   // read + publish every 15 min
                                                     // (e.g. 60000 = every minute)

Adafruit_SHT31 sht31 = Adafruit_SHT31();
unsigned long lastRead = 0;

// =====================================================================
struct EnvSensor : Service::TemperatureSensor {
  SpanCharacteristic *temp;
  EnvSensor() : Service::TemperatureSensor() {
    temp = new Characteristic::CurrentTemperature(0, true);
    temp->setRange(-40, 85);
  }
  void publish(float t) { temp->setVal(t); }
};

struct HumiditySensorSvc : Service::HumiditySensor {
  SpanCharacteristic *hum;
  HumiditySensorSvc() : Service::HumiditySensor() {
    hum = new Characteristic::CurrentRelativeHumidity(0, true);
  }
  void publish(float h) { hum->setVal(h); }
};

EnvSensor         *envSensor;
HumiditySensorSvc *humSensor;

// =====================================================================
bool readSensor(float &tempC, float &humidity) {
  tempC    = sht31.readTemperature();
  humidity = sht31.readHumidity();
  return !isnan(tempC) && !isnan(humidity);
}

// =====================================================================
// Blink while Wi-Fi is down, solid on while it is up. Non-blocking.
void updateStatusLed() {
  static unsigned long lastToggle = 0;
  static bool ledOn = false;
  if (WiFi.status() == WL_CONNECTED) {
    ledOn = true;
  } else if (millis() - lastToggle >= LED_BLINK_MS) {
    lastToggle = millis();
    ledOn = !ledOn;
  }
  digitalWrite(PIN_LED, ledOn ? HIGH : LOW);
}

// =====================================================================
void setup() {
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);
  Serial.begin(115200);   // HomeSpan's CLI and status messages use this
  Serial.printf("\nHomeKit Temp/Humidity Sensor firmware v%s\n", FW_VERSION);

  Wire.begin(PIN_SDA, PIN_SCL);
  if (!sht31.begin(0x44)) {
    Serial.println("SHT31/40 not found at 0x44 — check wiring and I2C address");
  }

  homeSpan.setControlPin(PIN_CONTROL);   // without this HomeSpan ignores the button
  homeSpan.enableAutoStartAP();          // start the setup hotspot if no Wi-Fi is stored
  homeSpan.setSketchVersion(FW_VERSION);  // shown in HomeSpan's status output
  homeSpan.begin(Category::Sensors, "Temp Sensor");

  new SpanAccessory();
    new Service::AccessoryInformation();
      new Characteristic::Identify();
    envSensor = new EnvSensor();
    humSensor = new HumiditySensorSvc();

  // Publish one reading at boot so the Home app has data straight away.
  float t, h;
  if (readSensor(t, h)) {
    envSensor->publish(t);
    humSensor->publish(h);
  }
  lastRead = millis();
}

// =====================================================================
void loop() {
  homeSpan.poll();   // must run continuously to keep the HomeKit connection live
  updateStatusLed();

  if (millis() - lastRead >= READ_INTERVAL_MS) {
    lastRead = millis();
    float t, h;
    if (readSensor(t, h)) {
      envSensor->publish(t);
      humSensor->publish(h);
    }
    // A failed read is simply retried on the next interval.
  }
}
