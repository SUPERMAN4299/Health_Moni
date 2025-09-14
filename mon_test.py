import json
import time
import os

# --- File path to the JSON data from ESP32 ---
filename = "sensor_data.json"

# --- Max entries (same as ESP32) ---
MAX_ENTRIES = 84600

# --- Refresh interval (seconds) ---
REFRESH_INTERVAL = 2

# --- State memory ---
last_entry = None
last_count = 0
device_connected = True


def read_sensor_data():
    """Read sensor data from JSON if available, else return None."""
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, "r") as f:
            data = json.load(f)
        if not data:
            return None
        return data
    except json.JSONDecodeError:
        # Happens if ESP32 is still writing to the file
        return None


# --- Main loop ---
while True:
    sensor_data = read_sensor_data()

    if sensor_data:
        total_entries = len(sensor_data)
        last = sensor_data[-1]

        # Detect new data (file grew)
        if total_entries > last_count:
            device_connected = True
            last_entry = last
            last_count = total_entries

            print("------ Latest Sensor Data ------")
            print(f"Temperature: {last['Temperature']} °C")
            print(f"Humidity:    {last['Humidity']} %")
            print(f"HQ07:        {last['HQ07']} V")
            print(f"GSR:         {last['GSR']} V")
            print("--------------------------------")

            if total_entries < MAX_ENTRIES:
                print(f"Appended new entry. Total entries: {total_entries}\n")
            else:
                print(f"Overwrote oldest entry. Buffer full ({MAX_ENTRIES} entries)\n")

        else:
            # No new entries since last check
            if last_entry:
                if device_connected:
                    print("Device not connected. Holding last values:\n")
                    print("------ Last Known Sensor Data ------")
                    print(f"Temperature: {last_entry['Temperature']} °C")
                    print(f"Humidity:    {last_entry['Humidity']} %")
                    print(f"HQ07:        {last_entry['HQ07']} V")
                    print(f"GSR:         {last_entry['GSR']} V")
                    print("--------------------------------\n")
                device_connected = False

    else:
        print("No sensor data file found (waiting for ESP32 to update JSON)\n")

    time.sleep(REFRESH_INTERVAL)
