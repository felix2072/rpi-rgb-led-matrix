import time
import subprocess

LEVEL_FILE = "/home/felix/rpi-rgb-led-matrix/bindings/python/daemon/levelselector.txt"
SCRIPT_PATHS = {
    "1": "/home/felix/rpi-rgb-led-matrix/bindings/python/samples/clock.py",
    "2": "/home/felix/rpi-rgb-led-matrix/bindings/python/samples/snake.py",
    "3": "/home/felix/rpi-rgb-led-matrix/bindings/python/samples/rotating-block-generator.py",
    "4": "/home/felix/rpi-rgb-led-matrix/bindings/python/samples/pulsing-colors.py",
    "5": "/home/felix/rpi-rgb-led-matrix/bindings/python/samples/runtext.py",
    "6": "/home/felix/rpi-rgb-led-matrix/bindings/python/samples/rotateIMG.py"
    # ... mehr Levels/Skripte hier ergänzen
}
BASE_ARGS = [
    "-r", "16", "--led-cols", "32", "--led-no-hardware-pulse", "LED_NO_HARDWARE_PULSE",
    "--led-row-addr-type", "2", "--led-brightness", "30", "--led-multiplexing", "13"
]

def read_level():
    try:
        with open(LEVEL_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")
        return None

def main():
    last_level = None
    process = None
    print("start")

    while True:
        level = read_level()

        if level != last_level:
            print(f"Level geändert zu: {level}")

            # Falls ein altes Script läuft → beenden
            if process:
                process.terminate()
                process.wait()
                print("Altes Script gestoppt.")

            # Neues Script starten, falls bekannt
            script = SCRIPT_PATHS.get(level)
            if script:
                print(["sudo /home/felix/rpi-rgb-led-matrix/venv/bin/python3", script] + BASE_ARGS)
                process = subprocess.Popen(["sudo", "/home/felix/rpi-rgb-led-matrix/venv/bin/python3", script] + BASE_ARGS)
                print(f"Script gestartet: {script}")
            else:
                print("Unbekanntes Level, kein Script gestartet.")

            last_level = level

        time.sleep(1)

if __name__ == "__main__":
    main()
