from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
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

class RotatingClock(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RotatingClock, self).__init__(*args, **kwargs)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf", 10)
        self.rotation_speed = 2.0  # Grad pro Sekunde

    def run(self):

        while True:

            # Uhrzeit holen (z.B. 12:34)
            current_time = time.strftime("%H•%M")

            # Neues leeres Bild vorbereiten
            final_img = Image.new("RGB", (self.matrix.width, self.matrix.height), (0, 0, 0))
            draw = ImageDraw.Draw(final_img)

            # Positionierung vorbereiten
            char_spacing = 1
            x = -2

            # Lese die MPU-Daten aus der Datei (nur Ax und Ay)
            mpu_data = read_mpu_data()

            # Wenn Daten erfolgreich ausgelesen wurden, setze sie als Gravitation
            if mpu_data:
                Ax, Ay = mpu_data
                Ax *= -1
                angle = math.degrees(math.atan2(Ay, Ax))+90

            for i, char in enumerate(current_time):

                # Zeichen rendern
                bbox = self.font.getbbox(char)
                char_width = bbox[2] - bbox[0]
                char_height = bbox[3] - bbox[1]

                # Etwas mehr Platz zum Rotieren (Padding)
                size = (char_width + 4, char_height + 4)  # +4 Padding für Drehen
                char_img = Image.new("RGBA", size, (0, 0, 0, 0))
                char_draw = ImageDraw.Draw(char_img)

                # Farbe (Blinkender Doppelpunkt)
                if char == "•" and (time.time() % 1) < 0.5:
                    fill = (0, 0, 0)
                else:
                    fill = (255, 0, 0)

    	        # Offset für zentriertes Texten
                text_offset_x = (size[0] - char_width+3) // 2
                text_offset_y = (size[1] - char_height-2) // 2
                char_draw.text((text_offset_x, text_offset_y), char, font=self.font, fill=fill)

                # Rotation mit expand=True
                rotated = char_img.rotate(angle, resample=Image.BICUBIC, expand=True)

                enhancer = ImageEnhance.Sharpness(final_img)
                res = enhancer.enhance(10) 

                # Improve contrast
                enhancer = ImageEnhance.Contrast(res)
                final_img = enhancer.enhance(10)

                # Zielposition (y zentriert)
                paste_y = (self.matrix.height - rotated.height) // 2 -2
                final_img.paste(rotated, (x, paste_y), rotated)

                #x += rotated.width-5
                x += 6

                #if x >= self.matrix.width:
                #    break  # Stop if we overflow the screen

            # Auf die Matrix übertragen
            self.matrix.SetImage(final_img.convert("RGB"))
            time.sleep(0.03)

# Main
if __name__ == "__main__":
    app = RotatingClock()
    if not app.process():
        app.print_help()
