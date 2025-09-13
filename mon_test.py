import json
import matplotlib.pyplot as plt

# --- File path to the JSON data from ESP32 ---
filename = "sensor_data.json"

# --- Load JSON data ---
with open(filename, 'r') as f:
    data = json.load(f)

# --- Extract sensor values ---
temperature = [entry["Temperature"] for entry in data]
humidity    = [entry["Humidity"] for entry in data]
hq07        = [entry["HQ07"] for entry in data]
gsr         = [entry["GSR"] for entry in data]

# Optional: if data is huge, take only last N points for plotting
N = 500  # last 500 readings
temperature = temperature[-N:]
humidity    = humidity[-N:]
hq07        = hq07[-N:]
gsr         = gsr[-N:]

# --- Create 4 subplots ---
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("ESP32 Sensor Data")

# Temperature
axs[0, 0].plot(temperature, color='r')
axs[0, 0].set_title("Temperature (°C)")
axs[0, 0].set_xlabel("Reading")
axs[0, 0].set_ylabel("°C")

# Humidity
axs[0, 1].plot(humidity, color='b')
axs[0, 1].set_title("Humidity (%)")
axs[0, 1].set_xlabel("Reading")
axs[0, 1].set_ylabel("%")

# HQ07 voltage
axs[1, 0].plot(hq07, color='g')
axs[1, 0].set_title("HQ07 Voltage (V)")
axs[1, 0].set_xlabel("Reading")
axs[1, 0].set_ylabel("V")

# GSR voltage
axs[1, 1].plot(gsr, color='m')
axs[1, 1].set_title("GSR Voltage (V)")
axs[1, 1].set_xlabel("Reading")
axs[1, 1].set_ylabel("V")

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
