# server.py
import socket
import json

server = socket.socket()
server.bind(("127.0.0.1", 8050))
server.listen(1)

print("Server waiting on 127.0.0.1:8050...")

client, addr = server.accept()
print("Connected:", addr)

KEY = "HEART_DATA"   # <<< change this to any value you want

while True:
    data = client.recv(1024).decode().strip()
    if data:
        try:
            json_data = json.loads(data)
            value = json_data.get(KEY)

            if value is not None:
                print(value)   # ONLY print value

        except:
            pass
