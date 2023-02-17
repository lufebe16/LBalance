

import math
from koords import LValue
import json

#=============================================================================

from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

class LCalaStore(EventDispatcher):

	cala_state = ObjectProperty()

	def __init__(self):
		self.store = {}
		self.accept_one = False
		self.last_ori = None
		self.load()

	def reset(self):
		self.store = {}
		self.accept_one = False
		print ("LCalaStore: reset()")
		self.save()

	def accept(self):
		self.accept_one = True
		print ("LCalaStore: accept()")

	def numCalibrated(self,values):
		ori = values.orientation()
		if ori not in self.store: return 0

		cntX = len(self.store[ori]['X'])
		cntY = len(self.store[ori]['Y'])
		return max(cntX,cntY)

	def addCalibration(self,rawValue):
		if not self.accept_one: return False

		ori = rawValue.orientation()
		if  ori not in self.store:
			self.store[ori] = { 'X': [],'Y': [] }
		if ori in ["LANDING","FLYING"]:
			self.store[ori]['X'].append(rawValue.valX)
			self.store[ori]['Y'].append(rawValue.valY)
		elif ori in ["TOP","BOTTOM"]:
			self.store[ori]['X'].append(rawValue.valX)
		else:
			self.store[ori]['Y'].append(rawValue.valY)

		print ("LCalaStore: new value added")
		self.accept_one = False
		return True

	def calibrate(self,rawValue):
		ori = rawValue.orientation()
		if ori not in self.store: return rawValue

		valX = 0.0
		lX = len(self.store[ori]['X'])
		if lX > 0:
			valX = -sum(self.store[ori]['X']) / lX
		valY = 0.0
		lY = len(self.store[ori]['Y'])
		if lY > 0:
			valY = -sum(self.store[ori]['Y']) / lY

		# die Korrektur der z-Komponente errechnet sich über g.
		valZ = 0.0
		vz2 = rawValue.g*rawValue.g-valX*valX-valY*valY
		if vz2 > 0.0:
			valZ = rawValue.g-math.sqrt(vz2)

		self.save()
		return LValue(rawValue.valX+valX,rawValue.valY+valY,rawValue.valZ+valZ)

	def handleCalibration(self,rawValue):
		chg = self.addCalibration(rawValue)
		if chg or self.last_ori != rawValue.orientation():
			self.cala_state = rawValue
		return self.calibrate(rawValue)

	def save(self):
		try:
			fp = open("ww_cala.json","w")
			json.dump(self.store,fp)
		except:
			pass

	def load(self):
		try:
			fp = open("ww_cala.json","r")
			self.store = json.load(fp)
		except:
			pass

#=============================================================================

CalaStore = LCalaStore()

#=============================================================================
