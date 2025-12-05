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

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin();
  if (!sensor.begin(Wire)) {
    Serial.println("MAX30102 NOT FOUND");
    while (1);
  }

  sensor.setup();  // default settings
  Serial.println("MAX30102 READY");
}

void loop() {
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

    Serial.print("HR=");
    Serial.print(beatAvg);
    Serial.print(" bpm   SpO2=");
    Serial.print(SPO2);
    Serial.println(" %");
  }

  // waveform
  wave.record(-IR_signal);
  wave.scale();
}
