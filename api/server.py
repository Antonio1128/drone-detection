from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Form
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import Optional
from supabase import create_client
from dotenv import load_dotenv
import os
import hmac
import hashlib

load_dotenv()

API_KEY = os.environ["API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
HMAC_SECRET = os.environ["HMAC_SECRET"]
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
    x_timestamp: str = Header(None),
    x_signature: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    mesaj = f"{x_timestamp}:true:{str(round(confidence, 4))}"
    expected = hmac.new(HMAC_SECRET.encode(), mesaj.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_signature or ""):
        raise HTTPException(status_code=403, detail="Invalid signature")

    timestamp = datetime.now(timezone.utc).isoformat()
    filename = image.filename if image else "no_image"
    image_url = None

    if image:
        try:
            image_bytes = await image.read()
            storage_path = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.jpg"
            supabase.storage.from_("alerts").upload(storage_path, image_bytes, {"content-type": "image/jpeg"})
            image_url = f"{SUPABASE_URL}/storage/v1/object/public/alerts/{storage_path}"
        except Exception:
            image_url = None

    result = {
        "is_drone": is_drone,
        "confidence": round(confidence, 4),
        "timestamp": timestamp,
        "filename": filename,
        "image_url": image_url,
    }
    supabase.table("detections").insert(result).execute()
    return result

@app.delete("/detections/{detection_id}")
def delete_detection(detection_id: int, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    supabase.table("detections").delete().eq("id", detection_id).execute()
    return {"status": "deleted"}

@app.delete("/detections")
def clear_detections(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    supabase.table("detections").delete().neq("id", 0).execute()
    return {"status": "cleared"}
