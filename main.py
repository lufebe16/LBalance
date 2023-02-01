#!/usr/bin/python
# -*- mode: python; coding: utf-8; -*-

import os
#print ('KIVY_HOME: '+os.environ['KIVY_HOME'])
import time
import math

import logging

from LApp import LApp, LWorkWindow, LCircleView

from kivy.uix.label import Label
from kivy.clock import Clock

import sensors

#=============================================================================

class sensor_update(object):

	def __init__(self, reader, view):
		self.reader = reader
		self.view = view
		self.eventId = None

	def orientation(self,phi,theta):
		# evaluation
		if (theta > 45.0):
			return "LANDING"
		if (theta < -45.0):
			return "FRONT"
		if (phi < 135.0 and phi > 45.0):
			return "TOP"
		if (phi < 45.0 and phi > -45.0):
			return "RIGHT"
		if (phi < -45.0 and phi > -135.0):
			return "BOTTOM"
		if (phi > 135.0 or phi < -135.0):
			return "LEFT"
		# fallback
		return "LANDING"

	def run(self, dt):
		#logging.info("Appli: sensor run update")
		if self.reader is not None:
			result = self.reader.getCurrentValues()
			phi = result.rawPhi
			theta = result.rawTheta
			ori = self.orientation(phi,theta)
			# handle calibration
			#self.view.refresh(phi,theta)
			self.view.refresh(result)

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
