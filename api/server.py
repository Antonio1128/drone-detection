from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Form
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import Optional
from supabase import create_client
import os

API_KEY = os.environ.get("API_KEY", "dronedetect-secret")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://huqbekfyoorzveogebzn.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh1cWJla2Z5b29yenZlb2dlYnpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA3NDI1NTEsImV4cCI6MjA5NjMxODU1MX0.6OjrlcpmtZZHXu-frTvXVL5ifkyXoxpq9MZpUKWx3po")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "online"}


@app.get("/detections")
def get_detections(limit: int = 50, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    data = supabase.table("detections").select("*").order("timestamp", desc=True).limit(limit).execute()
    return {"detections": data.data}

@app.post("/report/detection")
async def report_detection(
    is_drone: bool = Form(...),
    confidence: float = Form(...),
    image: Optional[UploadFile] = File(None),
    x_api_key: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    timestamp = datetime.now(timezone.utc).isoformat()
    filename = image.filename if image else "no_image"

    result = {
        "is_drone": is_drone,
        "confidence": round(confidence, 4),
        "timestamp": timestamp,
        "filename": filename,
    }
    supabase.table("detections").insert(result).execute()
    return result

@app.delete("/detections")
def clear_detections(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    supabase.table("detections").delete().neq("id", 0).execute()
    return {"status": "cleared"}
