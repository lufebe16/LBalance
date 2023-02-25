

from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.graphics import *

from graphics import rotated_text, LFont, set_color

#=============================================================================
# Definiert den App Hintergrund.

class LCircleView(Widget):

	val_ori = StringProperty("LANDING")

	def __init__(self,**kw):
		super(LCircleView, self).__init__(**kw)

		self.bind(pos=self.update)
		self.bind(size=self.update)
		self.update_event = None
		self.msiz = 0
		self.radius = 0.0
		self.circle = (0.0,0.0)

	def update(self, *args):
		Clock.unschedule(self.update_event)
		self.update_event = Clock.schedule_once(self.update_scheduled, 0.2)

	def update_scheduled(self, *args):
		#print("CircleView (center):",self.center)
		self.msiz = msiz = min(self.size[0],self.size[1])
		self.radius = msiz/2.0
		self.circle = center = (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)

		self.canvas.before.clear()
		with self.canvas.before:
			self.draw()

	def draw(self):
		# TB supplied by derived classes
		pass

	def on_val_ori(self,*args):
		# TBI in derived class if needed
		pass

	def get_tacho_center(self):
		# TBI in derived class if needed
		pass

	def get_tacho_radius(self):
		# TBI in derived class if needed
		pass

	def get_tacho_angle(self):
		# TBI in derived class if needed
		pass

	def get_meter_center(self):
		# TBI in derived class if needed
		return self.get_tacho_center()

	def get_meter_length(self):
		# TBI in derived class if needed
		return self.get_tacho_radius()

	def get_meter_angle(self):
		# TBI in derived class if needed
		return self.get_tacho_angle()

#=============================================================================

class LCircleViewSimple(LCircleView):

	def __init__(self,**kw):
		super(LCircleViewSimple, self).__init__(**kw)

	def get_tacho_center(self):
		return self.center

	def get_tacho_radius(self):
		return self.radius

	def get_tacho_angle(self):
		return 0

	def draw(self):
		c = self.center
		r = self.radius

		set_color([0.0, 0.1, 0.0, 1])   # violett
		Rectangle(pos=self.pos, size=self.size)
		set_color([1, 0.1, 0.1, 1])   # violett
		step = r / 45
		for i in range(5,45,10):
			Line(circle=(c[0],c[1],i*step),width=0.5)
		Line(circle=(c[0],c[1],45*step),width=0.7)

#=============================================================================

class LCircleViewFine(LCircleView):

	def __init__(self,**kw):
		super(LCircleViewFine, self).__init__(**kw)

	def get_tacho_center(self):
		return self.center

	def get_tacho_radius(self):
		return self.radius

	def get_tacho_angle(self):
		return 0

	def draw(self):
		c = self.center
		r = self.radius

		Color(0.7, 0.7, 0.7, 1)   # hellgrau
		step = r / 45
		for i in range(5,45,5):
			Line(circle=(c[0],c[1],i*step),width=0.5)
		Line(circle=(c[0],c[1],45*step),width=0.7)

#=============================================================================

class LCircleViewFineWithScale(LCircleView):

	def __init__(self,**kw):
		super(LCircleViewFineWithScale, self).__init__(**kw)
		self.last_val_ori = None

	def on_val_ori(self,*args):
		if (self.last_val_ori in ['TOP','LEFT']) != (args[1] in ['TOP','LEFT']):
			self.update()
		self.last_val_ori = self.val_ori

	def get_tacho_center(self):
		return self.center

	def get_tacho_radius(self):
		return self.radius

	def get_tacho_angle(self):
		return 0

	def draw(self):
		angle = None
		self.radius = 0.9*self.msiz/2
		fs = LFont.small()
		step = self.radius / 45
		c = self.center
		r = self.radius
		m = self.msiz/2

		set_color([0.0, 0.1, 0.0, 1])   # black
		Rectangle(pos=self.pos, size=self.size)

		# beschriftungs richtung
		axis_dir = 1
		if self.val_ori in ['LEFT','TOP']: axis_dir = -1

		# circles
		Color(0.7, 0.7, 0.7, 1)   # hellgrau
		for i in range(5,45,5):
			Line(circle=(c[0],c[1],i*step),width=0.5)
		Line(circle=(c[0],c[1],45*step),width=0.7)

		# lines
		for i in range(-45,46,1):
			if i % 10 == 0:
				Line(points=[c[0]-m,c[1]+i*step,c[0]-r,c[1]+i*step],width=0.5)
				Line(points=[c[0]+m,c[1]+i*step,c[0]+r,c[1]+i*step],width=0.5)
				Line(points=[c[0]+i*step,c[1]-m,c[0]+i*step,c[1]-r],width=0.5)
				Line(points=[c[0]+i*step,c[1]+m,c[0]+i*step,c[1]+r],width=0.5)
			elif i % 5 == 0:
				Line(points=[c[0]-m+5,c[1]+i*step,c[0]-r,c[1]+i*step],width=0.5)
				Line(points=[c[0]+m-5,c[1]+i*step,c[0]+r,c[1]+i*step],width=0.5)
				Line(points=[c[0]+i*step,c[1]-m+5,c[0]+i*step,c[1]-r],width=0.5)
				Line(points=[c[0]+i*step,c[1]+m-5,c[0]+i*step,c[1]+r],width=0.5)
			else:
				Line(points=[c[0]-m+15,c[1]+i*step,c[0]-r,c[1]+i*step],width=0.5)
				Line(points=[c[0]+m-15,c[1]+i*step,c[0]+r,c[1]+i*step],width=0.5)
				Line(points=[c[0]+i*step,c[1]-m+15,c[0]+i*step,c[1]-r],width=0.5)
				Line(points=[c[0]+i*step,c[1]+m-15,c[0]+i*step,c[1]+r],width=0.5)

		# text
		for i in range(-45,46,1):
			if i % 10 == 0:
				if angle is not None:
					rotated_text(str(i*axis_dir),c[0]-r,c[1]+i*step,font_size=fs,angle=angle)
					rotated_text(str(i*axis_dir),c[0]+r,c[1]+i*step,font_size=fs,angle=angle)
					rotated_text(str(i*axis_dir),c[0]+i*step,c[1]-r,font_size=fs,angle=angle)
					rotated_text(str(i*axis_dir),c[0]+i*step,c[1]+r,font_size=fs,angle=angle)
				else:
					rotated_text(str(i*axis_dir),c[0]-r,c[1]+i*step,font_size=fs,angle=90)
					rotated_text(str(i*axis_dir),c[0]+r,c[1]+i*step,font_size=fs,angle=-90)
					rotated_text(str(i*axis_dir),c[0]+i*step,c[1]-r,font_size=fs,angle=180)
					rotated_text(str(i*axis_dir),c[0]+i*step,c[1]+r,font_size=fs,angle=0)

#=============================================================================

class LCircleViewAV(LCircleView):

	def __init__(self,**kw):
		super(LCircleViewAV, self).__init__(**kw)
		self.d = 0.2
		self.w = 1.4
		self.h = 6.1
		self.n = 8.1

	def on_val_ori(self,*args):
		self.update()
		self.last_val_ori = self.val_ori

	def calcLin(self):
		for i in range(-44,45,2):
			set_color([0,0,0,1])
			if i % 10 == 0:
				Line(points=[i,0,i,3],width=0.12)
			else:
				Line(points=[i,0,i,1.5],width=0.12)

	def calcSkala(self):
		self.calcLin()
		PushMatrix()
		Rotate(angle=180.0,origin=(0,0))
		self.calcLin()
		PopMatrix()
		PushMatrix()
		Translate(0,10)
		Rotate(angle=180.0,origin=(0,0))
		self.calcLin()
		PopMatrix()
		PushMatrix()
		Translate(0,-10)
		self.calcLin()
		PopMatrix()
		Line(points=[-45,0,45,0],width=0.12)

	def calcCircle(self):
		for i in range(0,50,5):
			Line(circle=(0,0,i),width=0.12)
		Line(points=[-50,0,50,0],width=0.12)
		Line(points=[0,-50,0,50],width=0.12)

	def picture(self,colorc,color1,color2):
		d = self.d
		w = self.w
		h = self.h
		set_color(colorc) # gelb
		Ellipse(pos=(2*d+w,d),size=(6.1,6.1))
		set_color(color1)
		Rectangle(pos=(d,d),size=(w,h))
		set_color(color2)
		Rectangle(pos=(2*d+w,2*d+h),size=(h,w))

		PushMatrix()
		Translate(2*d+w+h/2,2*d+h+w/2.0)
		Scale(6.1/90.0,origin=(0,0))
		self.calcSkala()
		PopMatrix()

		PushMatrix()
		Translate(d+w/2,d+h/2.0)
		Rotate(angle=90.0,origin=(0,0))
		Scale(6.1/90.0,origin=(0,0))
		self.calcSkala()
		PopMatrix()

		PushMatrix()
		Translate(2*d+w+h/2,d+h/2.0)
		Scale(6.1/90.0,origin=(0,0))
		self.calcCircle()
		PopMatrix()

	def draw(self):
		c = self.center
		r = self.radius

		white = [0.92,0.92,0.92,1]
		yellow = [1.0,0.92,0.0,1]
		colorc = white
		color1 = white
		color2 = white
		if self.val_ori in ['LANDING','FLYING']:
			colorc = yellow
		elif self.val_ori in ['BOTTOM','TOP']:
			color1 = yellow
		else:
			color2 = yellow

		set_color([0.0, 0.1, 0.0, 1])   # black
		Rectangle(pos=self.pos, size=self.size)

		# RandLinie
		set_color([1.0, 1, 1.0, 1])   # violett
		m = self.msiz/2.0
		t = 2.0
		Line(points=(
			c[0]-m+t,c[1]-m+t,
			c[0]+m-t,c[1]-m+t,
			c[0]+m-t,c[1]+m-t,
			c[0]-m+t,c[1]+m-t,
			c[0]-m+t,c[1]-m+t),
			width=2.0*t)

		PushMatrix()
		if (self.size[0]<self.size[1]):
			Translate(0,self.pos[1]+(self.size[1]/2.0-m))
			Scale(2.0*m/8.1,origin=(0,0))
			self.picture(colorc,color2,color1)
		else:
			Translate(self.pos[0]+self.size[0]/2.0+m,0)
			Scale(2.0*m/8.1,origin=(0,0))
			Rotate(angle=90.0,origin=(0,0))
			self.picture(colorc,color1,color2)
		PopMatrix()

	def get_tacho_center(self):
		c = self.center
		m = self.msiz/2.0
		if (self.size[0]<self.size[1]):
			return (c[0]-m+2.0*m*(2*self.d+self.w+self.h/2.0)/self.n,
							c[1]-m+2.0*m*(self.d+self.h/2.0)/self.n)
		else:
			return (c[0]-m+2.0*m*(2*self.d+self.w+self.h/2.0)/self.n,
							c[1]-m+2.0*m*(2*self.d+self.w+self.h/2.0)/self.n)
		return self.center

	def get_tacho_radius(self):
		return self.h/2.0 * self.msiz/self.n

	def get_tacho_angle(self):
		return 0

	def get_meter_center(self):
		c = self.center
		m = self.msiz/2.0
		if self.val_ori in ['BOTTOM','TOP']:
			if (self.size[0]<self.size[1]):
				return (c[0]-m+2.0*m*(2*self.d+self.w+self.h/2.0)/self.n,
								c[1]-m+2.0*m*(2*self.d+self.h+self.w/2.0)/self.n)
			else:
				return (c[0]-m+2.0*m*(2*self.d+self.w+self.h/2.0)/self.n,
								c[1]-m+2.0*m*(self.d+self.w/2.0)/self.n)

		elif self.val_ori in ['LEFT','RIGHT']:
			if (self.size[0]<self.size[1]):
				return (c[0]-m+2.0*m*(self.d+self.w/2.0)/self.n,
								c[1]-m+2.0*m*(self.d+self.h/2.0)/self.n)
			else:
				return (c[0]-m+2.0*m*(self.d+self.w/2.0)/self.n,
								c[1]-m+2.0*m*(2*self.d+self.w+self.h/2.0)/self.n)

		return self.get_tacho_center()

	def get_meter_length(self):
		return self.get_tacho_radius()

#=============================================================================

from kivy.graphics.scissor_instructions import ScissorPush, ScissorPop

class LCircleViewBA(LCircleView):

	def __init__(self,**kw):
		super(LCircleViewBA, self).__init__(**kw)

	def draw(self):
		#ScissorPush(
		#	x=self.pos[0],y=self.pos[1],width=self.size[0],height=self.size[1])

		set_color([0.02, 0.02, 0.02, 1])   # black
		Rectangle(pos=self.pos, size=self.size)

		set_color([0.2, 0.2, 0.2, 1])   # grau
		r = self.get_tacho_radius()
		c = self.get_tacho_center()
		step = r / 45
		for i in range(5,46,5):
			Line(circle=(c[0],c[1],i*step),width=1.5)
		Line(circle=(c[0],c[1],45*step),width=1.5)

		set_color([0.1, 0.1, 0.1, 0.5])   # grau
		Line(circle=(c[0],c[1],277),width=50)

		#ScissorPop()

	def get_tacho_center(self):
		return self.center

	def get_tacho_radius(self):
		#return self.radius/3
		#return self.radius
		return self.radius*3.0

#=============================================================================

class StaticViews(object):

	def __init__(self):
		# Liste der verfügbaren Klassen.
		self.views = []
		self.views.append(LCircleViewSimple)
		self.views.append(LCircleViewFine)
		self.views.append(LCircleViewFineWithScale)
		self.views.append(LCircleViewAV)

	def count(self):
		return len(self.views)

	def view(self,index):
		# neue Instanz erzeugen und zurückgeben.
		return self.views[index]()

#=============================================================================
