from device import Device
from serial_port import PyAt
import serial_port

class Modem:
	'''Class that encapsulates communication with modem on serial port'''

	def __init__(self):
		print("Creating Modem instance...")
		self.serial = PyAt()
		self.device = Device()
		print("Setting up communication...")
		if not self.serial.expect_command_response(b'AT', b'OK'):
	                print("No response received, try to start the device...")
	                device.start()
		self.self_test()

	def self_test(self):
		assert(self.serial.expect_command_response(b'AT', b'OK'))
		print("Test disable echo...")
		assert(self.serial.expect_command_response(b'ATE0', b'OK'))
		assert(self.serial.expect_command_response(b'AT', b'OK', accept_echo = False))


