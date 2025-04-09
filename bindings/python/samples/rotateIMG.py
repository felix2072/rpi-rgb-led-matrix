from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
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


# Main function
if __name__ == "__main__":
    app = RotateEachChar()
    if not app.process():
        app.print_help()
