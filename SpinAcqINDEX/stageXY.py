from ctypes import (
	c_short,
	c_int,
	c_char_p,
)
from time import sleep

from thorlabs_kinesis import benchtop_stepper_motor as bsm
from time import sleep
from subprocess import Popen
import subprocess


global serial_no
global channelOne
global channelTwo
global defaultPos1 
global defaultPos2
global milliseconds 
defaultPos1 = 2000000
defaultPos2 = 3500000
serial_no = c_char_p(bytes("70116764", "utf-8")) ##########CHANGE SERIAL NUM HERE	
channelOne = c_short(1)
channelTwo = c_short(2)
milliseconds = c_int(100)






def __initialize_stages():
	
	global serial_no
	global channelOne
	global channelTwo
	global defaultPos1 
	global defaultPos2
	global milliseconds 
	
	obj = Popen('Thorlabs.MotionControl.Kinesis.exe')
	sleep(15)
	Popen.kill(obj)
	sleep(5)
	 
	print('Stages are initialized...')
	
	print('Homing channel one')
	__home(1)
	print('Homing channel two')	
	__home(2)	
	
	print('Homing is finished...')

	print('Going to default positions...')
		
	__moveAbsolute(1,defaultPos1)
	__moveAbsolute(2,defaultPos2)

	
	print('Stages are ready...')

	
	
	
def __moveRelative(channel, stepSize):
	
	global serial_no
	global milliseconds 
	channel = c_short(channel)
	step = int(stepSize*0.8192) 


	if bsm.TLI_BuildDeviceList() == 0:
		err = bsm.SBC_Open(serial_no, channel)
		if err == 0:
			#print("Starting polling ", bsm.SBC_StartPolling(serial_no, channel, milliseconds))
			#print("Clearing message queue ", bsm.SBC_ClearMessageQueue(serial_no, channel))
			sleep(0.2)

			
			bsm.SBC_SetMoveRelativeDistance(serial_no, channel, c_int(step))
			sleep(0.2)

			print(f"Moving step {stepSize}", bsm.SBC_MoveRelativeDistance(serial_no, channel))
			sleep(1)
			
			
		else:
			print(f"Can't open. Error: {err}")
		
	
	
	
def __moveAbsolute(channel, move_to):	
	
	global serial_no
	global milliseconds 
	channel = c_short(channel)
	move = int(move_to*0.8192) 
	
	if bsm.TLI_BuildDeviceList() == 0:
		err = bsm.SBC_Open(serial_no, channel)
		if err == 0:
			bsm.SBC_StartPolling(serial_no, channel, milliseconds)
			bsm.SBC_ClearMessageQueue(serial_no, channel)
			sleep(0.2)

			
			bsm.SBC_SetMoveAbsolutePosition(serial_no, channel, c_int(move))
			sleep(0.2)

			print(f"Moving to {move_to}", bsm.SBC_MoveAbsolute(serial_no, channel))
			sleep(0.2)
			pos = int(bsm.SBC_GetPosition(serial_no, channel))
			sleep(0.2)
			
			while not pos == move:
				sleep(0.2)
				pos = int(bsm.SBC_GetPosition(serial_no, channel))
			
				print(f"Current pos: {pos}")

			bsm.SBC_StopPolling(serial_no, channel)
			bsm.SBC_Close(serial_no, channel)
		else:
			print(f"Can't open. Error: {err}")
	
	
def __home(channel):

	global serial_no
	global milliseconds 
	channel = c_short(channel)

	if bsm.TLI_BuildDeviceList() == 0:
		if bsm.SBC_Open(serial_no) == 0:
			sleep(1.0)
			bsm.SBC_StartPolling(serial_no, channel, milliseconds)
			bsm.SBC_ClearMessageQueue(serial_no, channel)
			sleep(1.0)

			err = bsm.SBC_Home(serial_no, channel)
			sleep(1.0)
			if err == 0:
				while True:
					current_pos = int(bsm.SBC_GetPosition(serial_no, channel))
					if current_pos == 0:
						print("At home.")
						break
					
						

					sleep(1.0)
			else:
				print(f"Can't home. Err: {err}")

			bsm.SBC_StopPolling(serial_no, channel)
			bsm.SBC_Close(serial_no)
		else:
			print("Can't open")
	else:
		print("Can't build device list.")	
	
	
def __whereAmI(channel):	
	
	global serial_no
	global milliseconds 
	channel = c_short(channel)
	
	
	if bsm.TLI_BuildDeviceList() == 0:
		err = bsm.SBC_Open(serial_no, channel)
		if err == 0:
			bsm.SBC_StartPolling(serial_no, channel, milliseconds)
			bsm.SBC_ClearMessageQueue(serial_no, channel)
			sleep(0.2)

			pos = int(bsm.SBC_GetPosition(serial_no, channel))/0.8192

			print(f"Current pos: {pos}")

			bsm.SBC_StopPolling(serial_no, channel)
			bsm.SBC_Close(serial_no, channel)
		else:
			print(f"Can't open. Error: {err}")
	