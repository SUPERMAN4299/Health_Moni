#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

MAX30105 sensor;

// ---------------- MAX30102 BUFFERS ----------------
#define BUF_SIZE 100
uint32_t ir_buf[BUF_SIZE];
uint32_t red_buf[BUF_SIZE];

int32_t spo2_dummy; 
int8_t validSpo2_dummy;
int32_t hr_dummy;
int8_t validHr_dummy;

float hrFiltered = 0;
float spo2Filtered = 0;

// ---------------- MQ7 SETTINGS ----------------
#define MQ7_PIN 34
float R0 = 10.0;
const float VREF = 3.3;
float A_const = 99.042;
float B_const = -1.518;

float ppmFiltered = 0;
float aqiFiltered = 0;

// ---------------- GSR SETTINGS ----------------
#define GSR_PIN 35
float gsrVoltage = 0;
float gsrFiltered = 0;

#define FIR_TAP_NUM 33

float firCoeffs[FIR_TAP_NUM] = {
    -0.0012, -0.0025, -0.0048, -0.0067, -0.0062, -0.0006,
     0.0110,  0.0279,  0.0468,  0.0626,  0.0703,  0.0666,
     0.0502,  0.0237, -0.0080, -0.0401, -0.0665, -0.0821,
    -0.0832, -0.0676, -0.0357,  0.0032,  0.0400,  0.0659,
     0.0754,  0.0679,  0.0468,  0.0187, -0.0098, -0.0321,
    -0.0445, -0.0460, -0.0381
};

float firBuffer[FIR_TAP_NUM] = {0};
int firIndex = 0;

float applyFIR(float sample) {
    firBuffer[firIndex] = sample;
    float result = 0;
    int idx = firIndex;
    for (int i = 0; i < FIR_TAP_NUM; i++) {
        result += firCoeffs[i] * firBuffer[idx];
        idx--;
        if (idx < 0) idx = FIR_TAP_NUM - 1;
    }
    firIndex++;
    if (firIndex >= FIR_TAP_NUM) firIndex = 0;

    return result;
}

float dcIR = 0, dcRED = 0;
float acIR = 0, acRED = 0;

const float SPO2_A = 110.0;
const float SPO2_B = 25.0;

void computeACDC(float ir, float red) {
    dcIR  = 0.995 * dcIR  + 0.005 * ir;
    dcRED = 0.995 * dcRED + 0.005 * red;

    acIR  = ir  - dcIR;
    acRED = red - dcRED;
}

float computeSpO2Medical(float ac_ir, float dc_ir, float ac_red, float dc_red) {
    if (dc_ir < 2000 || dc_red < 2000) return -1;

    float R = (ac_red / dc_red) / (ac_ir / dc_ir);
    float spo2 = SPO2_A - SPO2_B * R;

    if (spo2 > 100) spo2 = 100;
    if (spo2 < 70) spo2 = 70;

    return spo2;
}

uint8_t ledPower = 0x1F;

bool fingerDetected(uint32_t ir) {
    return ir > 20000;
}

void autoLEDCalibration(uint32_t ir) {
    if (ir < 30000) ledPower += 2;
    else if (ir > 80000) ledPower -= 2;

    if (ledPower < 0x0A) ledPower = 0x0A;
    if (ledPower > 0x7F) ledPower = 0x7F;

    sensor.setPulseAmplitudeRed(ledPower);
    sensor.setPulseAmplitudeIR(ledPower);
}

float computeRs(float voltage, float RL = 10.0) {
    if (voltage <= 0.0001) return 999999;
    return (VREF - voltage) * RL / voltage;
}

float calculateAQI(float ppm) {
    if (ppm < 0) ppm = 0;
    if (ppm > 40) ppm = 40;

    if (ppm <= 4.4) return (ppm / 4.4) * 50;
    if (ppm <= 9.4) return 50 + ((ppm - 4.4) / 5.0) * 50;
    if (ppm <= 12.4) return 100 + ((ppm - 9.4) / 3.0) * 50;
    if (ppm <= 15.4) return 150 + ((ppm - 12.4) / 3.0) * 50;
    if (ppm <= 30.4) return 200 + ((ppm - 15.4) / 15.0) * 100;
    return 300 + ((ppm - 30.4) / 10.0) * 200;
}


void setup() {
    Serial.begin(115200);
    Wire.begin(21, 22);

    if (!sensor.begin(Wire, I2C_SPEED_FAST)) {
        Serial.println("MAX30102 not found!");
        while (1);
    }

    sensor.setup();
    sensor.setPulseAmplitudeRed(0x1F);
    sensor.setPulseAmplitudeIR(0x1F);

    Serial.println("System Ready.");
}


void loop() {

    // ---------------- MAX30102 READ ----------------
    uint32_t irRaw = sensor.getIR();
    uint32_t redRaw = sensor.getRed();

    if (!fingerDetected(irRaw)) {
        Serial.println("NO FINGER DETECTED");
        delay(100);
        return;
    }

    autoLEDCalibration(irRaw);

    float irFiltered  = applyFIR((float)irRaw);
    float redFiltered = applyFIR((float)redRaw);

    computeACDC(irFiltered, redFiltered);

    float spo2_medical = computeSpO2Medical(acIR, dcIR, acRED, dcRED);

    // ---------------- MQ7 READ ----------------
    int rawADC = analogRead(MQ7_PIN);
    float voltage = (rawADC / 4095.0) * VREF;

    float Rs = computeRs(voltage);
    float ppm = A_const * pow((Rs / R0), B_const);

    ppmFiltered = 0.05 * ppm + 0.95 * ppmFiltered;

    // AUTO CALIBRATION (only in clean air)
    static float Rs_avg = Rs;
    Rs_avg = 0.05 * Rs + 0.95 * Rs_avg;

    if (ppmFiltered < 3.0) {
        R0 = 0.999 * R0 + 0.001 * Rs_avg;
    }

    float AQI = calculateAQI(ppmFiltered);

    // ---------------- GSR ----------------
    int gsrRaw = analogRead(GSR_PIN);
    gsrVoltage = (gsrRaw / 4095.0) * 3.3;
    gsrFiltered = 0.15 * gsrVoltage + 0.85 * gsrFiltered;

    // ---------------- PRINT ----------------
    Serial.println("===== SENSOR DATA =====");
    Serial.print("SpO2 Medical: "); Serial.println(spo2_medical);
    Serial.print("IR Raw: "); Serial.println(irRaw);
    Serial.print("IR Filtered: "); Serial.println(irFiltered);

    Serial.print("CO (ppm filtered): "); Serial.println(ppmFiltered);
    Serial.print("AQI: "); Serial.println(AQI);
    Serial.print("R0 Auto: "); Serial.println(R0);

    Serial.print("GSR Voltage: "); Serial.println(gsrVoltage);
    Serial.print("GSR Filtered: "); Serial.println(gsrFiltered);

    Serial.println("========================\n");

    delay(120);
}
