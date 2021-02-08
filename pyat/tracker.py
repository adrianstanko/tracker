#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time
from collections import namedtuple
import json
import logging

GnsInf = namedtuple('GnsInfo', ['GNSS_run_status', 'FixS', 'UTCT', 'lat', 'lon',
'alt', 'spd', 'Course_Over_Ground', 'Fix_Mode', 'Reserved1', 'HDOP', 'PDOP', 'VDOP', 'Reserved2',
'GNSS_Satellites_in_View', 'GNSS_Satellites_Used', 'GLONASS_Satellites_Used', 'Reserved3', 'C_slash_N0_max', 'HPA', 'VPA'])
 
APN = 'internet'
ServerIP = '118.190.93.84'
Port = '2317'
Message = 'Waveshare'

class Tracker:
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
		

if __name__ == "__main__":
	logging.basicConfig(handlers=[logging.FileHandler("/home/pi/gpsdata.log"), logging.StreamHandler()], encoding='utf-8', level=logging.INFO)
	logging.info('Starting the script...')
	tracker = Tracker()
	
	tracker.power_on()
	ret = None
	while ret == None:
		ret = tracker.send_at('AT+CSQ')
	tracker.send_at('AT+CREG?','+CREG: 0,1',1)
	while ret == None:
		tracker.send_at('AT+CPSI?')

	'''tracker.send_at('AT+CIPSHUT')
	tracker.send_at('AT+CIPMUX=0')
	#tracker.send_at('AT+CIPSTATUS')
	tracker.send_at('AT+CSTT="internet","",""', 'OK', 2)
		tracker.send_at('AT+CIPSTATUS', 'OK', 2)
	tracker.send_at('AT+CIICR', 'OK', 2)
	tracker.send_at('AT+CIPSTATUS')
	tracker.send_at('AT+CIFSR', 'OK', 2)
	#tracker.send_at('AT+CIPPING="www.httpbin.org",3', 'OK', 30)'''

	'''tracker.send_at('AT+CGNSPWR=1', 'OK', 2)
	tracker.send_at('AT+CGNSMOD?')
	for _ in range(10):
		gps = send_gps('AT+CGNSINF')'''
		

	#tracker.send_at('AT+CIPSTART="TCP","httpbin.org","80"', 'OK', 4)

	#tracker.send_at('AT+SAPBR=3,1,"APN","internet"')
	#tracker.send_at('AT+SAPBR=1,1')
	#tracker.send_at('AT+HTTPINIT')
	#tracker.send_at('AT+HTTPPARA="CID",1')
	#tracker.send_at('AT+HTTPPARA="REDIR",1')
	#tracker.send_at('AT+HTTPPARA="URL","http://echo.jsontest.com/title/kokokokoko/content/Sofijka"', 'OK', 4)
	#tracker.send_at('AT+HTTPACTION=0', 'OK', 4)
	#tracker.send_at('AT+HTTPREAD', 'OK', 3)
	#tracker.send_at('AT+HTTPTERM')
	#tracker.send_at('AT+SAPBR=0,1')

	logging.info('Setting up the MQTT...')
	tracker.send_at('AT+CNACT=1,"internet"', 'OK', 4)
	tracker.send_at('AT+CNACT?', 'OK', 2)
	tracker.send_at('AT+SMDISC','OK',2)
	tracker.send_at('AT+SMCONF="URL","test.mosquitto.org","1883"','OK',1)
	tracker.send_at('AT+SMCONF="KEEPTIME",60','OK',1)
	tracker.send_at('AT+SMCONF?','OK',2)
	tracker.send_at('AT+SMSTATE?')
	tracker.send_at('AT+SMCONN','OK', 3)
	tracker.send_at('AT+SMSTATE?')
	
	logging.info('Powering up the GPS...')
	tracker.send_at('AT+CGNSPWR=1', 'OK', 2)
	tracker.send_at('AT+CGNSMOD?')
	
	try:
		while(True):
			gps_raw = tracker.send_gps('AT+CGNSINF')
			if gps_raw != None:
				gps = gps_raw._asdict()
				# send fake location
				#gps['Latitude'] = u'50.057709'
				#gps['Longitude'] = u'19.951270'
				
				data_to_send = ['FixS', 'UTCT', 'lat', 'lon', 'alt', 'spd']
				gps_to_send = {key : gps[key] for key in gps.keys() if key in data_to_send}
				# jsonize
				json_str = str(json.dumps(gps_to_send))
				tracker.send_at('AT+SMPUB="koko",' + str(len(json_str)) + ',1,1','>',2)
				tracker.send_at(json_str, 'OK', 3)
				logging.info('Sending location: lat ' + gps['lat'] + ' lon '+ gps['lon'])
			
	except KeyboardInterrupt:
		logging.info("Closing...")

		'''tracker.send_at('AT+SMPUB="koko",7,1,1','>',2)
		tracker.send_at('sofijka', 'OK', 3)'''
		tracker.send_at('AT+SMDISC','OK',2)
		tracker.send_at('AT+CNACT=0')

		tracker.power_down()

