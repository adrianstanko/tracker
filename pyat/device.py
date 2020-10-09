from gpiozero import DigitalOutputDevice as GPIO
from time import sleep


class Device:
	power_pin = 4
	
	def __init__(self):
		self.power = GPIO(4)

	def start(self):
		print('Starting the device...')
		self.power.off()
		sleep(1)
		self.power.on()
		

