from picamera2 import Picamera2
import cv2

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

print("Camera pornita. Apasa 'q' pentru a iesi.")

while True:
    frame = picam2.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imshow("Camera Test", frame_bgr)
    key = cv2.waitKey(30)
    if key == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()
