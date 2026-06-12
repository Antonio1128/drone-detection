# Drone Detection System

Sistem de detectie drone in timp real cu fuziune de senzori (camera + RF), dezvoltat pentru hackathon xHack Defense.

## Arhitectura

```
[Drona proprie]
  ├── Pi Camera Module 3  ──→ YOLO v8 (detectie vizuala)
  ├── Antena SDR          ──→ Random Forest (clasificare semnal RF)
  └── Raspberry Pi 4
        ├── MOG2 Background Subtraction (confirmare miscare)
        ├── Fuziune senzori (60% camera + 40% RF)
        ├── Salveaza alerte local (SD card)
        └── Trimite alerte la cloud (cand are conexiune)
               ↓
  [Server Cloud - Render + Supabase]
               ↓
  [Ground Station Dashboard - browser]
```

## Componente

### 1. Sistem Multi-Senzorial (`detection/sistem_suprem.py`)

ML ruleaza **local pe Raspberry Pi**. Alertele confirmate sunt trimise automat la cloud.

```bash
pip install -r requirements.txt
python detection/sistem_suprem.py
```

Taste:
- `R` — porneste/opreste scanarea antenei radio (Random Forest)
- `T` — simuleaza o alerta de test si o trimite la server
- `Q` — inchide programul

### 2. Server API (`api/server.py`)

- **URL**: https://drone-detection-hp41.onrender.com
- **Docs**: https://drone-detection-hp41.onrender.com/docs
- **Stack**: FastAPI, Uvicorn, Supabase PostgreSQL

| Method | Endpoint | Descriere |
|--------|----------|-----------|
| GET | `/` | Status server |
| POST | `/report/detection` | Primeste alerta de la Pi (is_drone, confidence, frame) |
| GET | `/detections` | Lista ultimelor 50 detectii |
| DELETE | `/detections/{id}` | Sterge o detectie |
| DELETE | `/detections` | Sterge toate detectiile |

Toate endpoint-urile (exceptand `/`) necesita header `x-api-key`.

### 3. Ground Station Dashboard (`dashboard/index.html`)

Deschide `dashboard/index.html` in browser. Se actualizeaza automat la fiecare 3 secunde.

## Setup local

### 1. Cloneaza repo-ul

```bash
git clone https://github.com/Antonio1128/drone-detection
cd drone-detection
```

### 2. Instaleaza dependintele

```bash
pip install -r requirements.txt
```

### 3. Configureaza variabilele de mediu

Copiaza `.env.example` in `.env` si completeaza cu valorile tale:

```bash
cp .env.example .env
```

```
API_KEY=cheia_ta_secreta
SUPABASE_URL=https://proiectul-tau.supabase.co
SUPABASE_KEY=cheia_ta_supabase
HMAC_SECRET=secretul_tau_hmac
SERVER_URL=https://drone-detection-hp41.onrender.com/report/detection
```

### 4. Ruleaza serverul local

```bash
uvicorn api.server:app --reload
```

### 5. Ruleaza sistemul de detectie

```bash
python detection/sistem_suprem.py
```

## Deploy pe Render

Seteaza urmatoarele Environment Variables in Render dashboard:

| Variabila | Descriere |
|-----------|-----------|
| `API_KEY` | Cheia de autentificare API |
| `SUPABASE_URL` | URL-ul proiectului Supabase |
| `SUPABASE_KEY` | Cheia anon Supabase |
| `HMAC_SECRET` | Secretul pentru semnatura HMAC |

## Baza de date (Supabase)

Tabel `detections`:

| Coloana | Tip |
|---------|-----|
| id | int8 (PK) |
| is_drone | bool |
| confidence | float4 |
| timestamp | text |
| filename | text |
| image_url | text |

## Fuziune senzori

| Mod | Formula |
|-----|---------|
| Doar camera (antena inactiva) | `confidence = YOLO_conf` |
| Camera + Radio (antena activa) | `confidence = YOLO_conf × 0.6 + RF_conf × 0.4` |

## Hardware necesar pe drona

| Component | Model recomandat |
|-----------|-----------------|
| Procesor | Raspberry Pi 4 |
| Camera | Pi Camera Module 3 (12MP, autofocus) |
| Antena RF | SDR USB dongle |
