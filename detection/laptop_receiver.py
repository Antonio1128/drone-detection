import cv2
import socket
import struct
import numpy as np

PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", PORT))
server.listen(1)
print(f"Waiting for Pi on port {PORT}...")

conn, addr = server.accept()
print(f"Pi connected from {addr}")

data = b""
payload_size = struct.calcsize(">L")

while True:
    # Primeste marimea frame-ului
    while len(data) < payload_size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    packed_size = data[:payload_size]
    data = data[payload_size:]
    frame_size = struct.unpack(">L", packed_size)[0]

    # Primeste frame-ul complet
    while len(data) < frame_size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    frame_data = data[:frame_size]
    data = data[frame_size:]

    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        continue

    cv2.imshow("Pi Camera Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

conn.close()
server.close()
cv2.destroyAllWindows()
