#ifndef PULSE_H
#define PULSE_H

#include <Arduino.h>

// DC Removal (Exponential Moving Average)
class DCFilter {
public:
    float w = 0.95f;
    float prev = 0;

    float process(float x) {
        float filtered = x + w * prev;
        prev = filtered;
        return filtered;
    }
};

// Moving Average Filter
class MAFilter {
public:
    static const int N = 10;
    int idx = 0;
    int count = 0;
    int16_t buf[N];
    long sum = 0;

    int16_t filter(int16_t v) {
        sum -= buf[idx];
        buf[idx] = v;
        sum += v;
        idx = (idx + 1) % N;
        if (count < N) count++;
        return sum / count;
    }
};

// Beat Detection + AC/DC estimation
class Pulse {
public:
    DCFilter dc;
    MAFilter ma;

    int16_t prev = 0;
    bool beatDetected = false;

    long lastBeatTime = 0;
    long beatInterval = 0;

    long acSum = 0;
    long dcSum = 0;
    int acCount = 0;
    int dcCount = 0;

    // Remove DC component
    int16_t dc_filter(int32_t x) {
        float f = dc.process((float)x);
        return (int16_t)(x - f);
    }

    // Moving average smoothing
    int16_t ma_filter(int16_t x) {
        return ma.filter(x);
    }

    // Very simple beat detection using rising edge
    bool isBeat(int16_t sample) {
        bool beat = false;

        if (sample > prev && sample > 30) {
            if (!beatDetected && millis() - lastBeatTime > 300) {
                beat = true;
                beatDetected = true;
                lastBeatTime = millis();
            }
        }

        if (sample < prev) {
            beatDetected = false;
        }

        prev = sample;
        return beat;
    }

    // Average AC amplitude
    int avgAC() {
        if (acCount == 0) return 1;
        int v = acSum / acCount;
        acSum = 0;
        acCount = 0;
        return v;
    }

    // Average DC value
    int avgDC() {
        if (dcCount == 0) return 1;
        int v = dcSum / dcCount;
        dcSum = 0;
        dcCount = 0;
        return v;
    }

    // Update AC/DC buffers
    void updateACDC(int16_t ac, int32_t dc) {
        acSum += (ac < 0 ? -ac : ac);
        acCount++;

        dcSum += dc;
        dcCount++;
    }
};

#endif
