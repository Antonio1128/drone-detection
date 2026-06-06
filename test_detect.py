import requests
import io

fake_image = io.BytesIO(b"fake image data")
r = requests.post("http://127.0.0.1:8000/detect/drone", files={"image": fake_image})
print(r.json())
