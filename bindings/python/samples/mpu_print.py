import time

def read_mpu_data():
    try:
        with open("/tmp/mpu_data.txt", "r") as f:
            data = f.read().strip().split(",")
            return float(data[0]), float(data[1]), float(data[2])
    except:
        return 0, 0, 0  # Falls Datei nicht gefunden oder Fehler

while True:
    acc_x, acc_y, acc_z = read_mpu_data()
    print(f"X: {acc_x}, Y: {acc_y}, Z: {acc_z}")  # Ersetze das mit der LED-Logik
    time.sleep(0.1)