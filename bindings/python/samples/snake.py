import sys
import termios
import tty
import os
import time
import math
from samplebase import SampleBase
import argparse
from collections import deque
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import random

def read_mpu_data():
    # Pfad zur Datei, in der die MPU-Daten gespeichert sind
    file_path = "../daemon/mpu_data.txt"
    
    try:
        with open(file_path, "r") as f:
            # Lese die Datei Zeile für Zeile
            data = f.readlines()

        for line in data:
            line = line.strip()  # Entfernt \n oder andere Whitespaces
            values = line.split(",")  # Teilt die Zeile bei jedem Komma
            
            # Umwandeln der Werte in Floats
            acc_x = float(values[0])
            acc_y = float(values[1])

            Ax = acc_x
            Ax += 0.044
            Ay = acc_y * -1.0

            return Ax, Ay

    except FileNotFoundError:
        print(f"Die Datei {file_path} wurde nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Auslesen der Datei: {e}")
        return None


class Snake(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Snake, self).__init__(*args, **kwargs)

    def parse_color(self, color_str):
        try:
            r, g, b = map(int, color_str.split(','))
            return r, g, b
        except:
            raise argparse.ArgumentTypeError("Color must be in r,g,b format")

    def interpolate(self, c1, c2, fraction):
        r = round(c1[0] * fraction + c2[0] * (1 - fraction))
        g = round(c1[1] * fraction + c2[1] * (1 - fraction))
        b = round(c1[2] * fraction + c2[2] * (1 - fraction))
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def spawn_food(self, canvas, trail):
        # Zufällige Position für das "Essen" erzeugen
        while True:
            x_food = random.randint(0, canvas.width - 1)
            y_food = random.randint(0, canvas.height - 1)
            if (x_food, y_food) not in trail:  # Stelle sicher, dass das Essen nicht auf der Snake liegt
                return x_food, y_food

    def run(self):
        canvas = self.matrix.CreateFrameCanvas()

        # Snake Anfangsposition
        x_pos = 5
        y_pos = 5
        trail = deque([(x_pos, y_pos)])

        front_color = (255, 0, 0)
        back_color = (0, 0, 0)
        trail_len = 0  # Startlänge des Trails
        max_trail_len = 10  # Maximale Länge des Trails

        # Initiales Essen (Apfel)
        food_x, food_y = self.spawn_food(canvas, trail)

        prev_x, prev_y = x_pos, y_pos  # Vorherige Position, um zu überprüfen, ob die Snake sich bewegt

        while True:

            # Get MPU movement
            mpu = read_mpu_data()
            if mpu:
                Ax, Ay = mpu

                Ax *= -1
                angle = math.degrees(math.atan2(Ay, Ax))-90
                
                # Bewegungslogik basierend auf dem Winkel
                if angle < -60 and angle > -120:
                    if x_pos < canvas.width - 1:  # Move right
                        x_pos += 1
                elif angle > 60 or angle < - 250:
                    if x_pos > 0:  # Move left
                        x_pos -= 1
                if angle < 20 and angle > -20:
                    if y_pos < canvas.height - 1:  # Move down
                        y_pos += 1
                elif angle < -150 and angle > -200:
                    if y_pos > 0:  # Move up
                        y_pos -= 1

                # Überprüfen, ob die Snake das Essen erreicht hat
                if (x_pos, y_pos) == (food_x, food_y):
                    trail_len += 1  # Trail wächst nur beim Einsammeln von Essen
                    if trail_len >= max_trail_len:
                        trail_len = 0
                        trail.clear()
                        trail.append((x_pos, y_pos))
                    # Neues Essen spawnen
                    food_x, food_y = self.spawn_food(canvas, trail)

                # Snake Kopf bewegen
                if (x_pos, y_pos) != (prev_x, prev_y):
                    trail.appendleft((x_pos, y_pos))  # Fügt den neuen Kopf vorne an (Trail wächst vorne)

                # Wenn der Trail größer als trail_len ist, entferne den ältesten Punkt
                if len(trail) > trail_len + 1:
                    trail.pop()  # Entferne den ältesten Punkt, der nicht Teil der Snake ist

            # Canvas löschen
            canvas.Clear()
            
            # Snake zeichnen
            distance_from_head = len(trail)
            for pos in trail:
                distance_from_head -= 1
                fraction = 1.0 - distance_from_head / len(trail)
                color = front_color
                canvas.SetPixel(pos[0], pos[1], *color)

            # Das "Essen" zeichnen
            canvas.SetPixel(food_x, food_y, 0, 255, 0)  # Weiß für das Essen

            canvas = self.matrix.SwapOnVSync(canvas)
            print(f"\rX,Y = {x_pos},{y_pos}     Trail Length = {trail_len}     ", end='', flush=True)

            prev_x, prev_y = x_pos, y_pos  # Speichere die Position der Snake für den nächsten Schritt

            time.sleep(0.1)  # Small delay to avoid overload

# Main function
if __name__ == "__main__":
    app = Snake()
    if not app.process():
        app.print_help()