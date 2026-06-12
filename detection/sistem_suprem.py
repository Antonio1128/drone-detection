import cv2
import numpy as np
import time
import os
import threading
import requests
from ultralytics import YOLO
from rf_classifier import RandomForestRFClassifier
import hmac
import hashlib


SERVER_URL = "https://drone-detection-hp41.onrender.com/report/detection"
API_KEY = "a3f8c2d1e4b7a9f0c3d6e8b1a4f7c2d5e8b3a6f9c2d5e8b1a4f7c2d5e8b3a6f9"
HMAC_SECRET= "ocheiesupersercreta1230"

def trimite_la_server(frame, confidence, rf_activ):
    try:
        _, buffer = cv2.imencode(".jpg", frame)
        image_bytes = buffer.tobytes()
        sensor_label = "AI+RF" if rf_activ else "AI"
        filename = f"alerta_{sensor_label}_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
        timestamp_req = time.strftime("%Y-%m-%dT%H:%M:%S")
        message = f"{timestamp_req}:true:{str(round(confidence, 4))}"
        signature = hmac.new(HMAC_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
        
        response = requests.post(
            SERVER_URL,
            data={"is_drone": "true", "confidence": str(round(confidence, 4)), "signature": signature   },
            files={"image": (filename, image_bytes, "image/jpeg")},
            headers={"x-api-key": API_KEY,"x-timestamp": timestamp_req,"x-signature": signature},
            timeout=10,
        )
        if response.status_code == 200:
            print(f"[CLOUD] Alerta trimisa cu succes! Conf: {confidence:.2f}")
        else:
            print(f"[CLOUD] Eroare server: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[CLOUD] Eroare conexiune: {e}")

# 1. Încărcăm modelul tău antrenat pe drone
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = YOLO(os.path.join(BASE_DIR, "runs", "detect", "train-7", "weights", "best.pt"))

# 2. Inițializăm filtrul de fundal (Toleranță mare la zgomot)
back_sub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

# 3. Inițializăm clasificatorul Random Forest extern
rf_classifier = RandomForestRFClassifier()

# 4. Folder pentru alerte salvate automatic
output_folder = os.path.join(BASE_DIR, "alerte_drone")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Comutator hardware pentru antenă (Toggle)
rf_hardware_trigger = False
ultimul_timp_salvare = 0

cap = cv2.VideoCapture(0)
print("\n=== SMT (SISTEM MULTI-SENZORIAL) SUPREM PORNIT ===")
print("-> Toate filtrele de curățare (Tavan, Densitate, Dimensiune) sunt ACTIVE.")
print("-> APASĂ scurt pe tasta 'R' pentru a porni/opri scanarea antenei radio (Random Forest)!")
print("-> APASĂ 'T' pentru a simula o alertă de test (trimite la server)!\n")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Verificăm tastatura instantaneu
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r') or key == ord('R'):
        rf_hardware_trigger = not rf_hardware_trigger
        print(f"📡 [HARDWARE SDR] Stare antenă modificată! Scanare radio activă: {rf_hardware_trigger}")
    if key == ord('t') or key == ord('T'):
        print("[TEST] Simulez alertă manuală...")
        threading.Thread(target=trimite_la_server, args=(frame, 0.99, rf_hardware_trigger), daemon=True).start()

    # Apelăm clasificatorul Random Forest din fișierul extern
    rf_activ, rf_conf = rf_classifier.predict_signal(rf_hardware_trigger)

    # Eliminăm vibrațiile de lumină (Zgomotul de pe tavan)
    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    fg_mask = back_sub.apply(blurred_frame)
    
    # Curățăm masca de fundal (Filtre morfologice fine)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=1)

    # Rulăm AI-ul vizual (Strictețe crescută conf=0.50)
    results = model(frame, stream=True, conf=0.50)
    annotated_frame = frame.copy()
    
    drona_detectata_acum = False
    max_conf = 0.0

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            visual_conf = float(box.conf[0])
            
            # Filtru de Dimensiune Minimă (Ștergem erorile microscopice)
            latime = x2 - x1
            inaltime = y2 - y1
            if latime < 30 or inaltime < 30:
                continue
                
            suprafata_totala = latime * inaltime
            
            # Decupăm masca de mișcare din zona obiectului
            roi_mask = fg_mask[y1:y2, x1:x2]
            motion_pixels = cv2.countNonZero(roi_mask) if roi_mask.size > 0 else 0
            
            # Calculăm densitatea mișcării
            procent_miscare = (motion_pixels / suprafata_totala) if suprafata_totala > 0 else 0
            
            # Păstrăm obiectul doar dacă se mișcă real (densitate > 25%)
            if procent_miscare > 0.25:
                drona_detectata_acum = True
                
                # === FUZIUNEA DE SENZORI PROPRIU-ZISĂ ===
                if rf_activ:
                    # Dacă antena prinde semnal: 60% Cameră + 40% Random Forest RF
                    final_conf = (visual_conf * 0.6) + (rf_conf * 0.4)
                    color = (0, 255, 0) # VERDE: Confirmare Hibridă Totală
                    label = f"DRONE [AI+RF] {final_conf:.2f} (M: {procent_miscare*100:.0f}%)"
                else:
                    # Dacă nu avem semnal radio: 100% bazat pe YOLO color
                    final_conf = visual_conf
                    color = (255, 0, 0) # ALBASTRU: Doar confirmare vizuală
                    label = f"drone [AI] {final_conf:.2f} (M: {procent_miscare*100:.0f}%)"
                
                if final_conf > max_conf:
                    max_conf = final_conf
                
                # Desenăm pe ecran
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated_frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Sistemul automat de alerte pe disc (Scrie text și salvează poze)
    timp_curent = time.time()
    if drona_detectata_acum and (timp_curent - ultimul_timp_salvare > 2.0):
        ultimul_timp_salvare = timp_curent
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        ora_citibila = time.strftime("%Y-%m-%d %H:%M:%S")
        
        nume_poza = os.path.join(output_folder, f"alerta_{timestamp}.jpg")
        cv2.imwrite(nume_poza, annotated_frame)
        
        nume_log = os.path.join(output_folder, "log_evenimente.txt")
        with open(nume_log, "a", encoding="utf-8") as f:
            status_radio = "ACTIV" if rf_activ else "INACTIV"
            f.write(f"[{ora_citibila}] ALERTĂ SUPREMĂ: Dronă confirmată! Scor: {max_conf:.2f}. Senzor Radio: {status_radio}.\n")
            
        print(f"🚨 [SISTEM SUPREM] {ora_citibila} - Alerta salvată pe disc! Scor: {max_conf:.2f}")
        threading.Thread(
            target=trimite_la_server,
            args=(annotated_frame, max_conf, rf_activ),
            daemon=True,
        ).start()

    # Afișăm ferestrele live
    cv2.imshow("Filtru Fundal Curat", fg_mask)
    cv2.imshow("SMT: Fuziune AI + Random Forest", annotated_frame)

    if key == ord('q') or key == ord('Q'):
        break
    if cv2.getWindowProperty("SMT: Fuziune AI + Random Forest", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()