import cv2
import socket
import struct
import time
import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
gas_proc = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "gas_sensor.py")])

LAPTOP_IP = os.getenv("LAPTOP_IP", "192.168.1.100")
PORT = int(os.getenv("PORT", 5000))
QUALITY = int(os.getenv("QUALITY", 80))
FPS = int(os.getenv("FPS", 15))

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, FPS)

interval = 1.0 / FPS

try:
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((LAPTOP_IP, PORT))
            print(f"Connected to laptop {LAPTOP_IP}:{PORT}")

            frame_count = 0
            while True:
                start = time.time()
                ret, frame = cap.read()
                if not ret:
                    print("Frame error")
                    continue

                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, QUALITY])
                data = buffer.tobytes()
                sock.sendall(struct.pack(">L", len(data)) + data)

                frame_count += 1
                if frame_count % 15 == 0:
                    print(f"Trimis {frame_count} frames")

                elapsed = time.time() - start
                sleep_time = interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"Connection lost: {e}. Retrying in 3s...")
            try:
                sock.close()
            except:
                pass
            time.sleep(3)

except KeyboardInterrupt:
    gas_proc.terminate()
    cap.release()
    try:
        sock.close()
    except:
        pass
