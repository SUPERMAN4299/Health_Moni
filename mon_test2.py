import json
import time
import os

# --- File path to the JSON data from ESP32 ---
filename = "sensor_data.json"

# How often to refresh (seconds)
REFRESH_INTERVAL = 2  

def read_sensor_data():
    if not os.path.exists(filename):
        print("⚠ JSON file not found yet...")
        return None

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        if not data:
            return None
        return data
    except json.JSONDecodeError:
        # Happens if ESP32 is still writing to the file
        return None

while True:
    sensor_data = read_sensor_data()

    if sensor_data:
        # Take only last entry
        last = sensor_data[-1]

        print("------ Latest Sensor Data ------")
        print(f"Temperature: {last['Temperature']} °C")
        print(f"Humidity:    {last['Humidity']} %")
        print(f"HQ07:        {last['HQ07']} V")
        print(f"GSR:         {last['GSR']} V")
        print("--------------------------------\n")

    time.sleep(REFRESH_INTERVAL)

