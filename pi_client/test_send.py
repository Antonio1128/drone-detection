import requests
import sys

SERVER_URL = "https://drone-detection-hp41.onrender.com/detect/drone"
API_KEY = "dronedetect-secret"

image_path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"

with open(image_path, "rb") as f:
    response = requests.post(
        SERVER_URL,
        files={"image": (image_path, f, "image/jpeg")},
        headers={"x-api-key": API_KEY},
        timeout=15
    )

print("Status:", response.status_code)
print("Raspuns:", response.text)

