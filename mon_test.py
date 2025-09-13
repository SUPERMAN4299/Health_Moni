import json
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# JSON file path (copied from ESP32 SPIFFS to PC)
JSON_FILE = "sensor_data.json"

# Data arrays
temps, hums, irs, reds = [], [], [], []

fig, axs = plt.subplots(2, 2, figsize=(10, 8))
plt.tight_layout()

def update(frame):
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)

        temps.append(data.get("Temperature", 0))
        hums.append(data.get("Humidity", 0))
        irs.append(data.get("Heartbeat_IR", 0))
        reds.append(data.get("Heartbeat_Red", 0))

        # Keep last 50 points
        for lst in [temps, hums, irs, reds]:
            if len(lst) > 50:
                lst.pop(0)

        # Plot
        axs[0,0].cla(); axs[0,0].plot(temps); axs[0,0].set_title("Temperature (°C)")
        axs[0,1].cla(); axs[0,1].plot(hums); axs[0,1].set_title("Humidity (%)")
        axs[1,0].cla(); axs[1,0].plot(irs); axs[1,0].set_title("Heartbeat IR")
        axs[1,1].cla(); axs[1,1].plot(reds); axs[1,1].set_title("Heartbeat Red")

    except Exception as e:
        print("Error:", e)

ani = FuncAnimation(fig, update, interval=2000)
plt.show()
