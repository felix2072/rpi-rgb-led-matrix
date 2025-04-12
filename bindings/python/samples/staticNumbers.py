""" from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from samplebase import SampleBase
import time
import math

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
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf", 12)
        #self.rotation_duration = 2.0  # Sekunden pro Umdrehung

    def run(self):
        #start_time = time.time()

        char_spacing = 2  # Abstand zwischen Zeichen
        while True:

             # Zeit aktualisieren (jede Sekunde neu)
            current_time = time.strftime("%H") + "•" + time.strftime("%M")
            self.text = current_time
            self.text = "12•34"
            # Blink-Logik für den mittleren Punkt
            blink_on = (time.time() % 1) < 0.5  # True in der ersten halben Sekunde jeder Sekunde

            # Lese die MPU-Daten aus der Datei (nur Ax und Ay)
            mpu_data = read_mpu_data()

            # Wenn Daten erfolgreich ausgelesen wurden, setze sie als Gravitation
            if mpu_data:
                Ax, Ay = mpu_data
                Ax *= -1
                angle = angle = math.degrees(math.atan2(Ay, Ax))-90


            #elapsed = time.time() - start_time
            #angle = (elapsed / self.rotation_duration) * 360 % 360
            #angle = 0
            # Leeres Endbild vorbereiten
            final_img = Image.new("RGB", (self.matrix.width, self.matrix.height), (0, 0, 0))

            # Positionierung vorbereiten
            total_width = 0
            char_imgs = []

            # Berechne Breite aller rotierenden Chars
            for char in self.text:
                bbox = self.font.getbbox(char)
                size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
                total_width += size[0] + char_spacing

            # Start X berechnen, damit mittig
            x = (self.matrix.width - total_width + char_spacing) // 2
            
            # Jedes Zeichen separat rendern, rotieren, einfügen
            for char in self.text:
                # Bild für das Zeichen
                bbox = self.font.getbbox(char)
                size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
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


# Main function
if __name__ == "__main__":
    app = RotateEachChar()
    if not app.process():
        app.print_help()
 """

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from samplebase import SampleBase
import time

class SimpleClock(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SimpleClock, self).__init__(*args, **kwargs)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf", 10)
        self.rotation_step = 90  # Grad pro Sekunde
        self.last_update = 0
        self.char_angles = [0] * 5  # Für HH:MM (z. B. ['1', '2', ':', '3', '4'])

    def run(self):
        while True:
            current_second = int(time.time())

            # Einmal pro Sekunde updaten
            if current_second != self.last_update:
                self.last_update = current_second
                self.char_angles = [(angle + self.rotation_step) % 360 for angle in self.char_angles]

            # Uhrzeit als Text holen
            current_time = time.strftime("%H") + ":" + time.strftime("%M")

            # Neues leeres Bild erzeugen
            final_img = Image.new("RGB", (self.matrix.width, self.matrix.height), (0, 0, 0))
            draw = ImageDraw.Draw(final_img)

            # Positionierung vorbereiten
            char_spacing = 1
            x = 0

            # Textgröße berechnen
            text_size = draw.textbbox((0, 0), current_time, font=self.font)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]

            # Zentrierte Position berechnen
            x = (self.matrix.width - text_width) // 2
            y = (self.matrix.height - text_height) // 2
            for i, char in enumerate(current_time):

                angle = self.char_angles[i]
                
                bbox = self.font.getbbox(char)
                
                size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
                char_img = Image.new("RGBA", (6,13), (0, 0, 0, 0))
                char_draw = ImageDraw.Draw(char_img)

                print(bbox)

                # Blinkender Doppelpunkt
                if char == ":" and (time.time() % 1) < 0.5:
                    fill = (0, 0, 0)
                else:
                    fill = (255, 0, 0)
                # Text zeichnen (rot)
                char_draw.text((0, 0), char, font=self.font, fill=fill)

                # Drehen
                rotated = char_img.rotate(angle, resample=Image.BICUBIC, expand=True)
                #char_img = char_img.filter(ImageFilter.SHARPEN)

                # Sharpen 
                enhancer = ImageEnhance.Sharpness(final_img)
                res = enhancer.enhance(10) 

                # Improve contrast
                enhancer = ImageEnhance.Contrast(res)
                final_img = enhancer.enhance(10)
                
                # Zielposition (zentriert auf Y)
                paste_y = (self.matrix.height - rotated.height) // 2
                final_img.paste(rotated, (x, paste_y), rotated)

                x += rotated.width + char_spacing
                if x >= self.matrix.width:
                    break

            # Auf die Matrix übertragen
            self.matrix.SetImage(final_img.convert("RGB"))
            time.sleep(0.03)

# Main
if __name__ == "__main__":
    app = SimpleClock()
    if not app.process():
        app.print_help()
