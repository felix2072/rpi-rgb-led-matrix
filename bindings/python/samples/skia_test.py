import skia
import numpy as np
import cv2
import math
import time

WIDTH, HEIGHT = 256, 256

def draw(canvas, angle):
    scale = WIDTH
    R = 0.45 * scale
    TAU = 6.2831853

    path = skia.Path()
    path.moveTo(R, 0.)
    for i in range(7):
        theta = 3 * i * TAU / 7
        path.lineTo(R * math.cos(theta), R * math.sin(theta))
    path.close()

    paint = skia.Paint()
    paint.setAntiAlias(True)
    paint.setColor(skia.ColorBLUE)

    canvas.clear(skia.ColorWHITE)
    canvas.translate(WIDTH/2, HEIGHT/2)
    canvas.rotate(angle)
    canvas.drawPath(path, paint)

def render_loop():
    angle = 0
    while True:
        surface = skia.Surface(WIDTH, HEIGHT)
        canvas = surface.getCanvas()
        draw(canvas, angle)

        image = surface.makeImageSnapshot()
        data = image.encodeToData()
        arr = np.frombuffer(bytes(data), np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)

        cv2.imshow("Rotating Star", img)
        if cv2.waitKey(10) == 27:  # ESC zum Beenden
            break

        angle += 2  # Winkel erhöhen
        if angle >= 360:
            angle -= 360

    cv2.destroyAllWindows()

render_loop()
