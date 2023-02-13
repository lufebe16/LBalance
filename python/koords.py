


import math

# =============================================================================
# helpers.

def kart(r,phi,theta):
	z = r * math.cos(theta)
	rxy = math.sqrt(r*r - z*z)
	x = rxy * math.cos(phi)
	y = rxy * math.sin(phi)
	return x,y,z

def kartDeg(r,phi,theta):
	return kart (r,math.radians(phi),math.radians(theta))

def polar(x,y,z):
	rxy = math.sqrt(x*x+y*y)
	phi = math.atan2(y,x);
	theta = math.atan2(z,rxy)
	r = math.sqrt(x*x+y*y+z*z)
	return r,phi,theta

def polarDeg(x,y,z):
	r,phi,theta = polar(x,y,z)
	return r,math.degrees(phi),math.degrees(theta)

# =============================================================================

def normAngle(angle):
	while angle < -180.0: angle += 360.0
	while angle >= 180.0: angle -=360.0
	if angle > 90.0: angle = 180.0 - angle
	if angle < -90.0: angle = -180.0 - angle
	return angle

# =============================================================================

class LValue(object):

	def __init__(self,valX,valY,valZ):

		self.valX = valX
		self.valY = valY
		self.valZ = valZ
		self.g,self.phi,self.theta = polarDeg(valX,valY,valZ)
		#print (self.g,self.phi,self.theta)

		def norm45(angle):
			angle = normAngle(angle)
			if angle < -45: angle = -45
			if angle > 45: angle = 45
			return angle

		self.bala = 0.0
		self.ori = "LANDING"
		if (self.theta > 45.0):
			self.ori = "LANDING"
			self.bala = norm45(90.0-self.theta)
		elif (self.theta < -45.0):
			self.ori = "FLYING"
			self.bala = norm45(-90.0-self.theta)
		elif (self.phi < 135.0 and self.phi > 45.0):
			self.ori = "BOTTOM"
			self.bala = norm45(90.0-self.phi)
		elif (self.phi < 45.0 and self.phi > -45.0):
			self.ori = "LEFT"
			self.bala = norm45(-self.phi)
		elif (self.phi < -45.0 and self.phi > -135.0):
			self.ori = "TOP"
			self.bala = norm45(-90.0-self.phi)
		elif (self.phi > 135.0 or self.phi < -135.0):
			self.ori = "RIGHT"
			self.bala = norm45(180.0-self.phi)

	def pitch(self):
		return (90.0-math.fabs(self.theta)) * math.sin(math.radians(self.phi))

	def roll(self):
		return (90.0-math.fabs(self.theta)) * math.cos(math.radians(self.phi))

	def balance(self):
		return self.bala

	def orientation(self):
		return self.ori

	def xy(self):
		x = 0.0
		y = 0.0
		if self.ori=="LANDING":
			x = self.roll()
			y = self.pitch()
		elif self.ori=="FLYING":
			x = self.roll()
			y = self.pitch()
		elif self.ori=="TOP":
			x = -self.bala
			y = 0
		elif self.ori=="BOTTOM":
			x = self.bala
			y = 0
		elif self.ori=="LEFT":
			y = -self.bala
			x = 0
		elif self.ori=="RIGHT":
			y = self.bala
			x = 0
		return x,y

	def txtori(self):
		txtori = 0.0
		if self.ori=="TOP":
			txtori = 180.0
		elif self.ori=="LEFT":
			txtori = -90.0
		elif self.ori=="RIGHT":
			txtori = 90.0
		return txtori

#=============================================================================
