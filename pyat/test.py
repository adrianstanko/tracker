from serial_port import PyAt
from device import Device
from modem import Modem

def test():
	port = PyAt()
	device = Device()
	print("Try to communicate with the device...")

	ok = port.expect_command_response(b'AT', b'OK')
	if  ok:
		print("Success!")
	else:
		print("No response received, try to start the device...")
		device.start()
		ok = port.expect_command_response(b'AT', b'OK')
		if not ok:
			print("Failed!")
		else:
			print("Success!")
			return False

	print("Test disable echo...")
	if not port.expect_command_response(b'ATE0', b'OK'):
		print("Failed!")
		return False
	if not port.expect_command_response(b'AT', b'OK', accept_echo = False):
		print("Echo not disabled, failed!")
		return False
	print("Success!")

	return True

if __name__ == "__main__":
	modem = Modem()
	#test()

