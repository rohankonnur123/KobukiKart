import smbus
import time
import Adafruit_I2C as I2C
import Adafruit_TCS34725

TCA9548A_ADDRESS = 0x70
TCS34725_ADDRESS = 0x29
CONTROL_ADDRESS = 0x04

device = I2C.Adafruit_I2C(TCA9548A_ADDRESS, 1, True)

# Try writing an 8-bit select number
device.write8(CONTROL_ADDRESS, 1<<6)
print("TCA Port #6")

# Try color sensor's I2C address
temp = Adafruit_TCS34725.TCS34725(address=TCS34725_ADDRESS, busnum=1)

while True:
  r, g, b, _ = temp.get_raw_data()
  print("R: {0}, G: {1}, B: {2}".format(r, g, b))
  time.sleep(0.5)
