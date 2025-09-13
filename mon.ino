#include <WiFi.h>
#include "DHT.h"
#include "MAX30105.h"
#include <ArduinoJson.h>

// --- WiFi AP Setup ---
const char* ssid     = "uPesy_AP";
const char* password = "super_strong_password";

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

  // WiFi AP
  Serial.println("\n[*] Creating AP...");
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  Serial.print("[+] AP Created with IP: ");
  Serial.println(WiFi.softAPIP());

  // DHT11
  dht11.begin();

  // MAX30102
  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("❌ MAX30102 not found!");
  } else {
    Serial.println("[+] MAX30102 detected!");
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
  doc["Heartbeat_IR"] = irValue;   //For heartbeat
  doc["Heartbeat_Red"] = redValue;   //For SpO2

  // --- Print JSON ---
  serializeJsonPretty(doc, Serial);
  Serial.println("\n-------------------------");

  delay(2000);
}
