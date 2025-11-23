import socket, json

server = socket.socket()
server.bind(("127.0.0.1", 5000))
server.listen(1)

client, addr = server.accept()
print("Connected:", addr)

while True:
    line = client.recv(1024).decode().strip()
    if line:
        data = json.loads(line)
        print("Captured:", data)
