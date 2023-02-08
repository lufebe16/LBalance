#!/usr/bin/python
# -*- mode: python; coding: utf-8; -*-

import os
import logging

from LApp import LApp, LWorkWindow, LCircleView
from kivy.clock import Clock

import sensors
from smoother import Smoother
import time

#=============================================================================

class sensor_update(object):

	def __init__(self, reader, view):
		self.reader = reader
		self.view = view
		self.eventId = None
		self.smX = 0.0
		self.smY = 0.0
		self.smZ = 0.0
		self.smooth = Smoother(0.2)

	def run(self, dt):
		#logging.info("Appli: sensor run update")
		if self.reader is not None:
			r = self.reader
			self.smooth.updateTime(time.time())
			self.smX = self.smooth.updateValue(self.smX,r.sensorX)
			self.smY = self.smooth.updateValue(self.smY,r.sensorY)
			self.smZ = self.smooth.updateValue(self.smZ,r.sensorZ)
			#st = time.time()
			self.view.refresh(self.smX, self.smY, self.smZ)
			#et = time.time()
			#logging.info("Appli: view refresh: %s" % str(round(et-st,3)))


	def start_reading(self):
		logging.info("Appli: sensor start update")
		if self.reader is not None:
			self.reader.startListening(sensors.currentActivity)
		self.eventId = Clock.schedule_interval(self.run,0.05)

	def stop_reading(self):
		logging.info("Appli: sensor stop update")
		Clock.unschedule(self.eventId)
		if self.reader is not None:
			self.reader.stopListening()

#=============================================================================

class Appli(LApp):
	def __init__(self, **kw):
		super(Appli, self).__init__(**kw)
		if 'title' in kw:
			self.title = kw['title']
		self.view = None
		logging.info("Appli: __init__")
		self.sensor_update = None
		self.sensor_reader = None
		if sensors.SensorReader is not None:
			self.sensor_reader = sensors.SensorReader.getInstance()

	def on_start(self):
		logging.info("Appli: on_start")
		self.view = LWorkWindow()
		self.mainWindow.setWork(self.view)
		self.sensor_update = sensor_update(self.sensor_reader,self.view)
		self.sensor_update.start_reading()

	def on_stop(self):
		logging.info("Appli: on_stop")
		if self.sensor_update is not None:
			self.sensor_update.stop_reading()
		# Achtung wird u.U. 2 mal aufgerufen !!!

	def on_pause(self):
		logging.info("Appli: on_pause")
		if self.sensor_update is not None:
			self.sensor_update.stop_reading()

		# return True: wenn wir wirklich in pause gehen. Dann wird auch
		# resume aufgerufen falls die app wieder aktiviert wird.
		# return False: app wird gestoppt (on_stop wird aufgerufen)
		return True

	def on_resume(self):
		logging.info("Appli: on_resume")
		if self.sensor_update is not None:
			self.sensor_update.start_reading()

#=============================================================================

if __name__ == '__main__':

	logging.info("LApp: before run()")
	Appli(bmenu=False,bframe=False,title='wwtool').run()
	logging.info("LApp: after run()")

#=============================================================================
