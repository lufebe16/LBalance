


import math

# =============================================================================
# helpers.

# ANM: Wir verwenden die in der Physik gebräuchlichen Polarkoordinaten.
# Dabei ist:
#  theta:
#    der Winkel zwischen dem Vektor (Erdbeschleunigung g) und der
#    z-Achse (Bereich 0..180 Grad).
#    (Die Erdwissenschafter defniern statt dessen die
#    geographische Breite, entsprechend 90-theta, Bereich -90..90.)
#  phi:
#    der Ebenenwinkel zur Projektion entlang der z-Achse des Vektors
#    auf die xy-Ebene (Bereich -180..180).

def kart(r,phi,theta):
	z = r * math.cos(theta)
	rxy = math.sqrt(r*r - z*z)
	x = rxy * math.cos(phi)
	y = rxy * math.sin(phi)
	return x,y,z

def kartDeg(r,phi,theta):
	return kart (r,math.radians(phi),math.radians(theta))

def polar(x,y,z):
	phi = 0.0
	theta = 0.0
	r = math.sqrt(x*x+y*y+z*z)
	if r!=0.0:
		phi = math.atan2(y,x);
		theta = math.acos(z/r)
	return r,phi,theta

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

		#print ('g,phi,theta',self.g,self.phi,self.theta)

		def norm45(angle):
			angle = normAngle(angle)
			if angle < -45: angle = -45
			if angle > 45: angle = 45
			return angle

		theta = self.theta
		phi = self.phi

		self.bala = 0.0
		self.ori = "LANDING"
		if (theta < 45.0):
			self.ori = "LANDING"
			self.bala = norm45(theta)
		elif (theta > 135.0):
			self.ori = "FLYING"
			self.bala = norm45(-theta)
		elif (phi < 135.0 and phi > 45.0):
			self.ori = "BOTTOM"
			self.bala = norm45(90.0-phi)
		elif (phi < 45.0 and phi > -45.0):
			self.ori = "LEFT"
			self.bala = norm45(-phi)
		elif (phi < -45.0 and phi > -135.0):
			self.ori = "TOP"
			self.bala = norm45(-90.0-phi)
		elif (phi > 135.0 or phi < -135.0):
			self.ori = "RIGHT"
			self.bala = norm45(180.0-phi)

	def pitch(self):
		return self.pitchExt()

	def roll(self):
		return self.rollExt()

	def pitchExt(self):
		th = self.theta
		if th > 90: th = (180 - th)
		reta = th * math.sin(math.radians(self.phi))
		return reta

	def rollExt(self):
		th = self.theta
		if th > 90: th = (180 - th)
		reta = th * math.cos(math.radians(self.phi))
		return reta

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
