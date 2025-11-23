# sendingtest.py
import socket
import json
import time
import random

s = socket.socket()
s.connect(("127.0.0.1", 8050))

while True:
    # Example sensor values
    data = {
        "TEMP_DATA": round(random.uniform(25, 35), 2),
        "HEART_DATA": random.randint(70, 110),
        "SPO2": round(random.uniform(95, 99), 1)
    }

    json_string = json.dumps(data)
    s.send((json_string + "\n").encode())

    time.sleep(1)
