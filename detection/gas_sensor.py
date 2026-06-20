import time
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.environ.get("SERVER_URL", "").replace("/report/detection", "/report/gas")
API_KEY = os.environ["API_KEY"]

# Prag periculos (ajustat dupa calibrare)
GAS_THRESHOLD_PPM = 300
INTERVAL = 2.0       # secunde intre citiri locale
SEND_INTERVAL = 15.0 # secunde intre trimiteri la server

def read_gas_ppm():
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn

    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    chan = AnalogIn(ads, 0)

    voltage = chan.voltage

    # Conversie aproximativa tensiune → PPM pentru MQ-2
    # Rs/R0 ratio — calibrat in aer curat (R0 ≈ tensiune la aer curat)
    R0 = 1.2691  # calibrat 2026-06-20
    if voltage <= 0:
        return 0.0
    rs = (5.0 - voltage) / voltage
    ratio = rs / R0
    # Formula logaritmica aproximativa MQ-2 pentru LPG/Smoke
    ppm = 1000 * (ratio ** -2.3)
    return round(ppm, 2)

def trimite_la_server(ppm, is_dangerous):
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        response = requests.post(
            SERVER_URL,
            json={"ppm": ppm, "is_dangerous": is_dangerous, "timestamp": timestamp},
            headers={"x-api-key": API_KEY},
            timeout=10,
        )
        if response.status_code == 200:
            print(f"[CLOUD] Gas alert sent: {ppm} ppm")
        else:
            print(f"[CLOUD] Server error: {response.status_code}")
    except Exception as e:
        print(f"[CLOUD] Connection error: {e}")

if __name__ == "__main__":
    print("=== GAS SENSOR MQ-2 STARTED ===")
    print(f"Danger threshold: {GAS_THRESHOLD_PPM} ppm")
    print("Warming up sensor (60s)...")
    time.sleep(60)
    print("Sensor ready.\n")

    last_send = 0

    while True:
        try:
            ppm = read_gas_ppm()
            is_dangerous = ppm > GAS_THRESHOLD_PPM
            status = "DANGER" if is_dangerous else "safe"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Gas: {ppm} ppm — {status}")

            now = time.time()
            if is_dangerous or (now - last_send >= SEND_INTERVAL):
                trimite_la_server(ppm, is_dangerous)
                last_send = now

        except Exception as e:
            print(f"[SENSOR] Read error: {e}")

        time.sleep(INTERVAL)
