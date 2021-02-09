#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time
import logging
from collections import namedtuple

GnsInf = namedtuple('GnsInfo', ['GNSS_run_status', 'FixS', 'UTCT', 'lat', 'lon',
'alt', 'spd', 'Course_Over_Ground', 'Fix_Mode', 'Reserved1', 'HDOP', 'PDOP', 'VDOP', 'Reserved2',
'GNSS_Satellites_in_View', 'GNSS_Satellites_Used', 'GLONASS_Satellites_Used', 'Reserved3', 'C_slash_N0_max', 'HPA', 'VPA'])

class Sim7000E:
	power_key = 4
	
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyS0',115200)
		self.ser.flushInput()

	def __del__(self):
		if self.ser != None:
			self.ser.close()
			GPIO.cleanup()
			
	def power_on(self):
		logging.info('SIM7000E is starting...')
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.power_key,GPIO.OUT)
		time.sleep(0.1)
		GPIO.output(self.power_key,GPIO.HIGH)
		time.sleep(2)
		GPIO.output(self.power_key,GPIO.LOW)
		time.sleep(2)
		self.ser.flushInput()
		logging.info('SIM7000E is ready!')

	def power_down(self):
		logging.info('SIM7000E is loging off...')
		GPIO.output(self.power_key,GPIO.HIGH)
		time.sleep(3)
		GPIO.output(self.power_key,GPIO.LOW)
		time.sleep(2)
		logging.info('Done!')
		
	def send_at(self, command, back='OK', timeout=1):
		rec_buff = ''
		self.ser.write((command+'\r\n').encode())
		time.sleep(timeout)
		if self.ser.inWaiting():
			time.sleep(0.1)
			rec_buff = self.ser.read(self.ser.inWaiting())
		if rec_buff != '':
			rec_decoded = rec_buff.decode(errors="replace")
			if back not in rec_decoded:
				logging.info(command + ' - command failed')
				logging.info('response:\t' + rec_decoded)
				return None
			else:
				logging.debug(command + ' - command successful')
				logging.debug('response: \t' + rec_decoded)
				return rec_decoded
		else:
			logging.info(command + ' no response')
			return None


	def send_gps(self, command, back='OK', timeout=1):
		response = self.send_at(command, back, timeout)
		if response:
			s = response.split(",")[:-1]
			# Remove echoed command
			s[0] = u''.join([a for a in s[0] if a.isdigit()])
			return GnsInf(*s)