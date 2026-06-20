import cv2
import socket
import struct
import time
import os
from dotenv import load_dotenv
from picamera2 import Picamera2

load_dotenv()

LAPTOP_IP = os.getenv("LAPTOP_IP", "192.168.1.100")
PORT = int(os.getenv("PORT", 5000))
QUALITY = int(os.getenv("QUALITY", 80))
FPS = int(os.getenv("FPS", 15))

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}))
picam2.start()
time.sleep(2)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((LAPTOP_IP, PORT))
print(f"Connected to laptop {LAPTOP_IP}:{PORT}")
print("Streaming... Press Ctrl+C to stop.")

interval = 1.0 / FPS
frame_count = 0

while True:
    start = time.time()

    frame = picam2.capture_array("main")
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    _, buffer = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, QUALITY])
    data = buffer.tobytes()
    size = len(data)

    sock.sendall(struct.pack(">L", size) + data)

    frame_count += 1
    if frame_count % 15 == 0:
        print(f"Trimis {frame_count} frames ({size} bytes)")

    elapsed = time.time() - start
    sleep_time = interval - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)

picam2.stop()
sock.close()
