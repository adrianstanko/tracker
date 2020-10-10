import serial
import time

class PyAt:

	def __init__(self, dev='/dev/ttyS0'):
		self.serial_port = serial.Serial(dev, 115200, timeout=1)

	def command(self, cmd, sleep_seconds = 1):
		self.serial_port.write(cmd + b'\r')
		time.sleep(sleep_seconds)
		ret = []
		while self.serial_port.inWaiting() > 0:
			msg = self.serial_port.readline().strip()
			msg = msg.replace(b'\r',b'')
			msg = msg.replace(b'\n', b'')
			if len(msg) != 0:
				ret.append(msg)
		return ret

	def expect_command_response(self, cmd, expected, accept_echo = True):
		received = self.command(cmd)
		if accept_echo:
			if cmd in received:
				received.remove(cmd)
		return [expected] == received

if __name__ == "__main__":
	pyat = PyAt()
	r = pyat.expect_command_response(b'AT', b'OK')
	print(r)
