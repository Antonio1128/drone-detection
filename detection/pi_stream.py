import cv2
import socket
import struct
import time
import os
from dotenv import load_dotenv

load_dotenv()

LAPTOP_IP = os.getenv("LAPTOP_IP", "192.168.1.100")
PORT = int(os.getenv("PORT", 5000))
QUALITY = int(os.getenv("QUALITY", 80))
FPS = int(os.getenv("FPS", 15))

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, FPS)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((LAPTOP_IP, PORT))
print(f"Connected to laptop {LAPTOP_IP}:{PORT}")
print("Streaming... Press Ctrl+C to stop.")

interval = 1.0 / FPS

while True:
    start = time.time()
    ret, frame = cap.read()
    if not ret:
        continue

    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, QUALITY])
    data = buffer.tobytes()
    size = len(data)

    # Trimite marimea frame-ului apoi frame-ul
    sock.sendall(struct.pack(">L", size) + data)

    elapsed = time.time() - start
    sleep_time = interval - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)

cap.release()
sock.close()
