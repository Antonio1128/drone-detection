import cv2
import numpy as np
import time
import os
from ultralytics import YOLO

# 1. Încărcăm modelul tău antrenat pe drone
model = YOLO(r"C:\Users\mario\Desktop\prj\runs\detect\train-7\weights\best.pt")

# 2. Inițializăm filtrul de fundal (Toleranță mare la zgomot)
back_sub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

# 3. Folder pentru alerte
output_folder = r"C:\Users\mario\Desktop\prj\alerte_drone"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

ultimul_timp_salvare = 0

cap = cv2.VideoCapture(0)
print("\n=== SISTEM MILITAR ULTRA-STRICT PORNIT ===")
print("-> S-a activat filtrul de Densitate a Mișcării (Minim 25% din suprafață).\n")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Eliminăm vibrațiile de lumină din cameră
    blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
    fg_mask = back_sub.apply(blurred_frame)
    
    # Curățăm masca de fundal ca să fie stabilă
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=1)

    # Rulăm AI-ul vizual (mărim pragul la 0.50 pentru siguranță crescută)
    results = model(frame, stream=True, conf=0.50)
    annotated_frame = frame.copy()
    
    drona_detectata_acum = False
    max_conf = 0.0

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            
            # Calculăm suprafața totală a pătrățelului detectat (lățime x înălțime)
            latime = x2 - x1
            inaltime = y2 - y1
            
            # === FILTRU DE DIMENSIUNE MINIMĂ ===
            # Dacă pătrățelul e mai mic de 30x30 pixeli, trecem peste el (e o alarmă falsă microscopică)
            if latime < 30 or inaltime < 30:
                continue
                
            suprafata_totala = latime * inaltime
            # Decupăm masca de mișcare corespunzătoare pătrățelului
            roi_mask = fg_mask[y1:y2, x1:x2]
            motion_pixels = cv2.countNonZero(roi_mask) if roi_mask.size > 0 else 0
            
            # CALCULĂM DENSITATEA: Cât la sută din pătrățel este alb (mișcare reală)?
            procent_miscare = (motion_pixels / suprafata_totala) if suprafata_totala > 0 else 0
            
            # === FILTRUL SUPREM ===
            # Obiectul trebuie să se miște masiv (să ocupe minim 25% din propriul pătrățel)
            if procent_miscare > 0.25:
                drona_detectata_acum = True
                if conf > max_conf:
                    max_conf = conf
                
                # Desenăm detecția DOAR dacă a trecut de filtrul de densitate radio-vizuală
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                label = f"drone {conf:.2f} (M: {procent_miscare*100:.0f}%)"
                cv2.putText(annotated_frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Sistemul automat de alerte pe disc
    timp_curent = time.time()
    if drona_detectata_acum and (timp_curent - ultimul_timp_salvare > 2.0):
        ultimul_timp_salvare = timp_curent
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        ora_citibila = time.strftime("%Y-%m-%d %H:%M:%S")
        
        nume_poza = os.path.join(output_folder, f"alerta_{timestamp}.jpg")
        cv2.imwrite(nume_poza, annotated_frame)
        
        nume_log = os.path.join(output_folder, "log_evenimente.txt")
        with open(nume_log, "a", encoding="utf-8") as f:
            f.write(f"[{ora_citibila}] ALERTĂ: Dronă confirmată cu densitate mare! Siguranță AI: {max_conf:.2f}.\n")
            
        print(f"🚨 [ALERTĂ STRICTĂ] {ora_citibila} - Confidență AI: {max_conf:.2f}")

    cv2.imshow("Filtru Fundal (Doar Miscare - FILTRAT)", fg_mask)
    cv2.imshow("Sistem Inteligent de Securitate UAV", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()