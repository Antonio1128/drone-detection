import time

SAMPLES = 50
# MQ-2: Rs/R0 = 9.8 in aer curat (din datasheet)
RS_R0_CLEAN_AIR = 9.8

def get_channel():
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    return AnalogIn(ads, 0)

def calibrate():
    print("=== CALIBRARE MQ-2 ===")
    print("Incalzire sensor (60s) — tine senzorul in AER CURAT...")
    time.sleep(60)
    print(f"Citire {SAMPLES} esantioane...\n")

    chan = get_channel()
    readings = []
    for i in range(SAMPLES):
        v = chan.voltage
        if v > 0:
            readings.append((5.0 - v) / v)
        print(f"  [{i+1}/{SAMPLES}] Voltage: {v:.4f}V  Rs/RL: {(5.0-v)/v if v>0 else 'N/A':.4f}")
        time.sleep(0.1)

    rs_clean = sum(readings) / len(readings)
    r0 = rs_clean / RS_R0_CLEAN_AIR

    print(f"\n--- REZULTAT ---")
    print(f"Rs mediu in aer curat : {rs_clean:.4f}")
    print(f"R0 calculat           : {r0:.4f}")
    print(f"\nActualizeaza in gas_sensor.py:")
    print(f"  R0 = {r0:.4f}  # calibrat {time.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    calibrate()
