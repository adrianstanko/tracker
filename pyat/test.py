from serial_port import PyAt
from device import Device


def test():
	port = PyAt()
	device = Device()

	response = port.command(b'AT\r')
	print(response)
	if len(response) == 0:
		device.start()
	r = port.command(b'AT\r')
	if len(r) == 0:
		print("Failed")
	else:
		print("Success")


if __name__ == "__main__":
	test()
