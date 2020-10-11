from collections import namedtuple

from device import Device
from serial_port import PyAt
import serial_port

class Modem:
	'''Class that encapsulates communication with modem on serial port'''

	GnssInfo = namedtuple('GnssInfo', ['GNSS_run_status','Fix_status','UTC_date_and_Time',
'Latitude','Longitude','MSL_Altitude','Speed_Over_Ground','Course_Over_Ground',
'Fix_Mode','Reserved1','HDOP','PDOP','VDOP','Reserved2','GNSS_Satellites_in_View',
'GNSS_Satellites_Used','GLONASS_Satellites_Used','Reserved3','C_N0_max','HPA','VPA'])

	def __init__(self):
		print("Creating Modem instance...")
		self.serial = PyAt()
		self.device = Device()
		print("Setting up communication...")
		if not self.serial.command_check(b'AT', b'OK'):
	                print("No response received, try to start the device...")
	                self.device.start()
		self.self_test()

	def self_test(self):
		print("Performing self test...")
		assert(self.serial.command_check(b'AT', b'OK'))
		print("Test disable echo...")
		assert(self.serial.command_check(b'ATE0', b'OK'))
		assert(self.serial.command_check(b'AT', b'OK', accept_echo = False))

	@property
	def gnss_power(self):
		return(self.serial.command(b'AT+CGNSPWR?'))
		
	@gnss_power.setter
	def gnss_power(self, value):
		assert(self.serial.command_check(b'AT+CGNSPWR' + str(value).encode, b'OK'))

	@property
	def gnss_info(self):
		info = (self.serial.command(b'AT+CGNSINF?')[0]).split(sep=',')
		return self.GnssInfo(*info)
