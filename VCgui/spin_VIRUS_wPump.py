
import sys
import queue
import functools
import datetime
import serial
from tkinter import messagebox
from tkinter import filedialog
from subprocess import Popen
import subprocess
import numpy as np
import scipy.io as sio

import NPC_controller as stageZ #objective scanner
import time
import os

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
from matplotlib.widgets import Slider
from matplotlib.text import Annotation
from matplotlib.widgets import RadioButtons

#from skimage.external import tifffile as ski
import imageio


import spincam

import ledserial_proto as ledserial
import pumpSerial as Pump



# Camera Properties Min/Max
__FPS_MIN = 1
__FPS_MAX = 30
__GAIN_MIN = 0
__GAIN_MAX = 47  # Units are dB
__EXPOSURE_MIN = 0.006  # microseconds
__EXPOSURE_MAX = 200000  # microseconds seconds

# GUI params
#__QUEUE = queue.Queue()
__STREAM = False
__IMSHOW_DICT = {'imshow': None, 'imshow_size': None, 'max_val': None}
__HIST_DICT = {'bar': None, 'max_val': None}
__GUI_DICT = None
__STAGE_DICT = None


__Z_STEP = 1
__Z_STEP_PLUS = 15

__STEP_MIN = 1
__STEP_MAX = 100

__Z_POS = 50

__COM_PORT = 11
__COM_PORT_NPC = 8
__COM_PORT_PUMP = 5

__PUMP_SPEED = 50
__SYRINGEPOSITION = 0
__VOLUME = 0
__VALVE = 'PBS'


def __find_and_init_cam(_=None):
	# Finds and initializes camera
	global __EXPOSURE_MAX
	global __EXPOSURE_MIN
	global __FPS_MAX
	global __FPS_MIN

	print('Connecting camera...')
	spincam.find_cam('test')

	spincam.init_cam()
	__EXPOSURE_MIN = spincam.get_exp_min()
	__EXPOSURE_MAX = spincam.get_exp_max()
	__FPS_MIN = spincam.get_fps_min()
	__FPS_MAX = spincam.get_fps_max()
	spincam.disable_auto_exp()
	spincam.disable_auto_gain()
	spincam.disable_auto_frame()
	__init_gain(0)
	spincam.set_video_mode('7')
	#ledserial.connect(__COM_PORT)
	
def __init_gain(gain):
	# gain text callback

	# Set gain for camera
	print('Initializing Gain to ' + str(gain))
	spincam.set_gain(gain)


def __choose_directory(_=None):
	dir = filedialog.askdirectory()
	__GUI_DICT['directory_text'].set_val(dir)

def __open_preview(_=None):
	#Popen('SpinView_WPF.exe')
	os.startfile("C:\Program Files\Micro-Manager-2.0gamma\ImageJ.exe")    



def __start_stream(_=None):
	# Starts stream of cameras
	global __STREAM

	# Ensure aren't already streaming
	if not __STREAM:
		print('Starting stream...')

		# Set buffer to newest only
		spincam.cam_node_cmd('TLStream.StreamBufferHandlingMode',
							 'SetValue',
							 'RW',
							 'PySpin.StreamBufferHandlingMode_NewestOnly')

		# Set acquisition mode to continuous
		spincam.cam_node_cmd('AcquisitionMode',
							 'SetValue',
							 'RW',
							 'PySpin.AcquisitionMode_Continuous')

		# Start acquisition
		spincam.start_acquisition()

		# Enable stream
		__STREAM = True


def __stop_stream(_=None):
	# Stops stream of cameras
	global __STREAM

	# Make sure they're streaming
	if __STREAM:
		print('Stopping stream...')

		# Stop acquisition
		spincam.end_acquisition()
		# End stream
		__STREAM = False


#############################################################
#############################################################
def resetNPC(_=None):
	stageZ.__reset()
	global __Z_POS
	__Z_POS = 0
	__update_pos_z()


def __go_defocus_up(_=None):
	global __Z_POS
	current = __Z_POS
	
	__Z_POS = min( __Z_POS + __Z_STEP,130)
	stageZ.moveAbsolute(__Z_POS, current)

	#stageZ.getPosition()
	
	__update_pos_z()

def __go_defocus_up_plus(_=None):
	global __Z_POS
	current = __Z_POS
	
	__Z_POS = min(  __Z_POS + __Z_STEP_PLUS,130)
	stageZ.moveAbsolute(__Z_POS, current)

	#stageZ.getPosition()
	__update_pos_z()

def __go_defocus_down(_=None):
	global __Z_POS
	current = __Z_POS
	
	__Z_POS = max( __Z_POS - __Z_STEP,0)
	stageZ.moveAbsolute(__Z_POS, current)

	#stageZ.getPosition()
	__update_pos_z()
	
def __go_defocus_down_plus(_=None):
	global __Z_POS
	current = __Z_POS
		
	__Z_POS = max( __Z_POS - __Z_STEP_PLUS,0)
	stageZ.moveAbsolute(__Z_POS, current)

	#stageZ.getPosition()
	__update_pos_z()

#############################################################
#############################################################

def __update_pos_z(_=None):
	global __Z_POS
	# updates the current postion
	stage_dict = __GUI_DICT
	pos = 'z_pos_but'
	current = __Z_POS
	stage_dict[pos].eventson = False
	stage_dict[pos].set_val(current)
	stage_dict[pos].eventson = True



def __z_step(_=None):

	global __Z_STEP
	# z_step text callback
	stage_dict = __GUI_DICT
	z_step = stage_dict['z_step_text1'].text
	if not z_step:
		return

	__Z_STEP = float(z_step)  # convert mm to um

	# Update slider to match text
	stage_dict['z_step_text1'].eventson = False
	stage_dict['z_step_text1'].set_val(__Z_STEP)
	stage_dict['z_step_text1'].eventson = True

	# 
	#__Z_STEP = min(__STEP_MAX, __Z_STEP)
	#__Z_STEP = max(__STEP_MIN, __Z_STEP)

	print('defocus step is set to ' + str(__Z_STEP) + ' um')
	
def __z_step_plus(_=None):
	global __Z_STEP_PLUS
	# z_step text callback
	stage_dict = __GUI_DICT
	z_step = stage_dict['z_step_text2'].text
	if not z_step:
		return

	__Z_STEP_PLUS = float(z_step)  # convert mm to um

	# Update slider to match text
	stage_dict['z_step_text2'].eventson = False
	stage_dict['z_step_text2'].set_val(__Z_STEP_PLUS)
	stage_dict['z_step_text2'].eventson = True

	# Set Z_STEp for camera
	#__Z_STEP_PLUS = min(__STEP_MAX, __Z_STEP_PLUS)
	#__Z_STEP_PLUS = max(__STEP_MIN, __Z_STEP_PLUS)

	print('Defocus large step is set to ' + str(__Z_STEP_PLUS) + ' um')

def __number_defocus(_=None):
	# fps text callback
	stage_dict = __GUI_DICT
	num_z_step = stage_dict['step_num_text'].text

	if not num_z_step:
		return
	defocus_interval = (2 * float(num_z_step)) * float(__Z_STEP)

	# Update total defocus to match text
	stage_dict['z_interval_text'].eventson = False
	stage_dict['z_interval_text'].set_val(int(defocus_interval))
	stage_dict['z_interval_text'].eventson = True

	# Update total defocus to match text
	stage_dict['step_num_text'].eventson = False
	stage_dict['step_num_text'].set_val(num_z_step)
	stage_dict['step_num_text'].eventson = True

	# Set fps for camera

	# def_radius = min(__STEP_MAX, def_radius)
	# def_radius = max(__STEP_MIN, def_radius)
	print('defocus radius is set to ' + str(defocus_interval) + ' um')

	
def __number_acquire(_=None): ###########################################
	# fps text callback
	stage_dict = __GUI_DICT
	
	number_acquire = stage_dict['num_images_text'].text ##
	number_acquire = int(number_acquire)

	# Update total defocus to match text
	stage_dict['num_images_text'].eventson = False
	stage_dict['num_images_text'].set_val(number_acquire)
	stage_dict['num_images_text'].eventson = True


	print('# to Acquire is set to' + str(number_acquire))


def __number_average(_=None):
	# fps text callback
	stage_dict = __GUI_DICT
	
	number_average = stage_dict['avg_images_text'].text
	number_average = int(number_average)

	# Update total defocus to match text
	stage_dict['avg_images_text'].eventson = False
	stage_dict['avg_images_text'].set_val(number_average)
	stage_dict['avg_images_text'].eventson = True

	print('# to Average is set to' + str(number_average))
		

def __defocus_acquisition(_=None):
	if (__STREAM):
		__stop_stream()
	time.sleep(0.1)
	__start_stream()
	time.sleep(0.1)
	global __Z_POS
	stage_dict = __GUI_DICT
	num_z_step = int(stage_dict['step_num_text'].text)
	num_images = int(__GUI_DICT['num_images_text'].text)
	time_int = float(stage_dict['time_btwn_z_text'].text)

	__Z_POS_orig = __Z_POS
	# file name
	name_format = __GUI_DICT['name_format_text'].text
	directory = __GUI_DICT['directory_text'].text
	img_name = name_format.replace('{date}', str(datetime.date.today()))

	if directory:
		directory = directory + '\\'

	img_main = directory + img_name.replace(' ', '_').replace('.', '_').replace(':', '')
	img_name = img_main
	print('Experiment start: ' + str(datetime.datetime.now()))
	
	# initialize z position for defocus acquisition
	rel_z = (num_z_step + 1) * __Z_STEP
	stageZ.moveAbsolute(__Z_POS-rel_z, __Z_POS)
	time.sleep(5)
	__Z_POS = __Z_POS - rel_z
	__update_pos_z()
	time.sleep(1)
	
	foo = np.zeros((2 * num_z_step + 1,4600,5320),dtype=np.float32)
	print('Relative z position %2.2f' % -rel_z)
	for ii in range(num_images):
		print('Defocus acquisition %05d' %ii + 'is started... ')
		for jj in range(1, 2 * num_z_step + 2):
			print('Time point %05d' % ii + '  Relative z position %2.2f  um' % (-rel_z + (jj) * __Z_STEP))

			
			stageZ.moveAbsolute(__Z_POS+__Z_STEP, __Z_POS)
			
			__Z_POS = __Z_POS + __Z_STEP
			__update_pos_z()
			data = __acquire_images()
			print(f"Current position {__Z_POS}")

			
			foo[jj-1,:,:] = data
			
			#file_name = img_name + '_time_%06d' % ii + '_z_%03d' % jj + '.tif'
			#ski.imsave(file_name, foo, compress = 0)
			
		print('Defocus acquisition %05d' %ii  + 'is finished')
		
		foo = foo.astype(np.uint16)
		file_name = img_name + '_time_%03d_' % ii + '%d' % __Z_STEP +'umSteps' +'.tif'
		file_name_std = img_name + '_time_%03d_' % ii + '%d' % __Z_STEP +'umSteps_std' +'.csv'
		#ski.imsave(file_name, np.stack(foo, axis = 0) , compress = 0)
		imageio.mimwrite(file_name, foo)
        
		np.savetxt(file_name_std, (np.std(foo,axis=0)), delimiter=",", fmt='%10.5f')
		
		#__save_def_images(img_name, foo,ii,'imCube')
 
		foo = np.zeros((2 * num_z_step + 1,4600,5320),dtype=np.float32)
		stageZ.moveAbsolute(__Z_POS_orig, __Z_POS)

		time.sleep(time_int)	# pause for certain time
		print('ckeck point 0')        
		__Z_POS = __Z_POS_orig
		__update_pos_z()


	print('ckeck point 1')
	#time.sleep(time_int)
	#stageZ.moveAbsolute(__Z_POS_orig, __Z_POS)
	print('ckeck point 2')
	#time.sleep(time_int)	# pause for certain time
	__Z_POS = __Z_POS_orig
	__update_pos_z()
	__stop_stream()
	
def __save_def_images(file_name, data, time,state):
    num_to_avg = int(__GUI_DICT['avg_images_text'].text)
    #
	
    #np.savetxt(file_name, data, delimiter=",")
    file_name1 =  file_name + '_' + state + '_step_size_%04d_nm' % __Z_STEP + '_avg_%05d_frames' % num_to_avg + '_time_%06d' % time + '.mat'
    sio.savemat(file_name1, {state:data})
    #file_name2 = file_name + '_' + type + '_time_%06d' % time + '.csv'
    #np.savetxt(file_name2, data, delimiter=",")
    
    #ski.imsave(file_name, data.astype(np.uint16), compress=0)  
def __time_int_def(_=None):
	# sets the time interval between z-stack frames
	stage_dict = __GUI_DICT
	time_int = stage_dict['time_btwn_z_text'].text

	if not time_int:
		return

	# Update total defocus to match text
	stage_dict['time_btwn_z_text'].eventson = False
	stage_dict['time_btwn_z_text'].set_val(float(time_int))
	stage_dict['time_btwn_z_text'].eventson = True

	print('Time interval between successive z-stacks is set to ' + str(float(time_int)) + ' sec')




def __ledON(_=None): #you can turn on two for both LED sets

	print('LED ON')

	ledserial.send(bytes.fromhex('0c64')) 
	
def __ledOFF(_=None):

	print('LED OFF')
	ledserial.send(bytes.fromhex('0b00')) #red
	ledserial.send(bytes.fromhex('0c00')) #green
	ledserial.send(bytes.fromhex('0d00')) #blue
	ledserial.send(bytes.fromhex('0e00')) #yellow



def __fix_name(_=None):
	# file name
	name_format = __GUI_DICT['name_format_text'].text
	directory = __GUI_DICT['directory_text'].text
	if directory:
		directory = directory + '\\'
	img_name = name_format.replace('{date}', str(datetime.date.today()))
	img_main = directory + img_name.replace(' ', '_').replace('.', '_').replace(':', '')
	return img_main

def __acquire_no_z(_=None):
	if (__STREAM):
		__stop_stream()
	time.sleep(0.1)
	__start_stream()
	time.sleep(0.1)
	global __GUI_DICT

	num_to_avg = int(__GUI_DICT['avg_images_text'].text)
	img_name=__fix_name()
	image_dict = spincam.get_image_and_avg(num_to_avg)
	print('Starting save ' + img_name)
	# Make sure images are complete
	if 'data' in image_dict:
		data=image_dict['data'].astype(np.uint16)
		__save_images(img_name, data,0,0)
		print('Finished Acquiring ' + img_name)
	__stop_stream()

def __acquire_images(_=None):
	global __IMSHOW_DICT
	global __HIST_DICT
	
	if not __STREAM:
		raise RuntimeError('Stream has not been started yet! Please start it first.')
	# number of defocus
	stage_dict = __GUI_DICT
	num_z_step = int(stage_dict['step_num_text'].text)
	# Get name format, counter, and number of images

	
	num_to_avg = int(__GUI_DICT['avg_images_text'].text)
	#time_btwn_frames = int(__GUI_DICT['time_images_text'].text)
	#frmrate = int(spincam.get_frame_rate())

	file_number = 1

	#if (time_btwn_frames != 0):
	#	num_to_avg = int(frmrate * time_btwn_frames)

	image_dict = spincam.get_image_and_avg(num_to_avg)

	# Make sure images are complete
	if 'data' in image_dict:
		return image_dict['data'].astype(np.uint16)


def __save_images(file_name, data, time, z):
	file_name = file_name + '_time_%06d' % time + '_z_%03d' % z + '.tiff'
	#ski.imsave(file_name, data, compress=0)
	imageio.mimwrite(file_name, data)
	
def __update_valve(label):

	global __VALVE
	__VALVE = label

    
def __update_speed(_=None):

	global __PUMP_SPEED

	stage_dict = __GUI_DICT
	__PUMP_SPEED = stage_dict['speed_text'].text
	if not __PUMP_SPEED:
		return

	__PUMP_SPEED = max( float(__PUMP_SPEED),50)
    
    
	stage_dict['speed_text'].eventson = False
	stage_dict['speed_text'].set_val(__PUMP_SPEED)
	stage_dict['speed_text'].eventson = True
	
	__update_duration() 

def __update_syringePosition(_=None):

	global __SYRINGEPOSITION

	stage_dict = __GUI_DICT
	__SYRINGEPOSITION = stage_dict['syringePosition_text'].text
	if not __SYRINGEPOSITION:
		return


	stage_dict['syringePosition_text'].eventson = False
	stage_dict['syringePosition_text'].set_val(__SYRINGEPOSITION)
	stage_dict['syringePosition_text'].eventson = True
	
	__update_duration()   

def __update_duration(_=None):


	stage_dict = __GUI_DICT

	__SYRINGEPOSITION = stage_dict['syringePosition_text'].text
	__SYRINGEPOSITION = float(__SYRINGEPOSITION)
	__PUMP_SPEED = stage_dict['speed_text'].text
	__PUMP_SPEED = float(__PUMP_SPEED)
	_DURATION = (__SYRINGEPOSITION*2500/100)/__PUMP_SPEED
    
	stage_dict['duration_text'].eventson = False
	stage_dict['duration_text'].set_val(_DURATION)
	stage_dict['duration_text'].eventson = True
	
def __run_syringe(_=None):    


	print('running syringe')


def __initialize_pump(_=None):
	#Popen('PSD SDK')
	Pump.__initialize()
    
def __run_valve(_=None):

	pos = __VALVE
	if pos == 'PBS' :
		Pump.send('/1h27225R')
	elif pos == 'Sample' :
		Pump.send('/1h27090R')
	elif pos == 'Chip' :
		Pump.send('/1h27135R')
    
    

def __spincam_gui():

	# Get figure

	fig = plt.figure(1)
    
	
    # Set position params
	padding = 0.01
	options_height = 0.02
	num_options = 6

	# Creates stage controls
	options_height = 0.02
	padding = 0.01
	but_width = options_height * 4
	but_height = options_height * 5

	start_stream_button_pos = [0.1,
							   1 - 2 * padding - but_height,
							   2*but_width,
							   but_height]
	start_stream_button_axes = fig.add_axes(start_stream_button_pos)
	start_stream_button = Button(start_stream_button_axes, 'Open uManager')
	start_stream_button.label.set_fontsize(8)


    


	# Set callback
	start_stream_button.on_clicked(__open_preview)
	
	####################### led

	led_on_button_pos = [0.38 - but_width,
					   1 - 2 * padding - but_height,
					   but_width,
					   but_height]
	led_on_button_axes1 = fig.add_axes(led_on_button_pos)
	led_on_button = Button(led_on_button_axes1, 'LED ON')
	led_on_button.label.set_fontsize(8)
	led_on_button.on_clicked(__ledON)


	led_off_button_pos = [led_on_button_pos[0] + but_width,
					    led_on_button_pos[1],
					   but_width,
					   but_height]
	led_off_axes = fig.add_axes(led_off_button_pos)
	led_off_button = Button(led_off_axes, 'LED OFF')
	led_off_button.label.set_fontsize(8)
	led_off_button.on_clicked(__ledOFF)
	
	#######################
    
	resetNPC_button_pos = [0.4 + 1.5*but_width,
					   1 - 2 * padding - but_height,
					   but_width,
					   but_height]
	resetNPC_button_axes = fig.add_axes(resetNPC_button_pos)
	resetNPC_button = Button(resetNPC_button_axes, 'RST NPC')
	resetNPC_button.label.set_fontsize(8)
	resetNPC_button.on_clicked(resetNPC)
    
    ###############################

    ###############################
	# current position
	z_pos_but_pos = [0.32 - options_height,
					   1 - 2 * padding - 2*but_height,
					   0.1 - 2 * padding,
					   options_height * 2]
	z_pos_but_axes = fig.add_axes(z_pos_but_pos)
	z_pos_but = TextBox(z_pos_but_axes, 'current z position ')
	z_pos_but.label.set_fontsize(10)
	z_pos_but.set_val(__Z_POS)

	z_pos_but.on_submit(__update_pos_z)

	
	####################### Set z step size
	z_step_text_pos1 = [0.32 - options_height,
					   z_pos_but_pos[1] - 2 * padding - options_height * 2,
					   0.1 - 2 * padding,
					   options_height * 2]
	z_step_text_axes1 = fig.add_axes(z_step_text_pos1)
	z_step_text1 = TextBox(z_step_text_axes1, '+ z step size (um) ')
	z_step_text1.label.set_fontsize(10)
	z_step_text1.set_val(__Z_STEP)
	z_step_text1.on_submit(__z_step)
	
	z_step_text_pos2 = [z_step_text_pos1[0],
					   z_step_text_pos1[1] - 2 * padding - options_height * 2,
					   0.1 - 2 * padding,
					   options_height * 2]
	z_step_text_axes2 = fig.add_axes(z_step_text_pos2)
	z_step_text2 = TextBox(z_step_text_axes2, '++ z step size (um) ')
	z_step_text2.label.set_fontsize(10)
	z_step_text2.set_val(__Z_STEP_PLUS)
	z_step_text2.on_submit(__z_step_plus)

	####################### num of steps
	step_num_text_pos = [z_step_text_pos1[0],
						 z_step_text_pos2[1] - 2 * padding - options_height * 2,
						 0.1 - 2 * padding,
						 options_height * 2]
	step_num_text_axes = fig.add_axes(step_num_text_pos)
	step_num_text = TextBox(step_num_text_axes, '# of steps (radius) ')
	step_num_text.label.set_fontsize(10)
	step_num_text.set_val(15)
	step_num_text.on_submit(__number_defocus)

	####################### z interval
	z_interval_text_pos = [z_step_text_pos1[0],
						   step_num_text_pos[1] - 2 * padding - options_height * 2,
						   0.1 - 2 * padding,
						   options_height * 2]
	z_interval_text_axes = fig.add_axes(z_interval_text_pos)
	z_interval_text = TextBox(z_interval_text_axes, 'defocus interval (um) ')
	z_interval_text.label.set_fontsize(10)
	z_interval_text.set_val(1)
	#z_interval_text.on_submit(__test)
	

	####################### time btwn z stacks
	time_btwn_z_text_pos = [z_step_text_pos1[0],
						   z_interval_text_pos[1] - 2 * padding - options_height * 2,
						   0.1 - 2 * padding,
						   options_height * 2]
	time_btwn_z_text_axes = fig.add_axes(time_btwn_z_text_pos)
	time_btwn_z_text = TextBox(time_btwn_z_text_axes, 'z-stack period (s) ')
	time_btwn_z_text.label.set_fontsize(10)
	time_btwn_z_text.set_val(1)
	time_btwn_z_text.on_submit(__time_int_def)
	
	####################### z control

	z_up_button_pos1 = [0.4 + 0.5*but_width,
					   z_step_text_pos2[1],
					   but_width,
					   but_height]
	z_up_button_axes1 = fig.add_axes(z_up_button_pos1)
	z_up_button1 = Button(z_up_button_axes1, '+z')
	z_up_button1.label.set_fontsize(10)
	
	z_up_button1.on_clicked(__go_defocus_up)



	z_up_button_pos2 = [z_up_button_pos1[0] + but_width,
					    z_up_button_pos1[1],
					   but_width,
					   but_height]
	z_up_button_axes2 = fig.add_axes(z_up_button_pos2)
	z_up_button2 = Button(z_up_button_axes2, '++ z')
	z_up_button2.label.set_fontsize(10)
	z_up_button2.on_clicked(__go_defocus_up_plus)


	z_down_button_pos1 = [z_up_button_pos1[0],
						 time_btwn_z_text_pos[1]+0.05,
						 but_width,
						 but_height]
	z_down_button_axes1 = fig.add_axes(z_down_button_pos1)
	z_down_button1 = Button(z_down_button_axes1, '- z')
	z_down_button1.label.set_fontsize(10)
	z_down_button1.on_clicked(__go_defocus_down)


	z_down_button_pos2 = [z_up_button_pos1[0] + but_width,
						 z_down_button_pos1[1],
						 but_width,
						 but_height]
	z_down_button_axes2 = fig.add_axes(z_down_button_pos2)
	z_down_button2 = Button(z_down_button_axes2, '- - z')
	z_down_button2.label.set_fontsize(10)
	z_down_button2.on_clicked(__go_defocus_down_plus)

	
	

	####################### defocus
	
	z_acquire_button_pos = [0.1,
						   time_btwn_z_text_pos[1] - 2 * padding - options_height * 3,
						 0.5,
						 options_height * 2]
	z_acquire_button_axes = fig.add_axes(z_acquire_button_pos)
	z_acquire_button = Button(z_acquire_button_axes, 'Start defocus acquisition(s)')
	z_acquire_button.label.set_fontsize(10)
	z_acquire_button.on_clicked(__defocus_acquisition)


	
	#################################################
	# Set default directory to current
	directory_pos = [0.13, 0.3, 0.66,
					 options_height*1.5]
	directory_axes = fig.add_axes(directory_pos)
	directory_text = TextBox(directory_axes, 'Directory')
	directory_text.label.set_fontsize(7)
	directory_text.set_val('')

	directory_button_pos = [directory_pos[0] + directory_pos[2] + padding,
							directory_pos[1],
							0.16,
							directory_pos[3]]
	directory_button_axes = fig.add_axes(directory_button_pos)
	directory_button = Button(directory_button_axes, 'Choose Directory')
	directory_button.label.set_fontsize(7)

	directory_button.on_clicked(__choose_directory)

	# Set name format
	name_format_pos = [directory_pos[0],
					   directory_pos[1] - 2*options_height - padding,
					   0.5,
					   directory_pos[3]]
	name_format_axes = fig.add_axes(name_format_pos)
	name_format_text = TextBox(name_format_axes, 'Name format')
	name_format_text.label.set_fontsize(7)
	name_format_text.set_val('test_{date}')

	# Set save primary button
	save_button_pos = [directory_pos[0],
					   name_format_pos[1] - 2*options_height - padding,
					   0.25,
					   directory_pos[3]]
	save_button_axes = fig.add_axes(save_button_pos)
	save_button = Button(save_button_axes, 'Start Acquisition(no z-scan)')
	save_button.label.set_fontsize(7)
	# Set callback
	save_button.on_clicked(__acquire_no_z)

	# Set av images text
	avg_images_text_pos = [save_button_pos[0] + save_button_pos[2] + padding + (
			0.5 - 2 * padding) * 0.1875 + 2 * padding,
						   name_format_pos[1] - 2*options_height - padding,
						   (0.2 - 2 * padding) * 0.8125 - padding,
						   directory_pos[3]]
	avg_images_text_axes = fig.add_axes(avg_images_text_pos)
	avg_images_text = TextBox(avg_images_text_axes, '# to Avg ')
	avg_images_text.label.set_fontsize(7)
	avg_images_text.set_val(10)
	avg_images_text.on_submit(__number_average)
	

	# Set counter
	counter_pos = [name_format_pos[0]+name_format_pos[2] + 10 * padding,
				   directory_pos[1] - 2*options_height - padding,
				   0.1,
				   directory_pos[3]]
	counter_axes = fig.add_axes(counter_pos)
	counter_text = TextBox(counter_axes, 'Counter ')
	counter_text.label.set_fontsize(7)
	counter_text.set_val(1)

	# Set num images text
	num_images_text_pos = [avg_images_text_pos[0]+avg_images_text_pos[2] + 12 * padding,
						   name_format_pos[1] - 2*options_height - padding,
						   0.1 - 2 * padding,
						   directory_pos[3]]
	num_images_text_axes = fig.add_axes(num_images_text_pos)
	num_images_text = TextBox(num_images_text_axes, '# to Acquire ')
	num_images_text.label.set_fontsize(7)
	num_images_text.set_val(1)
	num_images_text.on_submit(__number_acquire)
	


    #######################
    #PUMP

	
	pump_button_pos = [led_on_button_pos[0]-0.05 + 4.8*but_width,
					   1-1.8*but_height,
					   3*but_width,
					   0.7*but_height]

	valve_button_pos = [pump_button_pos[0],
					   1 - 2.4*but_height,
					   1.2*but_width,
					   0.5*but_height]
                       
	syringe_button_pos = [pump_button_pos[0],
					   1 - 5.8*but_height,
					   3*but_width,
					   0.7*but_height]
    
    
    
	rect_pos = [pump_button_pos[0]-0.01,
					   time_btwn_z_text_pos[1] - 2 * padding - options_height * 3, 
					   pump_button_pos[2]+0.02,
                       0.5]
	rect_id = fig.add_axes(rect_pos)
	rect_button = Button(rect_id,'')    
    
	pump_button_axes = fig.add_axes(pump_button_pos)
	pump_button = Button(pump_button_axes, 'Initialize Pump')
	pump_button.label.set_fontsize(8)
	pump_button.on_clicked(__initialize_pump)
    
	valve_button_axes = fig.add_axes(valve_button_pos)
	valve_button = Button(valve_button_axes, 'Run Valve')
	valve_button.label.set_fontsize(8)
	valve_button.on_clicked(__run_valve)
    
	syringe_button_axes = fig.add_axes(syringe_button_pos)
	syringe_button = Button(syringe_button_axes, 'Run Syringe')
	syringe_button.label.set_fontsize(8)
	syringe_button.on_clicked(__run_syringe)

	rax = [valve_button_pos[0]+0.11, valve_button_pos[1]-0.1, 0.13, 0.15]
	rax_axes = fig.add_axes(rax)
	valve_positions = RadioButtons(rax_axes, ('PBS', 'Sample', 'Chip'))
	valve_positions.on_clicked(__update_valve)

	speed_pos = [rax[0]+0.02,
						 valve_button_pos[1] - but_height*1.5,
						 0.1 - 2 * padding,
						 options_height * 2]
	speed_axes = fig.add_axes(speed_pos)
	speed_text = TextBox(speed_axes, 'Speed (ul/min) ')
	speed_text.label.set_fontsize(8)
	speed_text.set_val(__PUMP_SPEED)
	speed_text.on_submit(__update_speed)
    
	syringePosition_pos = [rax[0]+0.02,
						 valve_button_pos[1] - but_height*2,
						 0.1 - 2 * padding,
						 options_height * 2]
	syringePosition_axes = fig.add_axes(syringePosition_pos)
	syringePosition_text = TextBox(syringePosition_axes, 'Syringe (%) ')
	syringePosition_text.label.set_fontsize(8)
	syringePosition_text.set_val(__SYRINGEPOSITION)
	syringePosition_text.on_submit(__update_syringePosition)
	
	duration_pos = [rax[0]+0.02,
						 valve_button_pos[1] - but_height*2.5,
						 0.1 - 2 * padding,
						 options_height * 2]
	duration_axes = fig.add_axes(duration_pos)
	duration_text = TextBox(duration_axes, 'Duration (min) ')
	duration_text.label.set_fontsize(8)
	duration_text.set_val(0)

	
	return {'fig': fig,
 
			'duration_text': duration_text,	  
			'syringePosition_text': syringePosition_text,	    
			'speed_text': speed_text,			
			'valve_positions': valve_positions,
			'start_stream_button': start_stream_button,
			'start_stream_button': start_stream_button,
			'save_button': save_button,
			'name_format_text': name_format_text,
			'counter_text': counter_text,
			'num_images_text': num_images_text,
			'avg_images_text': avg_images_text,
		
			'directory_text': directory_text,
			'directory_button': directory_button,
			'syringe_button': syringe_button,            
			'pump_button': pump_button,
        	'valve_button':valve_button,
			'led_on_button': led_on_button,
			'led_off_button': led_off_button,
            'resetNPC_button': resetNPC_button,
			'z_step_text1': z_step_text1,
			'z_step_text2': z_step_text2,
			'step_num_text': step_num_text,
			'z_interval_text': z_interval_text,
			'time_btwn_z_text': time_btwn_z_text,
			'z_up_button1': z_up_button1,
			'z_down_button1': z_down_button1,
			'z_up_button2': z_up_button2,
			'z_down_button2': z_down_button2,
			'z_pos_but':z_pos_but,
			'z_acquire_button': z_acquire_button,
			
			}
def _test(_=None):
	print('test')



def main():

	global __STREAM
	global __IMSHOW_DICT, __IMSHOW_SECONDARY_DICT
	global __HIST_DICT, __HIST_SECONDARY_DICT
	global __GUI_DICT
	
	
	#stageZ.connect(__COM_PORT_NPC)
	#time.sleep(15)
	#stageZ.getSlewRate()
	#stageZ.getPosition()
	#stageZ.moveAbsolute(50,0)




	# Set GUI
	__GUI_DICT = __spincam_gui()


	#__find_and_init_cam()

	while plt.fignum_exists(__GUI_DICT['fig'].number):  # pylint: disable=unsubscriptable-object
		try:

			plt.pause(sys.float_info.min)
		except:  # pylint: disable=bare-except
			if plt.fignum_exists(__GUI_DICT['fig'].number):
				# Only re-raise error if figure is still open
				raise

	# Clean up
	#__QUEUE = queue.Queue()
	__STREAM = False
	__IMSHOW_DICT = {'imshow': None, 'imshow_size': None}
	__HIST_DICT = {'bar': None}
	__GUI_DICT = None
	__STAGE_DICT = None
	#__ledOFF()

	print('Exiting...')

	return 0
	

if __name__ == '__main__':
	sys.exit(main())
