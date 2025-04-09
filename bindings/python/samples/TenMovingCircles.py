#!/usr/bin/env python
import random
import time
import math
from samplebase import SampleBase
from rgbmatrix import graphics


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
            Ay = acc_y

            return Ax, Ay

    except FileNotFoundError:
        print(f"Die Datei {file_path} wurde nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Auslesen der Datei: {e}")
        return None


class MovingCircle:
    def __init__(self, x, y, dx, dy, size=1):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.size = size
        self.color = graphics.Color(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.gravity_strength = 0.2
        self.bounce_loss = 0.8

    def apply_gravity(self, Ax, Ay):
        # Verwende Ax und Ay als Richtung der Gravitation
        self.dx += Ax * self.gravity_strength
        self.dy += Ay * self.gravity_strength

    def update(self, width, height):
        # Wende die Gravitation an
        self.apply_gravity(0, 0)  # Hier wird die Gravitation durch Ax und Ay beeinflusst

        # Update der Position
        self.x += self.dx
        self.y += self.dy

        # Bounce an den Kanten
        if self.x - self.size < 0 or self.x + self.size >= width:
            self.dx *= -1
            self.x += self.dx

        if self.y - self.size < 0 or self.y + self.size >= height:
            self.dy *= -1
            self.y += self.dy
        
        self.dx *= 0.99
        self.dy *= 0.99

    def check_collision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.hypot(dx, dy)
        if distance < self.size + other.size:
            # Einfache elastische Kollision
            self.dx, other.dx = other.dx, self.dx
            self.dy, other.dy = other.dy, self.dy

    def draw(self, canvas):
        graphics.DrawCircle(canvas, int(self.x), int(self.y), self.size, self.color)


class TenMovingCircles(SampleBase):
    def __init__(self, *args, **kwargs):
        super(TenMovingCircles, self).__init__(*args, **kwargs)
        self.last_gravity_change = time.time()
        self.change_interval = 5  # seconds

    def run(self):
        balls = []
        for _ in range(10):
            x = random.randint(5, self.matrix.width - 5)
            y = random.randint(0, 5)
            dx = random.uniform(-0.5, 0.5)
            dy = random.uniform(0, 0.5)
            circle = MovingCircle(x, y, dx, dy)
            balls.append(circle)

        # Initialisiere die Gravity für alle Bälle
        canvas = self.matrix.CreateFrameCanvas()

        while True:
            # Lese die MPU-Daten aus der Datei (nur Ax und Ay)
            mpu_data = read_mpu_data()

            # Wenn Daten erfolgreich ausgelesen wurden, setze sie als Gravitation
            if mpu_data:
                Ax, Ay = mpu_data
                for ball in balls:
                    ball.apply_gravity(Ax, Ay)  # Setze die Accelerometer-Daten als Gravitation

            canvas.Clear()

            # Kollisionserkennung
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    balls[i].check_collision(balls[j])

            # Update und Zeichnen
            for ball in balls:
                ball.update(self.matrix.width, self.matrix.height)
                ball.draw(canvas)

            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(0.03)


# Main function
if __name__ == "__main__":
    app = TenMovingCircles()
    if not app.process():
        app.print_help()
