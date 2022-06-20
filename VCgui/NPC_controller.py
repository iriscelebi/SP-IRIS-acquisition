

#
##
###
# 1OR = enable, 1RS  = reset, 1ID? = ask ID, 1PA = move absolute, 1PA? = ask absolute, 1VA = slew rate
# Default slew rate = 6e-3, this takes 0.17 seconds for 1V

import serial
import atexit
import os
import time

__SERIAL = serial.Serial()

def __destructor():
	global __SERIAL
	command = '1RS'
	
	__SERIAL.write(command.encode())
	__SERIAL.write((b'\x0a'))
	print('Closing Connection')

	__close()
    
atexit.register(__destructor)

def connect(portno):
	global __SERIAL
	__connect(portno)
	if __SERIAL.is_open:
		command = '1OR'
		__SERIAL.write(command.encode())
		__SERIAL.write((b'\x0a'))
		print('connected')
		
def __connect(portno):
	global __SERIAL
	__SERIAL.baudrate = 57600
	__SERIAL.port = 'COM'+str(portno)
	__SERIAL.open()
    
def __reset():

	global __SERIAL
	command = '1RS'
	__SERIAL.write(command.encode())
	__SERIAL.write((b'\x0a'))
	time.sleep(1)
	command = '1OR'
	__SERIAL.write(command.encode())
	__SERIAL.write((b'\x0a'))

	
	

def close():
	global __SERIAL
	return __close()
def __close():
	global __SERIAL
	__SERIAL.close()
	
def moveAbsolute(moveTo, current):
	global __SERIAL
	
	#difference = abs(current - moveTo)
	command = '1PA'+str(moveTo)

	__SERIAL.write(command.encode())
	__SERIAL.write((b'\x0a'))
	
	#time.sleep(0.03*difference)
	

	
def getPosition(_=None):
	global __SERIAL
	command = '1PA?'
	__SERIAL.write(command.encode())
	__SERIAL.write((b'\x0a'))
	read_data = __SERIAL.readline().decode('ascii')
	print("Position : " + read_data)
	
	

def setSlewRateHigh(_=None):
	global __SERIAL
	#rate = 0.001
	command = '1VA6e-2'
	__SERIAL.write(command.encode())
	__SERIAL.write((b'\x0a'))
	
def setSlewRateLow(_=None):
	global __SERIAL
	#rate = 0.001
	command = '1VA6e-1'
	__SERIAL.write(command.encode())
	__SERIAL.write((b'\x0a'))
	
	
def getSlewRate(_=None):
	global __SERIAL
	command = '1VA?'
	__SERIAL.write(command.encode())
	__SERIAL.write((b'\x0a'))
	read_data = __SERIAL.readline().decode('ascii')
	print("Slew Rate : " + read_data)
	
	

