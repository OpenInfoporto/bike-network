from gattlib import DiscoveryService
import requests
import time
import json
from urllib2 import urlopen
import logging
import sys
import sqlite3


conn = sqlite3.connect('offline.db')
c = conn.cursor()
    
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
by = dict()
hello = []
offlineDevicesList = []
offlineDevicesIn = []
offlineDevicesOut = []

offlineDevices = dict()
compare = dict()
devices = service.discover(4)
compare = devices



    
while True:
	try:
		#request the devices information to the database
		resp = urlopen("%s/uri/devices/%s" % (url, controller) )
		#conversion json object
		jsonResp = json.loads(resp.read().decode('utf-8'))
		#little cycle that update the list "controlledDevices" with the database information
		for item in jsonResp['devices']:
			print item
			controlledDevices.update(item)
		#request the last state of the asscociated devices
		respStates = urlopen("%s/uri/cronologia/last/controller/%s" % (url, controller) )
		#conversion json object
		jsonRespStates = json.loads(respStates.read().decode('utf-8'))
		#cycle that print the last devices present in the range of the scanner
		for record in jsonRespStates['cronologia']:
			if record['state'] == 'in':
				print("already there: {}, address: {}".format(controlledDevices[record['mac']],record['mac'] ))
				states[record['mac']] = controlledDevices[record['mac']]
				c.execute('DELETE FROM cronologia')
				conn.commit()
		break
	except:
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
			elif address not in states and address in devices:
				offlineDevicesInDict = dict()
				ts = int(time.time())
				states[address]= name
				print("entering name: {}, address: {} at time: {}".format(name, address, ts))
				offlineDevicesInDict.update({'mac': address,  'time_stamp': ts, 'state': "in"})
				offlineDevicesIn.append(offlineDevicesInDict)
			else:
				pass
				
		while True:		
			if offlineDevicesIn:
				dtemp = offlineDevicesIn.pop()
				c.execute('INSERT INTO cronologia VALUES (?,?,?)', [dtemp['mac'], dtemp['time_stamp'], dtemp['state']])
				conn.commit()
			else:
				break
		while True:
			if offlineDevicesOut:
				dtemp = offlineDevicesOut.pop()
				c.execute('INSERT INTO cronologia VALUES (?,?,?)', [dtemp['mac'], dtemp['time_stamp'], dtemp['state']])
				conn.commit()
			else:
				break
		for row in c.execute('SELECT * FROM cronologia'):
			cd = list(row)
			i=0
			while cd:
				
				by['item%s' %i] = cd.pop()
				i = i + 1
			
			offlineDevices['state'] = by['item0']
			offlineDevices['time_stamp'] = by['item1']
			offlineDevices['mac'] = by['item2']
			offlineDevicesList.append(offlineDevices)
			while offlineDevicesList :				
				try:
					xx = offlineDevicesList.pop()
					response = requests.post(requestUrl, data=xx)
				except:
					break

#infinite loop
while True:	
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

					while True:
						if offlineDevicesOut:
							dtemp = offlineDevicesOut.pop()
							c.execute('INSERT INTO cronologia VALUES (?,?,?)', [dtemp['mac'], dtemp['time_stamp'], dtemp['state']])
							conn.commit()
						else:
							break
					
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

						while True:
							if offlineDevicesIn:
								dtemp = offlineDevicesIn.pop()
								c.execute('INSERT INTO cronologia VALUES (?,?,?)', [dtemp['mac'], dtemp['time_stamp'], dtemp['state']])
								conn.commit()
							else:
								break
	try:
		r = urlopen(url)
		for row in c.execute('SELECT * FROM cronologia'):
			cd = list(row)
			i=0
		
			
			while cd:
				by['item%s' %i] = cd.pop()
				i = i + 1
				
			offlineDevices['state'] = by['item0']
			offlineDevices['time_stamp'] = by['item1']
			offlineDevices['mac'] = by['item2']
			offlineDevicesList.append(offlineDevices)
			while offlineDevicesList:
					xx = offlineDevicesList.pop()
					response = requests.post(requestUrl, data=xx)			
	except:
		pass				
	try:
		r = urlopen(url)
		c.execute('DELETE FROM cronologia')
		conn.commit()
	except:
		pass	