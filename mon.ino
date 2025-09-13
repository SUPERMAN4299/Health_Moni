#include <WiFi.h>
#include "DHT.h"
#include "MAX30105.h"
#include <ArduinoJson.h>
#include "FS.h"
#include "SPIFFS.h"

// --- DHT11 Setup ---
#define DHT11_PIN 4
#define DHT11_TYPE DHT11
DHT dht11(DHT11_PIN, DHT11_TYPE);

// --- Analog Sensors ---
#define HQ07_AOUT 34
#define GSR_PIN   35

// --- MAX30102 ---
MAX30105 particleSensor;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // SPIFFS Setup (file handling)
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  // DHT11
  dht11.begin();

  // MAX30102
  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("❌ MAX30102 not found!");
  } else {
    particleSensor.setup();
  }
}

void loop() {
  // --- Read Sensors ---
  float tempDHT11 = dht11.readTemperature();
  float humDHT11  = dht11.readHumidity();

  int rawHQ07 = analogRead(HQ07_AOUT);
  float voltageHQ07 = (rawHQ07 / 4095.0) * 3.3;

  int rawGSR = analogRead(GSR_PIN);
  float voltageGSR = (rawGSR / 4095.0) * 3.3;

  long irValue = particleSensor.getIR();
  long redValue = particleSensor.getRed();

  // --- Create JSON ---
  StaticJsonDocument<256> doc;
  doc["Temperature"] = isnan(tempDHT11) ? 0 : tempDHT11;
  doc["Humidity"] = isnan(humDHT11) ? 0 : humDHT11;
  doc["HQ07"] = voltageHQ07;
  doc["GSR"] = voltageGSR;
  doc["Heartbeat_IR"] = irValue;
  doc["Heartbeat_Red"] = redValue;

  // --- Write JSON to file ---
  File file = SPIFFS.open("/sensor_data.json", FILE_WRITE);
  if(file){
    serializeJson(doc, file);
    file.close();
  } else {
    Serial.println("❌ Failed to open file for writing");
  }

  delay(2000); // every 2 seconds
}
