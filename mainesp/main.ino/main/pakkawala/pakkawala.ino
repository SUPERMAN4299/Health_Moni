#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"
#include <MQUnifiedsensor.h>

// === Sensor setup ===
MAX30105 particleSensor;

// === Pin Definitions ===
#define GSR_PIN 34
#define MQ7_PIN 35

// === MQ7 setup ===
#define placa "ESP-32"
#define Voltage_Resolution 3.3
#define type "MQ-7"
#define ADC_Bit_Resolution 12
#define RatioMQ7CleanAir 27.5

MQUnifiedsensor MQ7(placa, Voltage_Resolution, ADC_Bit_Resolution, MQ7_PIN, type);

// === MAX30102 buffers ===
#define BUFFER_SIZE 100
uint32_t irBuffer[BUFFER_SIZE];
uint32_t redBuffer[BUFFER_SIZE];
int32_t spo2;
int8_t validSPO2;
int32_t heartRate;
int8_t validHeartRate;

// === GSR variables ===
int gsrValue = 0;
float voltageGsr = 0;
float conductance = 0;

// === Temperature variable ===
float temperatureC = 0.0;

// === Voltage variables ===
float voltageRed = 0.0;
float voltageIR = 0.0;
float voltageMQ7 = 0.0;

// === Dynamic Finger Detection ===
uint32_t prevIR = 0;
uint8_t fingerDetected = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Initializing sensors...");

  // --- MAX30102 Initialization ---
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("❌ MAX30102 not found. Check wiring!");
    while (1);
  }

  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x2F);
  particleSensor.setPulseAmplitudeIR(0x2F);
  particleSensor.setPulseAmplitudeGreen(0x00);
  Serial.println("✅ MAX30102 ready. Place your finger on the sensor.");

  // --- MQ7 Initialization ---
  MQ7.setRegressionMethod(1);
  MQ7.setA(99.042);
  MQ7.setB(-1.518);
  MQ7.init();

  Serial.println("✅ MQ7 ready.");
  Serial.println("✅ GSR ready.");
  Serial.println("All sensors initialized successfully!\n");
}

void loop() {
  // === Collect MAX30102 data ===
  for (int i = 0; i < BUFFER_SIZE; i++) {
    while (!particleSensor.check()) {}
    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
  }

  uint32_t currentIR = irBuffer[BUFFER_SIZE - 1];

  // === Dynamic Finger Detection Logic ===
  if (currentIR > prevIR + 2000 && currentIR > 8000) {
    fingerDetected = 1;
  } else if (currentIR < 5000) {
    fingerDetected = 0;
  }
  prevIR = currentIR;

  // === Calculate Heart Rate and SpO2 only if finger detected ===
  if (fingerDetected) {
    maxim_heart_rate_and_oxygen_saturation(
      irBuffer, BUFFER_SIZE, redBuffer,
      &spo2, &validSPO2, &heartRate, &validHeartRate
    );
  } else {
    spo2 = 0;
    heartRate = 0;
  }

  // === Read Internal Temperature ===
  temperatureC = particleSensor.readTemperature();

  // === GSR Reading ===
  gsrValue = analogRead(GSR_PIN);
  voltageGsr = (gsrValue / 4095.0) * 3.3;
  conductance = (voltageGsr / 3.3) * 100.0;

  // === MQ7 Reading ===
  MQ7.update();
  float co_ppm = MQ7.readSensor();
  voltageMQ7 = (analogRead(MQ7_PIN) / 4095.0) * 3.3;

  // === Convert MAX30102 values to approximate voltages ===
  voltageRed = (redBuffer[BUFFER_SIZE - 1] / 100000.0) * 3.3;
  voltageIR = (irBuffer[BUFFER_SIZE - 1] / 100000.0) * 3.3;

  // === Create JSON-formatted output ===
  String jsonOutput = "{";
  jsonOutput += "\"GSR_DATA\": " + String(gsrValue) + ", ";
  jsonOutput += "\"AIR_QUA_DATA\": " + String(co_ppm, 2) + ", ";
  jsonOutput += "\"TEMP_DATA\": " + String(temperatureC, 2) + ", ";
  jsonOutput += "\"HEART_DATA\": " + String(heartRate) + ", ";
  jsonOutput += "\"SPO2\": " + String(spo2);
  jsonOutput += "}";

  // === Serial Output ===
  Serial.println("=== Sensor Readings ===");
  Serial.println(jsonOutput);

  if (fingerDetected)
    Serial.println("✅ Finger detected!");
  else
    Serial.println("⚠️ No finger detected!");

  Serial.println("=========================\n");

  delay(2000);
}
