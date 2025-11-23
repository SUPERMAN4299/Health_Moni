import requests
import json
import time
import random

def send_data():
    url = "http://127.0.0.1:5000/sensor"
    
    data = {
        "HEART_DATA": random.randint(60, 100),
        "GSR_DATA": round(random.uniform(100, 500), 2),
        "TEMP_DATA": round(random.uniform(36.0, 37.5), 1),
        "AIR_QUA_DATA": random.randint(0, 100),
        "SPO2": random.randint(95, 100)
    }
    
    try:
        print(f"Sending data: {data}")
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Failed to send data: {e}")

if __name__ == "__main__":
    print("Starting sensor data simulation...")
    for _ in range(5):
        send_data()
        time.sleep(2)
    print("Simulation complete.")
