# example.py
# -*- coding: utf-8 -*-
# jan 2016
# Si7005 temperature/relative humidity sensor example
# tested on micropython v1.3


from si7005 import SI7005
import time

sensor = SI7005('X', 'Y8')			# I2C bus side and CS pin connection

sensor.detectSensor()				# true if communication works
hum = sensor.getHumidity()			# humidity in %
temp = sensor.getTemperature()		# temperature in °C

sensor.enableHeater()				# turn on integrated heater during measurement
sensor.disableHeater()				# turn off integrated heater
sensor.enableFastMeasurements()		# enable fast measurement
sensor.disableFastMeasurements()	# disable fast measurement
