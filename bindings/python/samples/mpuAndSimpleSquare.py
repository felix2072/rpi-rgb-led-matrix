import os
os.environ['PYTHONUNBUFFERED'] = "1"

#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
import time


# MPU6050 Register-Konstanten
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47
Device_Address = 0x68


class MPU6050:
    def __init__(self):
        #self.bus = smbus.SMBus(1)
        self.init_sensor()

    def init_sensor(self):
        self.bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
        self.bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
        self.bus.write_byte_data(Device_Address, CONFIG, 0)
        self.bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
        self.bus.write_byte_data(Device_Address, INT_ENABLE, 1)

    def read_raw_data(self, addr):
        high = self.bus.read_byte_data(Device_Address, addr)
        low = self.bus.read_byte_data(Device_Address, addr + 1)
        value = ((high << 8) | low)
        if value > 32768:
            value -= 65536
        return value

    def read_values(self):
        acc_x = self.read_raw_data(ACCEL_XOUT_H)
        acc_y = self.read_raw_data(ACCEL_YOUT_H)
        acc_z = self.read_raw_data(ACCEL_ZOUT_H)
        gyro_x = self.read_raw_data(GYRO_XOUT_H)
        gyro_y = self.read_raw_data(GYRO_YOUT_H)
        gyro_z = self.read_raw_data(GYRO_ZOUT_H)

        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0
        Gx = gyro_x / 131.0
        Gy = gyro_y / 131.0
        Gz = gyro_z / 131.0

        return Ax, Ay, Az, Gx, Gy, Gz


class SimpleSquaree(SampleBase):
    def __init__(self, *args, **kwargs):
        super(SimpleSquaree, self).__init__(*args, **kwargs)

    def run(self):
        
        canvas = self.matrix.CreateFrameCanvas()
        
        from smbus2 import SMBus
        bus = SMBus(1)
        print("MPU6050 Bus geöffnet!")

        mpu = MPU6050()
        font = graphics.Font()
        font.LoadFont("../../../fonts/6x10.bdf")  # Stelle sicher, dass der Pfad korrekt ist
        color = graphics.Color(255, 255, 0)


        while True:
            canvas.Clear()

            # Zeichne Rand
            for x in range(0, canvas.width):
                canvas.SetPixel(x, 0, 255, 0, 0)
                canvas.SetPixel(x, canvas.height - 1, 255, 0, 0)
            for y in range(0, canvas.height):
                canvas.SetPixel(0, y, 255, 0, 0)
                canvas.SetPixel(canvas.width - 1, y, 255, 0, 0)

            # MPU-Daten lesen
            Ax, Ay, Az, Gx, Gy, Gz = mpu.read_values()
            output = f"Ax:{Ax:.2f} Ay:{Ay:.2f}"
            graphics.DrawText(canvas, font, 2, 10, color, output)

            canvas = self.matrix.SwapOnVSync(canvas)
            time.sleep(0.2)


# Main function
if __name__ == "__main__":
    simple_squares = SimpleSquaree()
    if not simple_squares.process():
        simple_squares.print_help()
