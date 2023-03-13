


import math

# =============================================================================
# helpers.

def kart(r,phi,theta):
	#z = r * math.cos(theta)
	# -> das system mit theta (KS d. dtheoret. Physik)
	z = r * math.sin(theta)
	# -> das system mit gross phi statt theta (geografisches KS)
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
	# -> das system mit gross phi statt theta (geografisches KS)
	print('1',theta)
	r = math.sqrt(x*x+y*y+z*z)
	#theta = math.acos(z/r)
	# -> das system mit theta (KS d. dtheoret. Physik)
	print('2',theta)
	return r,phi,theta

	# hab da einen heillosen durcheinander angerichtet !!!
	# bei der polarumwandlung wurde das geografische verwendet -
	# und bei der kartesischen ubwandlung das physikalische.

	# -> nun wurde die kart. korrigiert. Bendingte nur eine Aenderung LApp.py.)
	# so ist es wenigstens konsistent jetzt.

	# -> aber eigentlich wollte ich das physikalsche verwenden !

def polarDeg(x,y,z):
	r,phi,theta = polar(x,y,z)
	return r,math.degrees(phi),math.degrees(theta)

# =============================================================================

def normAngle360signed(angle):
	angle = angle % 360.0
	# REM: Modulo funktion ist heikel, da untesrchiedliche Implementationen
	# existieren. python benutzt 'floored divison': Das Resultat hat das
	# Vorzeichen vom Divisor. Im Gegensatz dazu verwendet math.fmod
	# 'truncated deivision': Da erbt das Resultat das Vorzeichen vom Dividenden
	# (wie auch in Java). Nach Wikipedia gibt es noch 3 weitere Verfahren,
	# um modulo zu berechnen, jede mit unterschiedlichem Resultat!. ('Floored'
	# und 'truncated' sind am weitesten verbreitet.).
	if angle >= 180.0: angle -= 360.0
	return angle

# =============================================================================

def normAngle(angle):
	angle = normAngle360signed(angle)
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

		#self.theta = 90-self.theta

		print ('g,phi,theta',self.g,self.phi,self.theta)

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

	def pitchExt(self):
		theta = self.theta
		if self.valZ < 0.0:
			if theta > 0: theta = 180 - theta
			if theta < 0: theta = -180 - theta
		return (90.0-math.fabs(theta)) * math.sin(math.radians(self.phi))

	def rollExt(self):
		theta = self.theta
		if self.valZ < 0.0:
			if theta > 0: theta = 180 - theta
			if theta < 0: theta = -180 - theta
		return (90.0-math.fabs(theta)) * math.cos(math.radians(self.phi))

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
