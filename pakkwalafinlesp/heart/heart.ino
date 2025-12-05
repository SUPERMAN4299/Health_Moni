#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"   // contains checkForBeat()

MAX30105 sensor;

unsigned long lastBeat = 0;
float beatsPerMinute;
float beatAvg;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  if (!sensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 NOT FOUND!");
    while (1);
  }

  sensor.setup();                  
  sensor.setPulseAmplitudeRed(0x3F);   // LED Brightness
  sensor.setPulseAmplitudeIR(0x3F);
}

void loop() {
  long irValue = sensor.getIR();

  if (irValue < 50000) {
    Serial.println("Place finger...");
    delay(300);
    return;
  }

  // Detect heartbeat peak
  if (checkForBeat(irValue) == true) {
    unsigned long now = millis();
    unsigned long delta = now - lastBeat;
    lastBeat = now;

    beatsPerMinute = 60.0 / (delta / 1000.0);

    // Valid range check
    if (beatsPerMinute > 30 && beatsPerMinute < 200) {
      beatAvg = (beatAvg * 0.8) + (beatsPerMinute * 0.2);
    }

    Serial.print("Heart Rate: ");
    Serial.print(beatAvg);
    Serial.println(" bpm");
  }

  delay(20);
}
