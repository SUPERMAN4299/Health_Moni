// ===================== MEDICAL GSR CODE (ESP32) =====================
// Real GSR Sensor | No Random | No Pattern | High Accuracy | Low Noise
// Pin: GPIO 34 | ADC: 12-bit | Voltage: 0–3.3V

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

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  for (int i = 0; i < MA_WINDOW; i++) maBuffer[i] = 0;

  // Initial baseline
  for (int i = 0; i < 50; i++) {
    baseline += analogRead(GSR_PIN);
    delay(10);
  }
  baseline /= 50;
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

  // ================== 8) PRINT OUTPUT ==================
  Serial.print("Voltage: ");
  Serial.print(voltage, 3);

  Serial.print(" V | GSR: ");
  Serial.print(gsr);

  Serial.print(" | ΔBaseline: ");
  Serial.print(deviation, 1);

  Serial.print(" | Status: ");
  Serial.println(status);

  delay(30);
}
