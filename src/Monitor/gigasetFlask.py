#import the necessary module
from flask import Flask, render_template, redirect, url_for, jsonify, g
from flask_restful import reqparse, abort, Api, Resource
from flask.ext.httpauth import HTTPBasicAuth
from flask_bootstrap import Bootstrap
import time
import datetime
import sqlite3
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, create_engine, MetaData, join, alias, desc
from sqlalchemy.orm import mapper

#creating the engine 																		
engine = create_engine('sqlite:///gigaset.db', convert_unicode=True) 
metadata = MetaData(bind=engine)

app = Flask(__name__)
Bootstrap(app)

#declaration table "cronologia" and "devices"
cronologia = Table('cronologia', metadata, autoload=True)
devices = Table('devices', metadata, autoload=True)


#creating parser, data that can be recived 
parser = reqparse.RequestParser()
parser.add_argument('mac', type=str)
parser.add_argument('time_stamp', type=str)
parser.add_argument('state', type=str)

#GET method that return all the devices
@app.route('/uri/devices', methods=['GET'])
def listaDevices():
	deviceList = list()
	deviceQuery = devices.select().execute()
	for device in deviceQuery:
		deviceList.append({
			'mac': device['mac'],
			'name': device['name'],
			'controller': device['controller']
			})

	return jsonify(devices = deviceList)

#GET method that return the devices filtred by controller
@app.route('/uri/devices/<idController>', methods=['GET']) 
def listaController(idController):
	#creating deviceList
	deviceList = list()
	#creating the query
	deviceQuery = devices.select(devices.c.controller==idController).execute()
	for device in deviceQuery:
		#inserting the mac and the name to the list
		deviceList.append({
			device['mac']: device['name']
			})
	#return the value, and http code 200 "ok"
	return jsonify(devices = deviceList) , 200


#POST method that recive from the scanner data that will be print in the database
@app.route('/uri/cronologia', methods=['POST'])
def postStory():
	#declaration variable args that convert the string variable to an object withe the method "parse_args()"
	args = parser.parse_args()
	print args['mac']
	print args['time_stamp']
	print args['state']
	mac = args['mac']
	time_stamp = args['time_stamp']
	state = args['state']
	#linking the engine
	conn = engine.connect()
	#inserting the value to the database, table "cronologia"
	conn.execute(cronologia.insert(), mac=mac, time_stamp=time_stamp, state=state)
	conn.close()
	return "inserito", 201

#GET method that return all the story
@app.route('/uri/cronologia', methods=['GET'])
def listaCronologia():
	storyList = list()
	#JOIN method,used for take the name frome the devices table
	tableJoin = cronologia.join(devices,
                cronologia.c.mac == devices.c.mac)
	#decreasing sorting
	recordQuery = tableJoin.select().apply_labels().order_by(cronologia.c.time_stamp.desc()).execute()
	for record in recordQuery:		
		storyList.append({
			'mac': record['cronologia_mac'],
			'name': record['devices_name'],
			'time_stamp': datetime.datetime.fromtimestamp(int(record['cronologia_time_stamp'])).strftime('%d-%m-%Y %H:%M'),
			'state': record['cronologia_state']
		})	

	return jsonify(cronologia = storyList) , 200




#GET method that return the story filtred by controller
@app.route('/uri/cronologia/controller/<idController>', methods=['GET'])
def listaCronologiaController(idController):
	storyList = list()
	tableJoin = cronologia.join(devices,
                cronologia.c.mac == devices.c.mac)
	recordQuery = tableJoin.select(devices.c.controller==idController).apply_labels().order_by(cronologia.c.time_stamp.desc()).execute()
	for record in recordQuery:		
		storyList.append({
			'mac': record['cronologia_mac'],
			'name': record['devices_name'],
			'time_stamp': datetime.datetime.fromtimestamp(int(record['cronologia_time_stamp'])).strftime('%d-%m-%Y %H:%M'),
			'state': record['cronologia_state']
		})	

	return jsonify(cronologia = storyList) , 200

#GET method that returns the last state of the devices assigned to a controller
@app.route('/uri/cronologia/last/controller/<idController>', methods=['GET'])
def listaLstaCronologiaController(idController):
	storyList = list()

	result = engine.execute('select mac, state from cronologia group by mac order by time_stamp DESC').fetchall()

	for record in result:
		storyList.append({
			'mac': record['mac'],
			'state': record['state']
		})

	return jsonify(cronologia = storyList) , 200

#GET method that return the story filtred by MAC address
@app.route('/uri/cronologia/mac/<macAddress>', methods=['GET'])
def listaCronologiaMac(macAddress):
	storyList = list()
	tableJoin = cronologia.join(devices,
	                cronologia.c.mac == devices.c.mac)
	recordQuery = tableJoin.select(devices.c.mac==macAddress).apply_labels().order_by(cronologia.c.time_stamp.desc()).execute()
	for record in recordQuery:		
		storyList.append({
			'mac': record['cronologia_mac'],
			'name': record['devices_name'],
			'time_stamp': datetime.datetime.fromtimestamp(int(record['cronologia_time_stamp'])).strftime('%d-%m-%Y %H:%M'),
			'state': record['cronologia_state']
		})

	return jsonify(cronologia = storyList) , 200






# ----------- web part -----------------------

#GET method that return all devices
@app.route('/devices', methods=['GET'])
def listaDevicesWeb():
	deviceList = list()
	deviceQuery = devices.select().execute()
	for device in deviceQuery:
		deviceList.append({
			'mac': device['mac'],
			'name': device['name'],
			'controller': device['controller']
			})
	return render_template("devices.html", lista = deviceList)


#GET method that return all devices in a controller
@app.route('/devices/<idController>', methods=['GET']) 
def listaControllerWeb(idController):	
	deviceList = list()	
	deviceQuery = devices.select(devices.c.controller==idController).execute()
	for device in deviceQuery:		
		deviceList.append({
			'mac': device['mac'],
			'name': device['name'],
			'controller': device['controller']
			})
	return render_template("devices.html", lista = deviceList)

#GET method that return all the story
@app.route('/cronologia', methods=['GET'])
def listaCronologiaWeb():
	storyList = list()
	#JOIN method,used for take the name frome the devices table
	tableJoin = cronologia.join(devices,
                cronologia.c.mac == devices.c.mac)
	#decreasing sorting
	recordQuery = tableJoin.select().apply_labels().order_by(cronologia.c.time_stamp.desc()).execute()
	for record in recordQuery:		
		storyList.append({
			'mac': record['cronologia_mac'],
			'name': record['devices_name'],
			'controller': record['devices_controller'],
			'time_stamp': datetime.datetime.fromtimestamp(int(record['cronologia_time_stamp'])).strftime('%d-%m-%Y %H:%M'),
			'state': record['cronologia_state']
		})	

	return render_template("story.html", lista = storyList)


#GET method that return the story filtred by controller
@app.route('/cronologia/controller/<idController>', methods=['GET'])
def listaCronologiaControllerWeb(idController):
	storyList = list()
	tableJoin = cronologia.join(devices,
                cronologia.c.mac == devices.c.mac)
	recordQuery = tableJoin.select(devices.c.controller==idController).apply_labels().order_by(cronologia.c.time_stamp.desc()).execute()
	for record in recordQuery:		
		storyList.append({
			'mac': record['cronologia_mac'],
			'name': record['devices_name'],
			'controller': record['devices_controller'],
			'time_stamp': datetime.datetime.fromtimestamp(int(record['cronologia_time_stamp'])).strftime('%d-%m-%Y %H:%M'),
			'state': record['cronologia_state']
		})	

	return render_template("story.html", lista = storyList)


#GET method that return the story filtred by MAC address
@app.route('/cronologia/mac/<macAddress>', methods=['GET'])
def listaCronologiaMacWeb(macAddress):
	storyList = list()
	tableJoin = cronologia.join(devices,
	                cronologia.c.mac == devices.c.mac)
	recordQuery = tableJoin.select(devices.c.mac==macAddress).apply_labels().order_by(cronologia.c.time_stamp.desc()).execute()
	for record in recordQuery:		
		storyList.append({
			'mac': record['cronologia_mac'],
			'name': record['devices_name'],
			'controller': record['devices_controller'],
			'time_stamp': datetime.datetime.fromtimestamp(int(record['cronologia_time_stamp'])).strftime('%d-%m-%Y %H:%M'),
			'state': record['cronologia_state']
		})	

	return render_template("story.html", lista = storyList)

#index
@app.route('/', methods=['GET'])
def index():
	return redirect(url_for('listaDevicesWeb'))





if __name__ == '__main__':
    #app.run(host='192.168.123.129',debug=False)
    app.run(debug=True)
