# Drone Detection System

Sistem de detecție drone în timp real, dezvoltat pentru hackathon.

## Arhitectură

```
Camera → Raspberry Pi → Server Cloud (Render) → Ground Station Dashboard
```

## Componente

### Server API (Render)
- **URL**: https://drone-detection-hp41.onrender.com
- **Docs**: https://drone-detection-hp41.onrender.com/docs
- **Stack**: Python, FastAPI, Uvicorn

### Endpoints
| Method | Endpoint | Descriere |
|--------|----------|-----------|
| GET | `/` | Status server |
| POST | `/detect/drone` | Trimite imagine pentru detecție |
| GET | `/detections` | Lista ultimelor 50 detecții |
| DELETE | `/detections` | Șterge toate detecțiile |

> Toate endpoint-urile (exceptând `/`) necesită header `x-api-key`.

### Ground Station Dashboard
Deschide `dashboard/index.html` în browser. Se actualizează automat la fiecare 3 secunde.

### Script Raspberry Pi
Rulează `pi_client/capture_and_send.py` pe Raspberry Pi.

```bash
pip install opencv-python requests
python capture_and_send.py
```

## Setup

### Variabile de mediu (Render)
```
API_KEY = <cheia secreta>
```

### Adaugă modelul ML
Înlocuiește conținutul funcției `run_inference()` din `api/detector.py` cu modelul real.

```python
def run_inference(image_bytes: bytes) -> tuple[bool, float]:
    # pune modelul ML aici
    # returneaza (is_drone: bool, confidence: float)
    ...
```


