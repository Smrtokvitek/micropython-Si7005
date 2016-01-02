# Si7005.py
# -*- coding: utf-8 -*-
# jan 2016 python port of Si7005 arduino library https://github.com/jjalling/Arduino-Si7005
# rewritten https://github.com/AKAMEDIASYSTEM/bbb-garden/blob/master/Si7005.py for micropython/pyboard v1.0
# 

import pyb


class SI7005(object):
	# /* Si7005 Registers */
	REG_STATUS         = 0x00
	REG_DATA           = 0x01
	REG_CONFIG         = 0x03
	REG_ID             = 0x11

	# /* Status Register */
	STATUS_NOT_READY   = 0x01

	# /* Config Register */
	CONFIG_START       = 0x01
	CONFIG_HEAT        = 0x02
	CONFIG_HUMIDITY    = 0x00
	CONFIG_TEMPERATURE = 0x10
	CONFIG_FAST        = 0x20

	# /* ID Register */
	ID_SAMPLE          = 0xF0
	ID_SI7005          = 0x50

	# /* Coefficients */
	TEMPERATURE_OFFSET  =  50
	TEMPERATURE_SLOPE   =  32
	HUMIDITY_OFFSET     =  24
	HUMIDITY_SLOPE      =  16
	a0 = -4.7844
	a1 =  0.4008
	a2 = -0.00393
	q0 =  0.1973
	q1 =  0.00237

	WAKE_UP_TIME = 15 # AKA thinks this was 15ms, so changing it to 0.015sec
	# address
	SI7005_ADR = 0x40


	def __init__(self, side, csPin):
		if side == 'X':
			self.i2c = pyb.I2C(1)
		else:
			self.i2c = pyb.I2C(2)
		self.i2c.init(pyb.I2C.MASTER, baudrate=400000) # 400kHz

		# CS pin - high = disabled
		self._cs_pin = pyb.Pin(csPin, pyb.Pin.OUT_PP)
		self._cs_pin.high()

		self._last_temperature = 25.0
		self._config_reg = 0


	def detectSensor(self):
		self._cs_pin.low()
		pyb.delay(self.WAKE_UP_TIME)
		deviceID = ord(self.i2c.mem_read(1, self.SI7005_ADR, self.REG_ID))
		self._cs_pin.high()					# disable sensor

		if (deviceID & self.ID_SAMPLE) == self.ID_SI7005:
			return True
		else:
			return False


	def doMeasurement(self, configValue):
		self._cs_pin.low()					# enable sensor
		pyb.delay(self.WAKE_UP_TIME) 		# wait for wakeup

		self.i2c.mem_write(self.CONFIG_START | configValue | self._config_reg, self.SI7005_ADR, self.REG_CONFIG)	# start measure
		# TODO heater, fast measurement etc.

		measurementStatus = self.STATUS_NOT_READY		# while data not ready wait...
		while (measurementStatus & self.STATUS_NOT_READY):
			measurementStatus = ord(self.i2c.mem_read(1, self.SI7005_ADR, self.REG_STATUS))

		rawData = bytearray(2)	# format raw data
		rawData = (self.i2c.mem_read(2, self.SI7005_ADR, self.REG_DATA)[0]) << 8	# MSB
		rawData |= (self.i2c.mem_read(2, self.SI7005_ADR, self.REG_DATA)[1])		# LSB

		self._cs_pin.high() # disable sensor
		return rawData


	def getTemperature(self):
		rawTemperature = self.doMeasurement(self.CONFIG_TEMPERATURE) >> 2	# shift according to datasheet
		self._last_temperature = ( rawTemperature / self.TEMPERATURE_SLOPE ) - self.TEMPERATURE_OFFSET
		return self._last_temperature


	def getHumidity(self):
		rawHumidity = self.doMeasurement(self.CONFIG_HUMIDITY) >> 4		# shift according to datasheet
		curve = (rawHumidity / self.HUMIDITY_SLOPE) - self.HUMIDITY_OFFSET
		linearHumidity = curve - ( (curve * curve) * self.a2 + curve * self.a1 +  self.a0 )
		linearHumidity = linearHumidity + ( self._last_temperature - 30 ) * ( linearHumidity * self.q1 + self.q0 )
		return linearHumidity


	def enableHeater(self):
		self._config_reg |= self.CONFIG_HEAT


	def disableHeater(self):
		self._config_reg ^= self.CONFIG_HEAT


	def enableFastMeasurements(self):
		self._config_reg |= self.CONFIG_FAST


	def disableFastMeasurements(self):
		self._config_reg ^= self.CONFIG_FAST
