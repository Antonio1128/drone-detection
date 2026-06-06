from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from api.detector import run_inference
import os

API_KEY = os.environ.get("API_KEY", "dronedetect-secret")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

detections: list[dict] = []

@app.get("/")
def root():
    return {"hellotest, status": "online"}

@app.post("/detect/drone")
async def detect_drone(image: UploadFile = File(...), x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    contents = await image.read()
    if not contents:
        return {"error": "Empty file received"}

    is_drone, confidence = run_inference(contents)
    timestamp = datetime.now(timezone.utc).isoformat()

    result = {
        "is_drone": is_drone,
        "confidence": confidence,
        "timestamp": timestamp,
        "filename": image.filename,
    }
    detections.append(result)

    return result

@app.get("/detections")
def get_detections(limit: int = 50, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"detections": detections[-limit:]}

@app.delete("/detections")
def clear_detections(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    detections.clear()
    return {"status": "cleared"}
