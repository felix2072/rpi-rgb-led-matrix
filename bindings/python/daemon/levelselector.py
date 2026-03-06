import sys
import termios
import tty
import signal
import os

# Funktion zum Abfangen von Strg+C (SIGINT) und Beenden des Programms
def signal_handler(sig, frame):
    print("\nProgramm wird beendet...")
    sys.exit(0)

# getch-Funktion zum Abrufen einer Taste ohne Eingabetaste
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch.lower()

# Funktion zum Speichern des Levels in einer Textdatei
def save_level_to_file(level):
    file_path = "/home/felix/rpi-rgb-led-matrix/bindings/python/daemon/levelselector.txt"
    with open(file_path, "w") as f:
        f.write(f"{level}\n")
    print(f"Level {level} wurde gespeichert.")

# Hauptfunktion
def main():
    print("Drücke eine Zahl von 1 bis 9, um den Level auszuwählen ('s' oder 'k' oder 'p' zum Beenden)")

    while True:
        ch = getch()
        if ch in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            save_level_to_file(ch)
        elif ch in ['s','k','p']:
            print("\nProgramm wird beendet...")
            sys.exit(0)
        else:
            print("Ungültige Eingabe. Bitte eine Zahl von 1 bis 9 drücken.")

if __name__ == "__main__":
    # Signalhandler für Strg+C (SIGINT)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Hauptprogramm starten
    main()
