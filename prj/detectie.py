import cv2
from ultralytics import YOLO

# 1. Încărcăm modelul BEST pe care l-ai antrenat adineauri
# YOLO salvează automat ultimul antrenament în folderul 'train' cu cel mai mare număr
model = YOLO(r"C:\Users\mario\Desktop\prj\runs\detect\train-3\weights\best.pt")

# 2. Deschidem camera web (0 este camera implicită a laptopului/PC-ului)
# Dacă vrei să testezi pe un video descărcat, înlocuiește 0 cu "nume_video.mp4"
cap = cv2.VideoCapture(0)

print("Se deschide camera web... Apasă tasta 'Q' pentru a închide fereastra!")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Rulăm AI-ul pe fiecare cadru de la cameră
    results = model(frame, stream=True)

    # Vizualizăm rezultatele (desenează pătrățelele de detecție)
    for r in results:
        annotated_frame = r.plot()
        
    # Afișăm fereastra video pe ecran
    cv2.imshow("YOLOv8 Detecție în Timp Real", annotated_frame)

    # Dacă apeși tasta 'q', se închide camera
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()