# Based on example code provided with Adafruit TCS34725 library. Author: Tony DiCola

# Import the TCS34725 module.
import Adafruit_TCS34725
import smbus
import time
import math

tcs = Adafruit_TCS34725.TCS34725(address=0x29, busnum=1)

# Disable interrupts (can enable them by passing true, see the set_interrupt_limits function too).
tcs.set_interrupt(False)

color_mappings = {}

while True:
  try:
    # Read the R, G, B, C color data.
    r, g, b, _ = tcs.get_raw_data()

    # Print out the values.
    print('red={0} green={1} blue={2}'.format(r, g, b))
    time.sleep(0.5)
  except KeyboardInterrupt:
    color = str(raw_input("Enter color name (or Enter to exit): "))
    if color:
      # Average the next 5 data points
      r_sum, g_sum, b_sum, _ = 0, 0, 0, 0
      print("sampling {0} color. . .".format(color))
      for i in range(5):
        _r, _g, _b, _ = tcs.get_raw_data()
        r_sum += _r
        g_sum += _g
        b_sum += _b
        time.sleep(0.3)
      r_avg = r_sum // 5
      g_avg = g_sum // 5
      b_avg = g_sum // 5
      # Input average to mapping
      color_mappings[color] = math.sqrt((r_avg * r_avg) + (g_avg * g_avg) + (b_avg * b_avg))
    else:
      break

if color_mappings:
  # Print color values
  print("[color]: [r], [g], [b]")
  for color in color_mappings.keys():
    rgb = color_mappings[color]
    print("{0}: {1}".format(color, str(rgb)))

def is_color(color):
  r, g, b, _ = tcs.get_raw_data()
  test = math.sqrt((r*r) + (g*g) + (b*b))
  rgb = color_mappings[color]
  return rgb - 2 < test and test < rgb + 2

while True:
  try:
    r, g, b, _ = tcs.get_raw_data()
  except KeyboardInterrupt:
    test = str(raw_input("Want to test for a color? (Hit Enter to exit): "))
    if test:
      for color in color_mappings:
        if is_color(color):
          print("detected {0} ".format(color))
    else:
      break

# Enable interrupts and put the chip back to low power sleep/disabled.
tcs.set_interrupt(True)
tcs.disable()
