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
import smbus
import Adafruit_I2C as I2C

COLOR_FILE = "color_mappings.txt"

TCA9548A_ADDRESS = 0x70
TCS34725_ADDRESS = 0x29
CONTROL_ADDRESS = 0x04

device = I2C.Adafruit_I2C(TCA9548A_ADDRESS, 1, True)

def tca_select(i):
	# Try writing an 8-bit select number
	device.write8(CONTROL_ADDRESS, 1<<i)

def read_light_sensor():
	# Two color sensors attached to mux port 2 and 6
	#right sensor
	tca_select(3)
	tcs3 = Adafruit_TCS34725.TCS34725(address=TCS34725_ADDRESS, busnum=1)
	#left sensor
	tca_select(5)
	tcs5 = Adafruit_TCS34725.TCS34725(address=TCS34725_ADDRESS, busnum=1)
	#middle sensor
	tca_select(7)
	tcs7 = Adafruit_TCS34725.TCS34725(address=TCS34725_ADDRESS, busnum=1)

	color_array = []

	# Read from first sensor
	tca_select(3)
	r1, g1, b1, _ = tcs3.get_raw_data()
	color_array.append((r1,g1,b1))

	print("I2C PORT 3 - R: {0}, G: {1}, B: {2}".format(r1, g1, b1))
	# time.sleep(0.5)

	# Read from second sensor
	tca_select(5)
	r2, g2, b2, _ = tcs5.get_raw_data()
	color_array.append((r2,g2,b2))

	print("I2C PORT 5 - R: {0}, G: {1}, B: {2}".format(r2, g2, b2))
	# time.sleep(0.5)

	# Read from second sensor
	tca_select(7)
	r3, g3, b3, _ = tcs7.get_raw_data()
	color_array.append((r3,g3,b3))

	print("I2C PORT 7 - R: {0}, G: {1}, B: {2}".format(r3, g3, b3))
	# time.sleep(0.5)

	return color_array

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
    for i in range(len(colors)/2):
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

def isBanana(colorsRead):
	# r, g, b, _ = Adafruit_TCS34725.TCS34725(address=0x29, busnum=1).get_raw_data()
	# if detect a yellow tape
	for sensor in colorsRead:
		r,g,b = sensor[0],sensor[1],sensor[2]
		if ((27 < r and r < 35) and (g < 25) and (10 < b and b < 15)):
			print("isBanana: " + str(True))
			return True
	return False

def isMushroom(colorsRead):
	# r, g, b, _ = Adafruit_TCS34725.TCS34725(address=0x29, busnum=1).get_raw_data()
	# if detect a blue tape
	for sensor in colorsRead:
		r,g,b = sensor[0],sensor[1],sensor[2]
		print("DIFFERENT MUSHROOM VALUES" + str(sensor))
		if ((r <= 10) and (g > 10) and (b > 13)):
			print("MUSHROOM VALUES" + str(sensor))
			print("isMushroom: " + str(True))
			return True
	return False

def isBorder(colorsRead):
	# r, g, b, _ = Adafruit_TCS34725.TCS34725(address=0x29, busnum=1).get_raw_data()
	#if detects a green tape
	for sensor in colorsRead:
		r,g,b = sensor[0],sensor[1],sensor[2]
		if ((r >= 27) and (g < 15) and (b < 10)):
			print("isBorder: " + str(True))
			return True
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

	numBananas = 1
	bananaTimestamp = 0
	mushroomSpeedupStart = 0
	maxSpeed = 200

	while True:
		if ser.isOpen():

			# print "Serial is open!"
			# print "Color sensor reading: "
			# r, g, b, _ = Adafruit_TCS34725.TCS34725(address=0x29, busnum=1).get_raw_data()
			# print "red: " + str(r)
			# print "green: " + str(g)
			# print "blue: " + str(b)
			# print "RBG: " + str(math.sqrt((r*r)+(g*g)+(b*b)))
			if (mushroomSpeedupStart !=0) and ((time.time() - mushroomSpeedupStart) > 10):
				maxSpeed = 200
				mushroomSpeedupStart = 0
			colorsRead = read_light_sensor()

			bananaSequence = isBanana(colorsRead)
			print bananaSequence
			if bananaSequence and ((time.time() - bananaTimestamp)>30):
				start = time.time()
				numBananas = 0
				bananaTimestamp = time.time()
				while (time.time() - start) < 10:
					print time.time() - start
					print (time.time()- start) < 10
					wm.rumble = True
					turnRightData = kobukiDriveSpeeds(200,-200)
					ser.write(toByteArray(turnRightData))
					time.sleep(0.1)
				wm.rumble = False

			mushroomSequence = isMushroom(colorsRead)
			print mushroomSequence
			if mushroomSequence:
				mushroomSpeedupStart = time.time()
				maxSpeed = 300
				# start = time.time()
				# while (time.time() - start) < 10:
				# 	print time.time() - start
				# 	speedUpData = kobukiDriveSpeeds(250, 250)
				# 	ser.write(toByteArray(speedUpData))
				# 	time.sleep(0.1)

			borderSequence = isBorder(colorsRead)
			print borderSequence
			if borderSequence:
				start = time.time()
				while (time.time() - start) < 2:
					print time.time() - start
					wm.rumble = True
					reverseData = kobukiDriveSpeeds(-200, -200)
					ser.write(toByteArray(reverseData))
					time.sleep(0.1)
				wm.rumble = False

			else:
				#normalRunning
				userData = kobukiDriveSpeeds(maxSpeed,maxSpeed)
				if wm.state['buttons'] == 8:
					#forward
					turn_angle = (3.6 * wm.state['acc'][1]) - 360
					print turn_angle
					if turn_angle < 86:
						userData = kobukiDriveSpeeds(maxSpeed-turn_angle,maxSpeed)
					elif turn_angle > 104:
						userData = kobukiDriveSpeeds(maxSpeed,maxSpeed-(180-turn_angle))
					else:
						userData = kobukiDriveSpeeds(maxSpeed,maxSpeed)
				elif wm.state['buttons'] == 4:
					#backwards
					userData = kobukiDriveSpeeds(-1*maxSpeed,-1*maxSpeed)
				else:
					userData = kobukiDriveSpeeds(0,0)
					#do nothing
				ser.write(toByteArray(userData))
				lastData = userData
				time.sleep(0.1)
	ser.close()


if __name__=="__main__":
	main()



