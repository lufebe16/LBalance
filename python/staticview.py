

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
		self.variante = 1
		self.msiz = None
		self.radius = None	# radisus of circle
		self.circle = None	# center of circle

		self.variants = []

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

	def get_radius(self):
		return self.radius

	def get_circle(self):
		return self.circle

	def on_touch_down(self, touch):
		# double tap
		if touch.is_double_tap:
			self.variante += 1
			self.variante = self.variante % 3
			self.update()
		return False

#=============================================================================

class LCircleViewSimple(LCircleView):

	def __init__(self,**kw):
		super(LCircleViewSimple, self).__init__(**kw)

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

	def draw(self):
		angle = None
		self.radius = 0.9*self.msiz/2
		fs = LFont.small()
		step = self.radius / 45
		c = self.center
		r = self.radius
		m = self.msiz/2

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

class StaticViews(object):

	def __init__(self):
		# Liste der verfügbaren Klassen.
		self.views = []
		self.views.append(LCircleViewSimple)
		self.views.append(LCircleViewFine)
		self.views.append(LCircleViewFineWithScale)

	def count(self):
		return len(self.views)

	def view(self,index):
		# neue Instanz erzeugen und zurückgeben.
		return self.views[index]()

#=============================================================================
