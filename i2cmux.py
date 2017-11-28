import smbus
import time
import Adafruit_I2C as I2C
import Adafruit_TCS34725

TCA9548A_ADDRESS = 0x70
TCS34725_ADDRESS = 0x29
CONTROL_ADDRESS = 0x04

device = I2C.Adafruit_I2C(TCA9548A_ADDRESS, 1, True)

def tca_select(i):
  # Try writing an 8-bit select number
  device.write8(CONTROL_ADDRESS, 1<<i)

# Two color sensors attached to mux port 2 and 6
tca_select(2)
tcs2 = Adafruit_TCS34725.TCS34725(address=TCS34725_ADDRESS, busnum=1)
tca_select(6)
tcs6 = Adafruit_TCS34725.TCS34725(address=TCS34725_ADDRESS, busnum=1)

while True:
  # Read from first sensor
  tca_select(2)
  r, g, b, _ = tcs2.get_raw_data()
  print("I2C PORT 2 - R: {0}, G: {1}, B: {2}".format(r, g, b))
  time.sleep(0.5)

  # Read from second sensor
  tca_select(6)
  r, g, b, _ = tcs6.get_raw_data()
  print("I2C PORT 6 - R: {0}, G: {1}, B: {2}".format(r, g, b))
  time.sleep(0.5)
