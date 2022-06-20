import serial
import atexit
import os

COM='COM5'
CR = chr(13)
s=None



def __destructor():

    print('Closing Pump Connection')

    __close()
    
atexit.register(__destructor)

	
def __close():
	s.close()


def close():
	return __close()
	
def send(command):

	command = command + CR
	s.write(command)
	
def receive(self):
	#receive the data from the arduino
	return __SERIAL.readline().decode('ascii')
	

def ___initialize():
	global s
	global COM
	s = serial.Serial()
	s.baudrate=9600
	s.port=COM
	s.open()
	if (s.isOpen()):
		print("Pump is Initialized")
		#Enable h Factor Commands and Queries
		command = "/1h30001R"+CR 
		s.write(command.encode())
		time.sleep(1)
		command = "/1h20000R"+CR  #Initialize Valve
		s.write(command.encode())
		time.sleep(1)
		command = "/1h10010R"+CR #Initialize Syringe Only Initialize Syringe initializes the syringe. 10,000 + speed code
		s.write(command.encode())
		time.sleep(1)
	else:
		print("Pump not Initialized")