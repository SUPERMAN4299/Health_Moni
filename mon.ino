#include <WiFi.h>
#include "DHT.h"
#include "MAX30105.h"
#include <ArduinoJson.h>

// --- WiFi AP ---
const char* ssid     = "uPesy_AP";
const char* password = "super_strong_password";

// --- DHT11 ---
#define DHT11_PIN 4
#define DHT11_TYPE DHT11
DHT dht11(DHT11_PIN, DHT11_TYPE);

// --- Analog Sensors ---
#define HQ07_AOUT 34
#define GSR_PIN   35

// --- MAX30102 ---
MAX30105 particleSensor;

// --- Web server ---
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  Serial.print("AP IP: "); Serial.println(WiFi.softAPIP());

  server.begin();

  dht11.begin();

  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found!");
  } else {
    particleSensor.setup();
  }
}

String createJSON() {
  float temp = dht11.readTemperature();
  float hum = dht11.readHumidity();

  int rawHQ07 = analogRead(HQ07_AOUT);
  float voltageHQ07 = (rawHQ07 / 4095.0) * 3.3;

  int rawGSR = analogRead(GSR_PIN);
  float voltageGSR = (rawGSR / 4095.0) * 3.3;

  long irValue = particleSensor.getIR();
  long redValue = particleSensor.getRed();

  StaticJsonDocument<256> doc;
  doc["Temperature"] = isnan(temp) ? 0 : temp;
  doc["Humidity"] = isnan(hum) ? 0 : hum;
  doc["HQ07"] = voltageHQ07;
  doc["GSR"] = voltageGSR;
  doc["Heartbeat_IR"] = irValue;
  doc["Heartbeat_Red"] = redValue;

  String jsonStr;
  serializeJson(doc, jsonStr);
  return jsonStr;
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    String currentLine = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (c == '\n') {
          client.println("HTTP/1.1 200 OK");
          client.println("Content-type: application/json");
          client.println("Connection: close");
          client.println();
          client.println(createJSON());
          break;
        }
      }
    }
    delay(1);
    client.stop();
  }

  delay(2000); // update every 2 seconds
}
