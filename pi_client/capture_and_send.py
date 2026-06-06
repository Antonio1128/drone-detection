import cv2
import requests
import time

SERVER_URL = "https://drone-detection-hp41.onrender.com/detect/drone"
API_KEY = "dronedetect-secret"
INTERVAL = 0.5  # secunde intre cadre trimise

cap = cv2.VideoCapture(0)  # 0 = prima camera detectata

if not cap.isOpened():
    print("Eroare: nu s-a putut deschide camera")
    exit()

print("Camera pornita. Trimit cadre la server...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Eroare la citirea cadrului")
        continue

    _, buffer = cv2.imencode(".jpg", frame)
    image_bytes = buffer.tobytes()

    try:
        response = requests.post(
            SERVER_URL,
            files={"image": ("frame.jpg", image_bytes, "image/jpeg")},
            headers={"x-api-key": API_KEY},
            timeout=10
        )
        result = response.json()
        status = "DRONA!" if result["is_drone"] else "curat"
        print(f"[{result['timestamp']}] {status} | confidence: {result['confidence']}")
    except Exception as e:
        print(f"Eroare trimitere: {e}")

    time.sleep(INTERVAL)

cap.release()
