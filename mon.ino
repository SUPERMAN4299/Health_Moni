#include <WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "Wire.h"
#include "MAX30105.h"
#include "MPU6050.h"

// --- WiFi AP ---
const char* ssid     = "ESP32_AP";
const char* password = "12345678";
WiFiServer server(3333);

// --- DS18B20 ---
#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18b20(&oneWire);

// --- TP4056 Battery Monitor (via ADC pin) ---
#define TP4056_PIN 34

// --- MQ-7 Gas Sensor ---
#define MQ7_PIN 35

// --- MAX30102 ---
MAX30105 particleSensor;

// --- MPU6050 ---
MPU6050 mpu;

void setup() {
  Serial.begin(115200);

  // Start WiFi AP
  WiFi.softAP(ssid, password);
  Serial.print("ESP32 AP IP: ");
  Serial.println(WiFi.softAPIP());
  server.begin();

  // Init DS18B20
  ds18b20.begin();

  // Init MAX30102
  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("MAX30102 not found!");
  } else {
    particleSensor.setup();
  }

  // Init MPU6050
  Wire.begin();
  if (!mpu.begin()) {
    Serial.println("MPU6050 not found!");
  } else {
    Serial.println("MPU6050 ready");
  }
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");

    while (client.connected()) {
      // --- DS18B20 ---
      ds18b20.requestTemperatures();
      float tempDS18B20 = ds18b20.getTempCByIndex(0);

      // --- TP4056 Battery Voltage ---
      int rawTP = analogRead(TP4056_PIN);
      float voltageTP = (rawTP / 4095.0) * 3.3 * 2; // adjust if voltage divider used

      // --- MQ-7 Gas Sensor ---
      int rawMQ7 = analogRead(MQ7_PIN);
      float voltageMQ7 = (rawMQ7 / 4095.0) * 3.3;

      // --- MAX30102 ---
      long irValue = particleSensor.getIR();
      long redValue = particleSensor.getRed();

      // --- MPU6050 ---
      mpu.update();
      float accX = mpu.getAccX();
      float accY = mpu.getAccY();
      float accZ = mpu.getAccZ();
      float gyroX = mpu.getGyroX();
      float gyroY = mpu.getGyroY();
      float gyroZ = mpu.getGyroZ();

      // --- Send as CSV ---
      client.print(tempDS18B20); client.print(",");
      client.print(voltageTP);   client.print(",");
      client.print(voltageMQ7);  client.print(",");
      client.print(irValue);     client.print(",");
      client.print(redValue);    client.print(",");
      client.print(accX);        client.print(",");
      client.print(accY);        client.print(",");
      client.print(accZ);        client.print(",");
      client.print(gyroX);       client.print(",");
      client.print(gyroY);       client.print(",");
      client.println(gyroZ);

      delay(2000); // every 2 sec
    }
    client.stop();
    Serial.println("Client disconnected");
  }
}
