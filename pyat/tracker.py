#!/usr/bin/python

import sim7000e
import time
import json
import logging


class Tracker:

	def __init__(self):
		self.sim = sim7000e.Sim7000E()

	def power_on(self):
		self.sim.power_on()

	def power_down(self):
		self.sim.power_down()
		
	def clean_connections(self):
		self.sim.send_at('AT+SMDISC','OK',2)
		self.sim.send_at('AT+CNACT=0')
		
	def send_at(self, command, back='OK', timeout=1):
		return self.sim.send_at(command, back, timeout)

	def send_gps(self, command, back='OK', timeout=1):
		return self.sim.send_gps(command, back, timeout)
		
	def configure_sim(self):
		ret = None
		while ret == None:
			ret = self.sim.send_at('AT+CSQ')
		self.sim.send_at('AT+CREG?', '+CREG: 0,1', 1)
		while ret == None:
			self.sim.send_at('AT+CPSI?')
		
	def configure_mqtt(self):
		logging.info('Setting up the MQTT...')
		self.sim.send_at('AT+CNACT=1,"internet"', 'OK', 4)
		self.sim.send_at('AT+CNACT?', 'OK', 2)
		self.sim.send_at('AT+SMDISC','OK',2)
		self.sim.send_at('AT+SMCONF="URL","test.mosquitto.org","1883"','OK',1)
		self.sim.send_at('AT+SMCONF="KEEPTIME",60','OK',1)
		self.sim.send_at('AT+SMCONF?','OK',2)
		self.sim.send_at('AT+SMSTATE?')
		self.sim.send_at('AT+SMCONN','OK', 3)
		self.sim.send_at('AT+SMSTATE?')
		
	def configure_gps(self):
		logging.info('Powering up the GPS...')
		self.sim.send_at('AT+CGNSPWR=1', 'OK', 2)
		self.sim.send_at('AT+CGNSMOD?')
		
	def send_location(self):
		gps_raw = self.sim.send_gps('AT+CGNSINF')
		if gps_raw != None:
			gps = gps_raw._asdict()
			# send fake location
			#gps['Latitude'] = u'50.057709'
			#gps['Longitude'] = u'19.951270'
			
			data_to_send = ['FixS', 'UTCT', 'lat', 'lon', 'alt', 'spd']
			gps_to_send = {key : gps[key] for key in gps.keys() if key in data_to_send}
			# jsonize
			json_str = str(json.dumps(gps_to_send))
			self.sim.send_at('AT+SMPUB="koko",' + str(len(json_str)) + ',1,1','>',2)
			self.sim.send_at(json_str, 'OK', 3)
			logging.info('Sending location: lat ' + gps['lat'] + ' lon '+ gps['lon'])

if __name__ == "__main__":
	logging.basicConfig(handlers=[logging.FileHandler("/home/pi/gpsdata.log"), logging.StreamHandler()], encoding='utf-8', level=logging.INFO)
	logging.info('Starting the script...')
	tracker = Tracker()
	
	tracker.power_on()
	tracker.configure_sim()
	
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

	'''tracker.send_at('AT+CIPSTART="TCP","httpbin.org","80"', 'OK', 4)

	tracker.send_at('AT+SAPBR=3,1,"APN","internet"')
	tracker.send_at('AT+SAPBR=1,1')
	tracker.send_at('AT+HTTPINIT')
	tracker.send_at('AT+HTTPPARA="CID",1')
	tracker.send_at('AT+HTTPPARA="REDIR",1')
	tracker.send_at('AT+HTTPPARA="URL","http://echo.jsontest.com/title/kokokokoko/content/Sofijka"', 'OK', 4)
	tracker.send_at('AT+HTTPACTION=0', 'OK', 4)
	tracker.send_at('AT+HTTPREAD', 'OK', 3)
	tracker.send_at('AT+HTTPTERM')
	tracker.send_at('AT+SAPBR=0,1')'''

	tracker.configure_mqtt()
	tracker.configure_gps()
	
	try:
		while(True):
			tracker.send_location()
			
	except KeyboardInterrupt:
		logging.info("Closing...")
		tracker.clean_connections()
		tracker.power_down()

