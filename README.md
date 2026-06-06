# Drone Detection System

Sistem de detecție drone în timp real, dezvoltat pentru hackathon (an 1 informatică).

## Arhitectură

```
Camera + Antenă SDR
       ↓
  Raspberry Pi
  ├── YOLOv8 (detecție vizuală)
  ├── MOG2 Background Subtraction (confirmare mișcare)
  └── Random Forest RF (clasificare semnal radio)
       ↓ fuziune senzori (60% cameră + 40% RF)
  Server Cloud (Render + Supabase)
       ↓
  Ground Station Dashboard (browser)
```

## Componente

### Server API (Render)
- **URL**: https://drone-detection-hp41.onrender.com
- **Docs**: https://drone-detection-hp41.onrender.com/docs
- **Stack**: Python, FastAPI, Uvicorn, Supabase PostgreSQL

### Endpoints
| Method | Endpoint | Descriere |
|--------|----------|-----------|
| GET | `/` | Status server |
| POST | `/detect/drone` | Trimite imagine brută — serverul rulează inferența |
| POST | `/report/detection` | Trimite rezultat pre-calculat de Pi (is_drone, confidence, frame) |
| GET | `/detections` | Lista ultimelor 50 detecții |
| DELETE | `/detections` | Șterge toate detecțiile |

> Toate endpoint-urile (exceptând `/`) necesită header `x-api-key: dronedetect-secret`.

### Ground Station Dashboard
Deschide `dashboard/index.html` în browser. Se actualizează automat la fiecare 3 secunde.

### Sistem Multi-Senzorial Pi (`prj/sistem_suprem.py`)
ML rulează **local pe Pi**. Rezultatele confirmate sunt trimise automat la cloud.

```bash
pip install opencv-python ultralytics requests
python prj/sistem_suprem.py
```

Taste:
- `R` — pornește/oprește scanarea antenei radio (Random Forest)
- `T` — simulează o alertă de test și o trimite la server
- `Q` sau `X` — închide programul

### Fuziune senzori
| Mod | Formula |
|-----|---------|
| Doar cameră (antenă inactivă) | `confidence = YOLO_conf` |
| Cameră + Radio (antenă activă) | `confidence = YOLO_conf × 0.6 + RF_conf × 0.4` |

## Setup

### Variabile de mediu (Render)
```
API_KEY=dronedetect-secret
SUPABASE_URL=...
SUPABASE_KEY=...
```

### Baza de date (Supabase)
Tabel `detections`:
| Coloană | Tip |
|---------|-----|
| id | int8 (PK) |
| is_drone | bool |
| confidence | float4 |
| timestamp | text |
| filename | text |
