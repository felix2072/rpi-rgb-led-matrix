import random
import time
import math

import cv2
import skia
from PIL import ImageFont

WIDTH, HEIGHT = 256, 256  # Canvas-Größe

def read_mpu_data():
    file_path = "../daemon/mpu_data.txt"
    try:
        with open(file_path, "r") as f:
            data = f.readlines()

        for line in data:
            line = line.strip()
            values = line.split(",")
            acc_x = float(values[0])
            acc_y = float(values[1])

            Ax = acc_x * -1.0
            Ax += 0.044
            Ay = acc_y * -1.0

            return Ax, Ay
    except FileNotFoundError:
        print(f"Die Datei {file_path} wurde nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Auslesen der Datei: {e}")
        return None

class MovingCircle:
    def __init__(self, x, y, dx, dy, size=5):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.size = size
        self.color = skia.Color(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.gravity_strength = 0.2
        self.bounce_loss = 0.8

    def apply_gravity(self, Ax, Ay):
        self.dx += Ax * self.gravity_strength
        self.dy += Ay * self.gravity_strength

    def update(self, width, height):
        self.x += self.dx
        self.y += self.dy

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
            self.dx, other.dx = other.dx, self.dx
            self.dy, other.dy = other.dy, self.dy

    def draw(self, canvas):
        paint = skia.Paint()
        paint.setAntiAlias(True)
        paint.setColor(self.color)
        canvas.drawCircle(self.x, self.y, self.size, paint)

class Clock:
    def __init__(self):
        self.balls = []
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf", 16)

    def run(self):
        start_time = time.time()
        last_created_second = -1

        while True:
            surface = skia.Surface(WIDTH, HEIGHT)
            canvas = surface.getCanvas()
            canvas.clear(skia.ColorBLACK)

            current_time = time.time()
            elapsed = current_time - start_time
            current_second = int(elapsed)

            mpu_data = read_mpu_data()
            if mpu_data:
                Ax, Ay = mpu_data
                for ball in self.balls:
                    ball.apply_gravity(Ax, Ay)

            if current_second >= 60:
                self.balls.clear()
                start_time = current_time
                last_created_second = -1

            angle_rad = math.atan2(Ay, Ax)
            sin_a = math.sin(angle_rad)
            cos_a = math.cos(angle_rad)

            if current_second != last_created_second:
                margin = 5
                if abs(Ax) > abs(Ay):
                    if Ax > 0:
                        x = margin
                    else:
                        x = WIDTH - margin
                    y = random.randint(margin, HEIGHT - margin)
                else:
                    if Ay > 0:
                        y = margin
                    else:
                        y = HEIGHT - margin
                    x = random.randint(margin, WIDTH - margin)

                dx = cos_a * 0.5
                dy = sin_a * 0.5
                circle = MovingCircle(x, y, dx, dy)
                self.balls.append(circle)
                last_created_second = current_second

            for i in range(len(self.balls)):
                for j in range(i + 1, len(self.balls)):
                    self.balls[i].check_collision(self.balls[j])

            for ball in self.balls:
                ball.update(WIDTH, HEIGHT)
                ball.draw(canvas)

            # Zeit anzeigen
            current_time_str = time.strftime("%H:%M:%S")
            img = ImageFont.Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
            draw = ImageFont.ImageDraw.Draw(img)
            draw.text((10, 10), current_time_str, font=self.font, fill=(255, 255, 255))
            skia_img = skia.Image.fromarray(img.tobytes(), skia.kRGBA_8888_ColorType)
            canvas.drawImage(skia_img, 0, 0)

            image = surface.makeImageSnapshot()
            data = image.encodeToData()
            arr = np.frombuffer(bytes(data), np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
            print("FPS:", 1 / (time.time() - current_time))
            cv2.imshow("Clock with Skia", img)
            if cv2.waitKey(10) == 27:
                break

            time.sleep(0.03)

        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = Clock()
    app.run()