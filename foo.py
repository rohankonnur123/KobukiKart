#!/usr/bin/python

import Adafruit_BBIO.UART as UART
import Adafruit_TCS34725
import smbus
import math
import serial
import time
import array
import struct
import random
import cwiid

COLOR_FILE = "color_mappings.txt"

def read_colors():
    """
    Reads colors from COLOR_FILE
    File is formatted in color/magnitude pairs, separated by commas
    Returns dictionary of color/magnitude pairs
    """
    color_mappings = {}
    _file = open(COLOR_FILE, "r")
    colors = _file.read()
    colors.split(",")
    for i in range(len(colors)/2)
        color_mappings[colors[2*i]] = colors[2*i + 1]
    _file.close()
    return color_mappings

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
    try:
        color_mappings = read_colors()
        # Able to read from file, prompt for overwrite
        redo = str(raw_input("Read colors from file, re-calibrate? (y/n): "))
        if redo == "y" or redo == "Y":
            color_mappings = {}
        else:
            return color_mappings
    except IOError:
        print("No previous calibration to use, entering calibration")

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
    return color_mappings

def checkSum(data, length):
	cs = 0x00
	for i in range(2,length):
		cs = cs^data[i]
	return cs

def split_int16(data, LSB):
	if LSB:
		return data & 0x00FF
	else:
		return (data & 0xFF00) >> 8

def kobukiDrive(radius, speed):
	#print radius
	#print speed
	writeData = [chr(0x31)]*25
	writeData[0] = 0xAA
	writeData[1] = 0x55
	writeData[2] = 0x06
	writeData[3] = 0x01
	writeData[4] = 0x04
	writeData[5] = split_int16(speed, 1)
	writeData[6] = split_int16(speed, 0)
	writeData[7] = split_int16(radius, 1)
	writeData[8] = split_int16(radius, 0)

	writeData[9] = 13
	writeData[10] = 13
	writeData[11] = 0x1
	writeData[12] = 0xA0
	writeData[13] = 0x86
	writeData[14] = 1
	writeData[15] = 0
	writeData[16] = 0
	writeData[17] = 0
	writeData[18] = 0
	writeData[19] = 0
	writeData[20] = 0
	writeData[21] = 0
	writeData[22] = 0
	writeData[23] = 0
	writeData[24] = checkSum(writeData, 24);

	return writeData

def kobukiDriveSpeeds(rws,lws):
	CmdSpeed = 0
	CmdRadius = 0
	if abs(rws) > abs(lws):
		CmdSpeed = rws
	else:
		CmdSpeed = lws

	if rws == lws:
		CmdRadius = 0
	else:
		CmdRadius = (rws + lws) / (2.0 * (rws - lws) / 123.0)
		CmdRadius = int(CmdRadius)
		if CmdRadius > 32767:
			CmdRadius = 0
		if CmdRadius < -32768:
			CmdRadius = 0
		if CmdRadius == 0:
			CmdRadius = 1

	if CmdRadius == 1:
		CmdSpeed = CmdSpeed * -1

	return kobukiDrive(int(CmdRadius),int(CmdSpeed))

def toByteArray(data):
	#byteData = [struct.pack('<I', n) for n in data]
	byteData = array.array('B',data).tostring()
	return byteData

def isBanana():
	return False #random.choice([True, False])

def isMushroom():
	return False

def userInputDirection():
	text = raw_input("direction: ")
	if text is None:
		return None
	else:
		if str(text) == "w":
			return kobukiDriveSpeeds(150,150)
		if str(text) == "a":
			return kobukiDriveSpeeds(50,100)
		if str(text) == "d":
			return kobukiDriveSpeeds(100,50)
		if str(text) == "s":
			return kobukiDriveSpeeds(-100,-100)
		return None

def main():
	print('hello')
	ser = serial.Serial("/dev/ttyO1",115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
	ser.close()
	ser.open()

	lastData = kobukiDriveSpeeds(100,100)

	#connecting to the Wiimote. This allows several attempts 
	# as first few fail. 
	print 'Press 1+2 on your Wiimote now...'
	wm = None 
	i=2 
	while not wm: 
	  try: 
	    wm=cwiid.Wiimote() 
	  except RuntimeError: 
	    if (i>10): 
	      quit() 
	      break 
	    print "Error opening wiimote connection" 
	    print "attempt " + str(i) 
	    i +=1 

	#set Wiimote to report button presses and accelerometer state 
	wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC 

	#turn on led to show connected 
	wm.led = 1

	while True:
		if ser.isOpen():
			print "Serial is open!"
			bananaSequence = isBanana()
			print bananaSequence
			if bananaSequence:
				start = time.time()
				while (time.time() - start) < 10:
					print time.time() - start
					print (time.time()- start) < 10
					turnRightData = kobukiDriveSpeeds(100,50)
					ser.write(toByteArray(turnRightData))
			mushroomSequence = isMushroom()
			print mushroomSequence
			if mushroomSequence:
				start = time.time()
				while (time.time() - start) < 10:
					print time.time() - start
					speedUpData = kobukiDriveSpeeds(250, 250)
					ser.write(toByteArray(speedUpData))
			else:
				#normalRunning
				userData = kobukiDriveSpeeds(150,150)
				if wm.state['buttons'] == 8:
					#forward
					turn_angle = (3.6 * wm.state['acc'][1]) - 360
					print turn_angle
					if turn_angle < 86:
						userData = kobukiDriveSpeeds(150-turn_angle,150)
					elif turn_angle > 104:
						userData = kobukiDriveSpeeds(150,150-(180-turn_angle))
					else:
						userData = kobukiDriveSpeeds(150,150)
				elif wm.state['buttons'] == 4:
					#backwards
					userData = kobukiDriveSpeeds(-150,-150)
				else:
					userData = kobukiDriveSpeeds(0,0)
					#do nothing
				ser.write(toByteArray(userData))
				lastData = userData
				time.sleep(0.1)
	ser.close()


if __name__=="__main__":
	main()
