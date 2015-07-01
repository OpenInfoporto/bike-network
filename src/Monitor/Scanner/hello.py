from gattlib import DiscoveryService
import requests
import time
import json
from urllib2 import urlopen
import logging
import sys
    

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
url = "http://127.0.0.1:5000"
discoverDevice = "hci0"	
controller = "controller001"
requestUrl = "%s/uri/cronologia" % url

#invoke the "DiscoveryService" class  
service = DiscoveryService(discoverDevice)

#declaration of the two dictionaries "controlledDevices" and "states"
controlledDevices = dict()
states = dict ()
offlineDevicesIn = []
offlineDevicesOut = []

compare = dict()
devices = service.discover(4)
compare = devices

    
while True:
	logging.error ('Server not found')
	logging.info ('Starting local scanning')  
	#invoke the function from module "gattlib" that discover the LE( low energy )devices
	devices = service.discover(4)
	for address, name in compare.items():
		if address in states and address not in devices:
			offlineDevicesOutDict = dict()
			ts = int(time.time())
			print("leaving name: {}, address: {} at time: {}".format(name, address, ts))
			offlineDevicesOutDict.update({'mac': address,  'time_stamp': ts,  'state': "out"})
			offlineDevicesOut.append(offlineDevicesOutDict)
			del states[address]
		else:
			if address not in states and address in devices:
				offlineDevicesInDict = dict()
				ts = int(time.time())
				states[address]= name
				print("entering name: {}, address: {} at time: {}".format(name, address, ts))
				offlineDevicesInDict.update({'mac': address,  'time_stamp': ts, 'state': "in"})
				offlineDevicesIn.append(offlineDevicesInDict)						
#infinite loop
while True:
	for obj in states.items():
		try:
			r = urlopen(url)
		except:
			break
		if  offlineDevicesIn:
			dtemp = offlineDevicesIn.pop()
		else:
			break
		for  key in states.keys():
			if key == dtemp['mac']:
				try:
					response = requests.post(requestUrl, data=dtemp)
				except:
					break
	for obj in states.items():
		try:
			r = urlopen(url)
		except:
			break
		if  offlineDevicesOut:
			dtemp = offlineDevicesOut.pop()
		else:
			break
		for  key in states.keys():
			if key == dtemp['mac']:
				try:
					response = requests.post(requestUrl, data=dtemp)
				except:
					break
	logging.debug('Scanning')
	#invoke the function from module "gattlib" that discover the LE( low energy )devices
	devices = service.discover(4)
	for address, name in controlledDevices.items():
		if address in states and address not in devices:
			ts = int(time.time())
			print("leaving name: {}, address: {} at time: {}".format(name, address, ts))
			#request to the local server to invoke POST method, to update the story					
			try:
					response = requests.post(requestUrl, data={'mac': address, 'time_stamp': int(time.time()), 'state': "out"})
			except:
					offlineDevicesOutDict = dict()
					logging.error ('Server not found')
					logging.info ('Adding data to a local storage')
					ts = int(time.time())
					offlineDevicesOutDict.update({'mac': address,  'time_stamp': ts,  'state': "out"})
					offlineDevicesOut.append(offlineDevicesOutDict)
					del states[address]
		else:
			if address not in states and address in devices:	
				ts = int(time.time())
				print("entering name: {}, address: {} at time: {}".format(name, address, ts))
				#request to the local server to invoke POST method, to update the story
				states[address] = name
				try:
						response = requests.post(requestUrl, data={'mac': address,  'time_stamp': int(time.time()), 'state': "in"})
				except:
						offlineDevicesInDict = dict()
						logging.error ('Server not found')
						logging.info ('Adding data to a local storage')
						ts = int(time.time())
						offlineDevicesInDict.update({'mac': address,  'time_stamp': ts, 'state': "in"})
						offlineDevicesIn.append(offlineDevicesInDict)


