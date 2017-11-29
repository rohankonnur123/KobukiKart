#!/usr/bin/python

import Adafruit_BBIO.UART as UART
import serial
import time
import array
import struct
import random
import cwiid 

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