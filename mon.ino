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

// --- Constants ---
const char* filename = "/sensor_data.json";
const long MAX_ENTRIES = 84600;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // SPIFFS Setup
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  // DHT11
  dht11.begin();

  // MAX30102
  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found!");
  } else {
    particleSensor.setup();
  }

  // Initialize file if doesn't exist
  if (!SPIFFS.exists(filename)) {
    File file = SPIFFS.open(filename, FILE_WRITE);
    if(file){
      file.print("[]"); // empty JSON array
      file.close();
    }
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

  // --- Load existing JSON file ---
  File file = SPIFFS.open(filename, FILE_READ);
  StaticJsonDocument<10240> doc; // increase size for many entries
  JsonArray arr;

  if(file){
    DeserializationError error = deserializeJson(doc, file);
    file.close();
    if(error){
      arr = doc.to<JsonArray>();
    } else {
      arr = doc.as<JsonArray>();
    }
  } else {
    arr = doc.to<JsonArray>();
  }

  // --- Create new entry ---
  StaticJsonDocument<256> entry;
  entry["Temperature"] = isnan(tempDHT11) ? 0 : tempDHT11;
  entry["Humidity"] = isnan(humDHT11) ? 0 : humDHT11;
  entry["HQ07"] = voltageHQ07;
  entry["GSR"] = voltageGSR;
  entry["Heartbeat_IR"] = irValue;
  entry["Heartbeat_Red"] = redValue;

  // --- Add entry with circular buffer logic ---
  if(arr.size() < MAX_ENTRIES){
    arr.add(entry);  // just append if not full
  } else {
    // overwrite oldest entry (index 0) and shift array
    for (size_t i = 0; i < arr.size() - 1; i++){
      arr[i] = arr[i + 1];
    }
    arr[MAX_ENTRIES - 1] = entry;
  }

  // --- Write updated array back to file ---
  file = SPIFFS.open(filename, FILE_WRITE);
  if(file){
    serializeJson(arr, file);
    file.close();
  } else {
    Serial.println("Failed to open file for writing");
  }

  delay(2000); // every 2 seconds
}
