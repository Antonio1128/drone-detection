import cv2
import numpy as np
from ultralytics import YOLO
from rf_classifier import RandomForestRFClassifier

# 1. Încărcăm modelul tău antrenat pe drone
model = YOLO(r"C:\Users\mario\Desktop\prj\runs\detect\train-7\weights\best.pt")

# 2. Inițializăm clasificatorul Random Forest extern
rf_classifier = RandomForestRFClassifier()

cap = cv2.VideoCapture(0)

# Variabilă de tip comutator (Toggle) - pornește dezactivată
rf_hardware_trigger = False

print("\n=== PIPELINE DE TEST: AI + RADIO RF (COMPLET CURAT) ===")
print("-> APASĂ o singură dată scurt pe 'R' pentru a porni/opri semnalul Random Forest.")
print("-> Apasă 'Q' pentru a închide.\n")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Verificăm tastatura instantaneu
    key = cv2.waitKey(1) & 0xFF
    
    # Dacă apeși R scurt, comutăm starea ca la un întrerupător (Toggle)
    if key == ord('r') or key == ord('R'):
        rf_hardware_trigger = not rf_hardware_trigger
        print(f"[HARDWARE SDR] Stare antenă radio modificată! Activă: {rf_hardware_trigger}")

    # Apelăm clasificatorul Random Forest din fișierul extern
    rf_activ, rf_conf = rf_classifier.predict_signal(rf_hardware_trigger)

    # Rulăm AI-ul vizual cu un prag rezonabil de test (0.35) ca să detecteze mai stabil
    results = model(frame, stream=True, conf=0.35)
    annotated_frame = frame.copy()

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            visual_conf = float(box.conf[0])
            
            if rf_activ:
                # Fuziune multi-senzorială: 60% Cameră + 40% Random Forest RF
                final_conf = (visual_conf * 0.6) + (rf_conf * 0.4)
                color = (0, 255, 0) # Verde de confirmare militară
                label = f"DRONE [AI+RF] {final_conf:.2f}"
            else:
                final_conf = visual_conf
                color = (255, 0, 0) # Albastru (doar vizual)
                label = f"drone [AI] {final_conf:.2f}"
            
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Afișăm fereastra hibridă
    cv2.imshow("Sistem EXPERIMENTAL: AI + Radio RF", annotated_frame)

    if key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()