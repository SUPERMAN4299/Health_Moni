// =================== MQ-7 SENSOR + ESP32 (AIR QUALITY INDEX) ===================
// Pin: GPIO 34 (Analog Input)
// Filter: MA7 (Moving Average of last 7 samples)

#define MQ7_PIN 34

// ---- Calibration Values (Tune these using real calibration data) ----
float R0 = 10.0;      // Sensor resistance in clean air (kohm)
float RL = 10.0;      // Load resistance (kohm)

// ---- Moving Average Window ----
const int MA_WINDOW = 7;
float maBuffer[MA_WINDOW];
int maIndex = 0;
bool bufferFilled = false;

// ---- Function: Moving Average ----
float movingAverage(float newValue) {
  maBuffer[maIndex] = newValue;
  maIndex = (maIndex + 1) % MA_WINDOW;

  float sum = 0;
  int count = bufferFilled ? MA_WINDOW : maIndex;

  for (int i = 0; i < count; i++) {
    sum += maBuffer[i];
  }

  if (maIndex == 0 && !bufferFilled) bufferFilled = true;
  return sum / count;
}

// ---- AQI Classification ----
String aqiStatus(int aqi) {
  if (aqi <= 50)  return "Good";
  if (aqi <= 100) return "Moderate";
  if (aqi <= 150) return "Unhealthy for Sensitive Groups";
  if (aqi <= 200) return "Unhealthy";
  if (aqi <= 300) return "Very Unhealthy";
  return "Hazardous";
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("MQ7 Air Quality Monitoring (MA7 Filter)");
}

void loop() {

  // ---- Step 1: Read RAW ADC ----
  int rawADC = analogRead(MQ7_PIN);

  // ---- Step 2: Convert ADC → voltage ----
  float voltage = (rawADC / 4095.0) * 3.3;

  // ---- Step 3: Calculate Sensor Resistance Rs ----
  float Rs = (3.3 / voltage - 1) * RL;

  // ---- Step 4: Calculate CO ppm (MQ-7 curve approximation) ----
  float ratio = Rs / R0;

  // MQ-7 characteristic approximation: ppm = 10 ^ ((log10(ratio) - b) / m)
  // (Adjust m & b from your calibration graph)
  float m = -0.77;
  float b = 1.78;

  float ppm = pow(10, (log10(ratio) - b) / m);

  // ---- Step 5: Apply MA7 filter to ppm ----
  float ppmSmooth = movingAverage(ppm);

  // ---- Step 6: Convert ppm → AQI (rough estimation) ----
  int AQI = map(ppmSmooth, 0, 50, 0, 300);
  AQI = constrain(AQI, 0, 500);

  // ---- PRINT OUTPUT ----
  Serial.print("RAW:");
  Serial.print(rawADC);

  Serial.print(" | Volt:");
  Serial.print(voltage, 2);

  Serial.print("V | PPM:");
  Serial.print(ppmSmooth, 1);

  Serial.print(" | AQI:");
  Serial.print(AQI);

  Serial.print(" | Status: ");
  Serial.println(aqiStatus(AQI));

  delay(500);
}
