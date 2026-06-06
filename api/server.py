from fastapi import FastAPI, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from api.detector import run_inference

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
async def detect_drone(image: UploadFile = File(...)):
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
def get_detections(limit: int = 50):
    return {"detections": detections[-limit:]}

@app.delete("/detections")
def clear_detections():
    detections.clear()
    return {"status": "cleared"}
