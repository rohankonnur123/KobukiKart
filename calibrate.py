import Adafruit_BBIO.UART as UART
import Adafruit_TCS34725
import smbus
import math
import time

COLOR_FILE = "color_mappings.txt"

def write_colors(color_mappings):
    """
    Writes existing colors to COLOR_FILE
    """
    _file = open(COLOR_FILE, "w")
    for color in color_mappings:
        _file.write("{0},{1},".format(color, color_mappings[color]))

def calibrate(tcs):
    """
    Checks for existing color mappings file and asks user to re-calibrate or not
    Takes in a color sensor object and begins reading values
    On Ctrl+C, prompts for a color name
        - if name entered, stores reference color 'magnitude' to COLOR_MAPPINGS
        - else, writes existing color mappings and exits calibration
    Returns dictionary of color/magnitude pairs
    """
    color_mappings = {}
    while True:
        try:
            # Read the R, G, B, C color data.
            r, g, b, _ = tcs.get_raw_data()

            # Print out the values.
            print("red={0} green={1} blue={2}".format(r, g, b))
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
                r_avg = r_sum / 5
                g_avg = g_sum / 5
                b_avg = g_sum / 5
                # Input average to mapping
                color_mappings[color] = \
                    math.sqrt((r_avg*r_avg) + (g_avg*g_avg) + (b_avg*b_avg))
            else:
                break
    write_colors(color_mappings)
