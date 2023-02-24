
import math

#=============================================================================

class Smoother(object):

	def __init__(self, halfLive = 1.0, wmin = None, wmax = None):
		self.lastTime = None
		self.lastDelta = None
		self.beta = 0.0
		self.half = halfLive
		self.range = 0.0
		self.rangeHalf = 0.0
		self.rangeMin = 0.0
		self.rangeMax = 0.0
		if wmin is not None and wmax is not None:
			self.range = wmax - wmin
			self.rangeHalf = self.range / 2.0
			self.rangeMin = wmin
			self.rangeMax = wmax

	def updateTime(self, curTime):
		if self.lastTime is not None:
			self.lastDelta = curTime-self.lastTime
			self.beta = math.pow(0.5,self.lastDelta/self.half)
			print('last',self.lastTime,'cur',curTime,'delta',self.lastDelta,'beta',self.beta)
		self.lastTime = curTime

	def norm(self, value):
		while (value < self.rangeMin): value += self.range
		while (value >= self.rangeMax): value -= self.range
		return value

	def updateValue(self, smoothed, raw):
		b = self.beta;
		if (math.isnan(raw)): return smoothed
		if (math.isnan(smoothed)): b = 0.0

		if (self.range != 0.0):
			s = self.norm(smoothed);
			r = self.norm(raw);
			d = s - r;
			if (d > self.rangeHalf):
				d = self.range - d;
				return self.norm((self.range - b*d) + r)

			if (d < -rangeHalf):
				d = -self.range - d
				return self.norm((-self.range - b*d) + r)

			return self.norm(b*d + r)
		else:
			return b*(smoothed-raw) + raw


#=============================================================================

class Mean(object):

	def __init__(self, nvalues):
		self.nvalues = nvalues
		self.values = []

	def add_value(self,value):
		self.values.append(value)
		if len(self.values) > nvalues:
			del self.values[0]

	def get_mean(self):
		mean = 0
		if len(self.values) > 0:
			mean = sum(self.values) / len(self.values)
		return mean

#=============================================================================

