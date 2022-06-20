
import sys
#import queue
import functools
import datetime
import serial
from tkinter import messagebox
from tkinter import filedialog
from subprocess import Popen
import subprocess
import numpy as np

import time
# import cv2


import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
from matplotlib.widgets import Slider

from skimage.external import tifffile as ski

import spincam
import ledserial


from ctypes import (
	c_short,
	c_int,
	c_char_p,
)
from time import sleep

from thorlabs_kinesis import benchtop_stepper_motor as bsm
from subprocess import Popen
import subprocess

"""
obj = Popen('Thorlabs.MotionControl.Kinesis.exe')
sleep(10)
Popen.kill(obj)
sleep(5)
"""

def main():
	#if __name__ == "__main__":
	serial_no = c_char_p(bytes("70960510", "utf-8"))
	channel = c_short(1)
	milliseconds = c_int(100)

	if bsm.TLI_BuildDeviceList() == 0:
		err = bsm.SBC_Open(serial_no, channel)
		if err == 0:
			#print("Starting polling ", bsm.SBC_StartPolling(serial_no, channel, milliseconds))
			#print("Clearing message queue ", bsm.SBC_ClearMessageQueue(serial_no, channel))
			sleep(0.2)

			stepSize = 4000000
			print("Setting step size ", bsm.SBC_SetMoveRelativeDistance(serial_no, channel, c_int(stepSize)))
			sleep(0.2)

			print(f"Moving step {stepSize}", bsm.SBC_MoveRelativeDistance(serial_no, channel))
			sleep(0.2)
			#initPos = int(bsm.SBC_GetPosition(serial_no, channel))
			#print(f"Position {initPos}", bsm.SBC_GetPosition(serial_no, channel))
			#print(f"To {stepSize+initPos}", bsm.SBC_GetPosition(serial_no, channel))
			
		else:
			print(f"Can't open. Error: {err}")
			
	return 0
	
if __name__ == '__main__':
    sys.exit(main())