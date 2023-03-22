#!/usr/bin/python
# -*- mode: python; coding: utf-8; -*-

import os
import logging
import time
import sensors

#=============================================================================
# Sprache konfigurieren.

import locale
import gettext

if 'LANG' not in os.environ:
	if sensors.jnius is not None:  # android
		Locale = sensors.jnius.autoclass('java.util.Locale')
		os.environ['LANG'] = Locale.getDefault().getLanguage()

locale.setlocale(locale.LC_ALL, '')

#=============================================================================

from kivy.clock import Clock

from LApp import LApp, LWorkWindow, LCircleView
import smoother

#=============================================================================

def int32(i):
	i = i & 0xffffffff
	if i > 0x80000000:
		return 0x80000000 - i
	return i

#=============================================================================

class sensor_update(object):

	def __init__(self, reader, view):
		self.reader = reader
		self.view = view
		self.eventId = None
		self.smX = 0.0
		self.smY = 0.0
		self.smZ = 0.0
		self.smooth = smoother.Smoother(0.1)
		self.lt = 0.0

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
			#logging.info("Appli: view duration: %s" % str(round(et-st,3)))
			#if self.lt > 0:
			#	logging.info("Appli: view invoke delta: %s" % str(round(st-self.lt,3)))
			#self.lt = st

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

		'''
		if sensors.jnius is not None:
			w = sensors.currentActivity.getWindow()
			print ('current window: ',w)
			if w is not None:
				# w.addFlags(-2147483648) # (-> geht nicht wir sind im falsche thread).
				w.setStatusBarColor(int32(0xff888888))
				w.setNavigationBarColor(int32(0xff777777))
				print ('current window, colors set')
		'''

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
