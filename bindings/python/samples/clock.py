#!/usr/bin/env python
import random
import time
import math
from samplebase import SampleBase
from rgbmatrix import graphics
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

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

class RotateEachChar(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RotateEachChar, self).__init__(*args, **kwargs)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf", 8)
        #self.rotation_duration = 2.0  # Sekunden pro Umdrehung

    def run(self):
        #start_time = time.time()

        char_spacing = 2  # Abstand zwischen Zeichen
        while True:

             # Zeit aktualisieren (jede Sekunde neu)
            current_time = time.strftime("%H") + "•" + time.strftime("%M")
            self.text = current_time

            # Blink-Logik für den mittleren Punkt
            blink_on = (time.time() % 1) < 0.5  # True in der ersten halben Sekunde jeder Sekunde

            # Lese die MPU-Daten aus der Datei (nur Ax und Ay)
            mpu_data = read_mpu_data()

            # Wenn Daten erfolgreich ausgelesen wurden, setze sie als Gravitation
            if mpu_data:
                Ax, Ay = mpu_data
                Ax *= -1
                angle = angle = math.degrees(math.atan2(Ay, Ax))-90

            # Leeres Endbild vorbereiten
            final_img = Image.new("RGB", (self.matrix.width, self.matrix.height), (0, 0, 0))

            # Positionierung vorbereiten
            total_width = 0
            char_imgs = []

            # Berechne Breite aller rotierenden Chars
            for char in self.text:
                size = self.font.getsize(char)
                total_width += size[0] + char_spacing

            # Start X berechnen, damit mittig
            x = (self.matrix.width - total_width + char_spacing) // 2
            
            # Jedes Zeichen separat rendern, rotieren, einfügen
            for char in self.text:
                # Bild für das Zeichen
                size = self.font.getsize(char)
                char_img = Image.new("RGBA", size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(char_img)

                # Wähle Farbe: nur der mittlere Punkt blinkt
                if char == "•":
                    color = (0, 0, 0) if blink_on else (255, 0, 0)
                else:
                    color = (255, 0, 0)

                draw.text((0, 0), char, font=self.font, fill=color)
                #char_img = char_img.filter(ImageFilter.SHARPEN)

                # Sharpen 
                enhancer = ImageEnhance.Sharpness(char_img)
                res = enhancer.enhance(10) 

                # Improve contrast
                enhancer = ImageEnhance.Contrast(res)
                char_img = enhancer.enhance(10)

                # Rotieren um Mittelpunkt
                rotated = char_img.rotate(angle, resample=Image.BICUBIC, expand=True)

                # Positionieren
                paste_x = x + (size[0] - rotated.width) // 2
                paste_y = (self.matrix.height - rotated.height) // 2
                final_img.paste(rotated, (paste_x, paste_y), rotated)

                x += size[0] + char_spacing

            self.matrix.SetImage(final_img.convert("RGB"))
            time.sleep(0.03)

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


class Clock(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Clock, self).__init__(*args, **kwargs)

    def run(self):
        balls = []
        canvas = self.matrix.CreateFrameCanvas()

        start_time = time.time()
        last_created_second = -1  # Zum Tracken der letzten Ball-Erzeugung

        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            current_second = int(elapsed)

            # MPU-Daten auslesen
            mpu_data = read_mpu_data()
            if mpu_data:
                Ax, Ay = mpu_data
                for ball in balls:
                    ball.apply_gravity(Ax, Ay)

            # Alle 60 Sekunden zurücksetzen
            if current_second >= 60:
                balls.clear()
                start_time = current_time
                last_created_second = -1  # Reset auch hier

            # Richtung berechnen
            angle_rad = math.atan2(Ay, Ax)  # Richtung der "Schwerkraft"
            sin_a = math.sin(angle_rad)
            cos_a = math.cos(angle_rad)

            # Erzeuge neuen Ball jede Sekunde
            if current_second != last_created_second:
                margin = 5  # etwas Abstand vom Rand

                # Bestimme Startposition basierend auf Gravitation
                if abs(Ax) > abs(Ay):  # horizontale "Gravitation"
                    if Ax > 0:
                        x = margin  # kommt von links rein
                    else:
                        x = self.matrix.width - margin  # von rechts
                    y = random.randint(margin, self.matrix.height - margin)
                else:  # vertikale "Gravitation"
                    if Ay > 0:
                        y = margin  # von oben
                    else:
                        y = self.matrix.height - margin  # von unten
                    x = random.randint(margin, self.matrix.width - margin)

                dx = cos_a * 0.5  # Startimpuls in Grav-Richtung
                dy = sin_a * 0.5
                circle = MovingCircle(x, y, dx, dy)
                balls.append(circle)
                last_created_second = current_second


            # Kollisionen prüfen
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    balls[i].check_collision(balls[j])

            canvas.Clear()

            # Bälle updaten & zeichnen
            for ball in balls:
                ball.update(self.matrix.width, self.matrix.height)
                ball.draw(canvas)

            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(0.03)


# Main function
if __name__ == "__main__":
    app = Clock()
    if not app.process():
        app.print_help()
