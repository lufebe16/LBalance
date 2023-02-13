

import math
from koords import LValue

#=============================================================================

class LCala(object):

	def __init__(self):
		self.cala_angle = 0.0		# durchschnit gemessener abweichungen.
		self.cala_cnt = 0				# anzahl werte

	def reset(self):
		self.cala_angle = 0.0
		self.cala_cnt = 0

	def addValue(self,angle,soll):
		self.cala_cnt += 1
		delta = angle-soll
		# wir berechnen die resultierende Abweichung
		self.cala_angle = ((self.cala_cnt-1)*self.cala_angle + delta) / self.cala_cnt

	def getValue(self):
		# wir geben den Korrekturwert zurück
		return -self.cala_angle;

	def getCount(self):
		return self.cala_cnt;

#=============================================================================

class LCalaStore(object):

	def __init__(self):
		self.store = {}
		self.accept_one = False

	def reset(self):
		self.store = {}
		self.accept_one = False
		print ("LCalaStore: reset()")

	def accept(self):
		self.accept_one = True
		print ("LCalaStore: accept()")

	def numCalibrated(self,values):
		ori = values.orientation()
		if ori not in self.store: return 0

		cntX = self.store[ori]['X'].getCount()
		cntY = self.store[ori]['Y'].getCount()
		return max(cntX,cntY)

	def isCalibrated(self,values):
		ori = values.orientation()
		if ori not in self.store: return None

		valX = round(self.store[ori]['X'].getValue(),1)
		valY = round(self.store[ori]['Y'].getValue(),1)
		valZ = 0.0
		vz2 = values.g*values.g-valX*valX-valY*valY
		if vz2 > 0.0:
			valZ = round(values.g-math.sqrt(vz2),1)

		return str(valX)+'/'+str(valY)+'/'+str(valZ)

	def addCalibration(self,rawValue):
		if not self.accept_one: return

		ori = rawValue.orientation()
		if  ori not in self.store:
			self.store[ori] = { 'X':LCala(),'Y':LCala() }
		if ori in ["LANDING","FLYING"]:
			self.store[ori]['X'].addValue(rawValue.valX,0)
			self.store[ori]['Y'].addValue(rawValue.valY,0)
		elif ori in ["TOP","BOTTOM"]:
			self.store[ori]['X'].addValue(rawValue.valX,0)
		else:
			self.store[ori]['Y'].addValue(rawValue.valY,0)
		print ("LCalaStore: new value added")
		self.accept_one = False

	def calibrate(self,rawValue):
		ori = rawValue.orientation()
		if ori not in self.store: return rawValue

		valX = self.store[ori]['X'].getValue()
		valY = self.store[ori]['Y'].getValue()
		# die Korrektur der z-Komponente errechnet sich über g.
		valZ = 0.0
		vz2 = rawValue.g*rawValue.g-valX*valX-valY*valY
		if vz2 > 0.0:
			valZ = rawValue.g-math.sqrt(vz2)

		return LValue(rawValue.valX+valX,rawValue.valY+valY,rawValue.valZ+valZ)

	def handleCalibration(self,rawValue):
		self.addCalibration(rawValue)
		return self.calibrate(rawValue)

#=============================================================================
