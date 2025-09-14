import socket
import matplotlib.pyplot as plt

# ESP32 AP IP + port
ESP32_IP = "192.168.4.1"
ESP32_PORT = 3333

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ESP32_IP, ESP32_PORT))
print("Connected to ESP32")

# Data buffers
temps, voltages, mq7s, irs, reds = [], [], [], [], []

plt.ion()
fig, ax = plt.subplots()

while True:
    data = client.recv(1024).decode().strip()
    if not data:
        continue
    try:
        values = data.split(",")
        if len(values) != 11:  # we expect 11 values
            continue

        temp, tp, mq7, ir, red, accX, accY, accZ, gX, gY, gZ = map(float, values)

        temps.append(temp)
        voltages.append(tp)
        mq7s.append(mq7)
        irs.append(ir)
        reds.append(red)

        # --- Example graph: Temp + MQ7 + Battery ---
        ax.clear()
        ax.plot(temps, label="DS18B20 Temp (C)")
        ax.plot(voltages, label="Battery (V)")
        ax.plot(mq7s, label="MQ-7 Gas (V)")
        ax.legend()
        plt.pause(0.1)

    except Exception as e:
        print("Parse error:", e)
        continue
