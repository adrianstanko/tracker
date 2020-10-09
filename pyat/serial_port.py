import serial
import time

class PyAt:

	def __init__(self, dev='/dev/ttyS0'):
		self.serial_port = serial.Serial(dev, 115200, timeout=1)

	def command(self, cmd):
		self.serial_port.write(cmd + b'\r')
		time.sleep(1)
		ret = []
		while self.serial_port.inWaiting() > 0:
			msg = self.serial_port.readline().strip()
			if msg != "":
				ret.append(msg)
		return ret

if __name__ == "__main__":
	pyat = PyAt()
	r = pyat.command(b'AT')
	print(r)
