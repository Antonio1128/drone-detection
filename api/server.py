from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Form, Request
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from typing import Optional
from supabase import create_client
from dotenv import load_dotenv
import os
import hmac
import hashlib
import re

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
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["x-api-key", "x-timestamp", "x-signature", "content-type"],
)

@app.get("/")
def root():
    return {"status": "online"}


@app.get("/detections")
def get_detections(limit: int = 50, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    data = supabase.table("detections").select("*").order("timestamp", desc=True).limit(limit).execute()
    return {"detections": data.data}

@app.get("/public/detections")
def get_detections_public(limit: int = 50):
    if limit < 1 or limit > 100:
        limit = 50
    data = supabase.table("detections").select("*").order("timestamp", desc=True).limit(limit).execute()
    return {"detections": data.data}

@app.post("/report/detection")
async def report_detection(
    is_drone: bool = Form(...),
    confidence: float = Form(...),
    detected_class: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    x_api_key: str = Header(None),
    x_timestamp: str = Header(None),
    x_signature: str = Header(None),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if confidence < 0 or confidence > 1:
        raise HTTPException(status_code=400, detail="confidence must be between 0 and 1")

    # Validare timestamp — max 5 minute vechime (replay attack prevention)
    try:
        request_time = datetime.fromisoformat(x_timestamp)
        if request_time.tzinfo is None:
            request_time = request_time.replace(tzinfo=timezone.utc)
        if abs((datetime.now(timezone.utc) - request_time).total_seconds()) > 300:
            raise HTTPException(status_code=403, detail="Request expired")
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid timestamp")

    mesaj = f"{x_timestamp}:true:{str(round(confidence, 4))}"
    expected = hmac.new(HMAC_SECRET.encode(), mesaj.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_signature or ""):
        raise HTTPException(status_code=403, detail="Invalid signature")

    timestamp = datetime.now(timezone.utc).isoformat()
    image_url = None

    # Sanitizare filename
    raw_filename = image.filename if image else "no_image"
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]", "_", os.path.basename(raw_filename))

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
        "detected_class": detected_class or "drone",
        "timestamp": timestamp,
        "filename": safe_filename,
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
