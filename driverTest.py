import Adafruit_BBIO.UART as UART
import serial

def checkSum(data, length):
	cs = 0x00
	for i in range(2,length):
		cs = cs^data[i]
	return cs

def split_int16(data, LSB):
	if LSB:
		return data & 0x000FFFF
	else:
		return (data & 0xFFF0000) >> 16


def kobukiDrive(radius, speed):
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

UART.setup("UART1")
 
ser = serial.Serial("/dev/ttyO1",115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
ser.close()
ser.open()
while True:
	if ser.isOpen():
		print "Serial is open!"
		data = kobukiDrive(0,150)
		print data
		print str(data)
		ser.write(bytearray(data))
ser.close()
