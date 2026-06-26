import cv2
import socket
import struct
import numpy as np

PORT = 5000

def recv_exactly(conn, n):
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", PORT))
server.listen(1)
print(f"Waiting for Pi on port {PORT}...")

conn, addr = server.accept()
print(f"Pi connected from {addr}")

frame_count = 0
while True:
    header = recv_exactly(conn, 4)
    if header is None:
        print("Conexiune inchisa.")
        break

    frame_size = struct.unpack(">L", header)[0]
    frame_data = recv_exactly(conn, frame_size)
    if frame_data is None:
        print("Frame incomplet.")
        break

    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        print("Frame None - eroare decodare")
        continue

    frame_count += 1
    if frame_count % 15 == 0:
        print(f"Frame {frame_count} primit: {frame.shape}")

    cv2.imshow("Pi Camera Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

conn.close()
server.close()
cv2.destroyAllWindows()
