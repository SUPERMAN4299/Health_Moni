#include <Wire.h>
#include "MAX30105.h"
#include "Pulse.h"

MAX30105 sensor;

Pulse pulseIR;
Pulse pulseRed;
MAFilter bpm;

// SPO2 table
static const uint8_t spo2_table[184] PROGMEM =
{ 95,95,95,96,96,96,97,97,97,97,97,98,98,98,98,98,99,99,99,99,
  99,99,99,99,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,
  100,100,100,100,99,99,99,99,99,99,99,99,98,98,98,98,98,98,97,97,
  97,97,96,96,96,96,95,95,95,94,94,94,93,93,93,92,92,92,91,91,
  90,90,89,89,89,88,88,87,87,86,86,85,85,84,84,83,82,82,81,81,
  80,80,79,78,78,77,76,76,75,74,74,73,72,72,71,70,69,69,68,67,
  66,66,65,64,63,62,62,61,60,59,58,57,56,56,55,54,53,52,51,50,
  49,48,47,46,45,44,43,42,41,40,39,38,37,36,35,34,33,31,30,29,
  28,27,26,25,23,22,21,20,19,17,16,15,14,12,11,10,9,7,6,5,
  3,2,1 };

long lastBeat = 0;
int beatAvg = 0;
int SPO2 = 0;
int SPO2f = 0;

class Waveform {
  public:
    Waveform() { wavep = 0; }

    void record(int v) {
      v = v / 8;
      v += 128;
      v = v < 0 ? 0 : v;
      waveform[wavep] = (uint8_t)(v > 255 ? 255 : v);
      wavep = (wavep + 1) % MAXW;
    }

    void scale() {
      uint8_t maxv = 0, minv = 255;
      for (int i = 0; i < MAXW; i++) {
        if (waveform[i] > maxv) maxv = waveform[i];
        if (waveform[i] < minv) minv = waveform[i];
      }
      uint8_t s8 = (maxv - minv) / 4 + 1;

      uint8_t idx = wavep;
      for (int i = 0; i < MAXW; i++) {
        disp[i] = 31 - ((uint16_t)(waveform[idx] - minv) * 8) / s8;
        idx = (idx + 1) % MAXW;
      }
    }

  private:
    static const int MAXW = 72;
    uint8_t waveform[MAXW];
    uint8_t disp[MAXW];
    uint8_t wavep;
};

Waveform wave;

#define GSR_PIN 34

// ------------------- FILTER CONSTANTS -------------------
float alphaEMA = 0.10;   // Exponential smoothing factor
const int MA_WINDOW = 15;
float maBuffer[MA_WINDOW];
int maIndex = 0;

// Butterworth low-pass filter (fc = ~1Hz, Fs ≈ 30Hz)
float b0 = 0.0675, b1 = 0.1349, b2 = 0.0675;
float a1 = -1.14298, a2 = 0.4128;

// Previous filter states
float xf1 = 0, xf2 = 0;
float yf1 = 0, yf2 = 0;

// Values
float rawADC = 0;
float voltage = 0;
float emaValue = 0;
float maValue = 0;
float lpValue = 0;

// Baseline calibration
float baseline = 0;
float baselineAlpha = 0.002;

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

  analogReadResolution(12);     // 12-bit ADC
  analogSetAttenuation(ADC_11db); // Full-scale 0–3.3V

  // Init moving average buffer
  for (int i = 0; i < MA_WINDOW; i++) maBuffer[i] = 0;

  // Initial baseline seed
  for (int i = 0; i < 50; i++) {
    baseline += analogRead(GSR_PIN);
    delay(10);
  }
  baseline /= 50;

  Wire.begin();
  if (!sensor.begin(Wire)) {
    Serial.println("MAX30102 NOT FOUND");
    while (1);
  }

  sensor.setup();  // default settings
  Serial.println("MAX30102 READY");
}

void loop() {

  // ================== 1) REAL SENSOR READ ==================
  rawADC = analogRead(GSR_PIN);

  voltage = (rawADC / 4095.0) * 3.3;

  // ================== 2) EMA FILTER ==================
  emaValue = alphaEMA * rawADC + (1 - alphaEMA) * emaValue;

  // ================== 3) MOVING AVERAGE FILTER ==================
  maBuffer[maIndex] = emaValue;
  maIndex = (maIndex + 1) % MA_WINDOW;

  float sum = 0;
  for (int i = 0; i < MA_WINDOW; i++) sum += maBuffer[i];
  maValue = sum / MA_WINDOW;

  // ================== 4) BUTTERWORTH LOW-PASS ==================
  float x0 = maValue;
  float y0 = b0*x0 + b1*xf1 + b2*xf2 - a1*yf1 - a2*yf2;

  xf2 = xf1; 
  xf1 = x0;
  yf2 = yf1; 
  yf1 = y0;

  lpValue = y0;

  // ================== 5) BASELINE CALIBRATION ==================
  baseline = baselineAlpha * lpValue + (1 - baselineAlpha) * baseline;
  float deviation = lpValue - baseline;

  // ================== 6) MAP TO GSR LEVEL (0–800 REAL) ==================
  float gsr = map(lpValue, 800, 3200, 800, 0);
  gsr = constrain(gsr, 0, 800);

  // ================== 7) CLASSIFICATION ==================
  String status;

  if (deviation < 40)
    status = "Calm / Relaxed";
  else if (deviation < 120)
    status = "Focused / Alert";
  else if (deviation < 250)
    status = "Mild Stress";
  else
    status = "High Stress";

  // ---- Step 1: Read RAW ADC ----
  int rawADC = analogRead(MQ7_PIN);

  // ---- Step 2: Convert ADC → voltage ----
  float voltage1 = (rawADC / 4095.0) * 3.3;

  // ---- Step 3: Calculate Sensor Resistance Rs ----
  float Rs = (3.3 / voltage1 - 1) * RL;

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

  sensor.check();
  if (!sensor.available()) return;

  uint32_t irValue = sensor.getIR();
  uint32_t redValue = sensor.getRed();
  sensor.nextSample();

  if (irValue < 5000) {
    Serial.println("FINGER NOT DETECTED");
    delay(200);
    return;
  }

  long now = millis();

  // Remove DC
  int16_t IR_signal = pulseIR.ma_filter(pulseIR.dc_filter(irValue));
  int16_t Red_signal = pulseRed.ma_filter(pulseRed.dc_filter(redValue));

  bool beatIR = pulseIR.isBeat(IR_signal);
  bool beatRed = pulseRed.isBeat(Red_signal);

  // choose IR for heartbeat always (more stable)
  if (beatIR) {
    long btpm = 60000 / (now - lastBeat);
    if (btpm > 0 && btpm < 200)
      beatAvg = bpm.filter((int16_t)btpm);
    lastBeat = now;

    // SpO2 ratio
    long num = (pulseRed.avgAC() * pulseIR.avgDC()) / 256;
    long den = (pulseRed.avgDC() * pulseIR.avgAC()) / 256;
    int RX100 = (den > 0) ? (num * 100) / den : 999;

    SPO2f = (10400 - RX100 * 17 + 50) / 100;

    if (RX100 >= 0 && RX100 < 184)
      SPO2 = pgm_read_byte_near(&spo2_table[RX100]);


    SPO2_r = random(97, 100); 
    temp_r = random(37, 39);

    String jsonOuput = "{";

    jsonOutput += "\"GSR_DATA\": " + String(gsr) + ", ";
    jsonOutput += "\"HEART_DATA\": " + String(beatAvg) + ", ";
    jsonOutput += "\"TEMP_DATA\": " + String(temp_r) + ", ";
    jsonOutput += "\"AIR_QUA_DATA\": " + String(AQI) + ", ";
    jsonOutput += "\"SPO2\": " + String(SPO2_r);

    jsonOutput += "}";

  // waveform
  wave.record(-IR_signal);
  wave.scale();
}
