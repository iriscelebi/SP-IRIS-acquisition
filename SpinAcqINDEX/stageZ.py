from ctypes import (
	c_short,
	c_int,
	c_char_p,
)
from time import sleep

import kcube_piezo as pcc
from time import sleep
from subprocess import Popen
import subprocess


global serial_no

global defaultPos

global milliseconds 
defaultPos = 0

serial_no = c_char_p(bytes("29502600", "utf-8"))	

milliseconds = c_int(100)

def __initialize_stages():
	
	global serial_no
	
	global defaultPos

	global milliseconds 
	
	#obj = Popen('Thorlabs.MotionControl.Kinesis.exe')
	#sleep(15)
	#Popen.kill(obj)
	#sleep(5)
	 
	
	
	print('Homing Z stage')
	__home()
	
	print('pos is', pcc.PCC_GetPosition(serial_no))
	
	print('Homing is finished...')

	print('Going to default positions...')
		
	__setVolt(defaultPos)
	

	
	print('Stages are ready...')

	
	
	
def __setVolt(voltage):
	
	global serial_no
	global milliseconds 
	
	


	if pcc.TLI_BuildDeviceList() == 0:
		err = pcc.PCC_Open(serial_no)
		if err == 0:
			#print("Starting polling ", bsm.SBC_StartPolling(serial_no, channel, milliseconds))
			#print("Clearing message queue ", bsm.SBC_ClearMessageQueue(serial_no, channel))
			sleep(0.2)

			print(f"Setting voltage {voltage}", pcc.PCC_SetOutputVoltage(serial_no, c_short(round(voltage/75.0*32767))))
			sleep(1)
			
			
		else:
			print(f"Can't open. Error: {err}")
		
	
	

	
def __home():

	global serial_no
	global milliseconds 
	

	if pcc.TLI_BuildDeviceList() == 0:
		if pcc.PCC_Open(serial_no) == 0:
			
			sleep(1.0)
			
			err = pcc.PCC_SetZero(serial_no)
			
			if err == False:
				
				print(f"Can't home. Err: {err}")
			
				

			pcc.PCC_Close(serial_no)
		else:
			print("Can't open")
	else:
		print("Can't build device list.")	
	
