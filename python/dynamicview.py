

import math

from kivy.graphics import *
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

from graphics import set_color, set_color_range, baloon, triangle, rotated_text

#=============================================================================
# Definiert den App Vordergrund

class LAngleView(BoxLayout):
	def __init__(self,**kw):
		super(LAngleView, self).__init__(**kw)
		with self.canvas.before:
			#Color(0, 0.00, 0.3, 1)   # schwarz mit blau stich
			Color(0.15, 0.00, 0.3, 1)   # schwarz mit violett stich
			self.rect = Rectangle(pos=self.pos, size=self.size)

		self.bind(pos=self.update)
		self.bind(size=self.update)
		self.update_event = None
		self.bckgnd = None
		self.val_ori = None
		self.last_phi = 0.0
		self.last_theta = 0.0

	def update(self,*args):
		Clock.unschedule(self.update_event)
		self.update_event = Clock.schedule_once(self.update_scheduled, 0.2)

	def update_scheduled(self,*args):
		self.rect.pos = self.pos
		self.rect.size = self.size
		#print("LAngleView (pos): ",self.pos)
		#print("LAngleView (size): ",self.size)
		#print("LAngleView (center): ",self.center)

	def set_background(self,bckgnd):
		self.clear_widgets()
		self.bckgnd = bckgnd
		self.add_widget(bckgnd)

	def present(self,value):
		# orientierungsänderung weiterleiten.
		if self.val_ori != value.orientation():
			self.val_ori = value.orientation()
			self.bckgnd.val_ori = self.val_ori

		if math.fabs(self.last_phi-value.phi) < 0.005: return
		self.last_phi = value.phi
		if math.fabs(self.last_theta-value.theta) < 0.005: return
		self.last_theta = value.theta

		# Vordergrund neu zeichnen.
		self.canvas.after.clear()
		with self.canvas.after:
			self.draw(value)

	def draw(self,value):
		# Implementation in derived classes.
		pass

	def on_touch_down(self, touch):
		# double tap
		if touch.is_double_tap:
			for c in self.children:
				c.on_touch_down(touch)
		return False

	def balance_label(self,balance,txtangle,color):
		lbx = self.size[0]/2.0
		#lby = (self.size[1]-msiz)/4.0
		lby = self.size[1]/12
		if self.size[0] > self.size[1]:
			lby = self.size[1]/2.0
			#lbx = self.size[0]-(self.size[0]-msiz)/4.0
			lbx = self.right - self.size[0]/12
		rotated_text("{0: 5.2f}\u00b0".format(balance),
				lbx,lby,txtangle,font_size=72,color=color)

#=============================================================================

class LAngleViewSimple(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewSimple, self).__init__(**kw)

	def draw(self,value):

		radius = self.bckgnd.get_radius()
		circle = self.bckgnd.get_circle()

		balance = value.balance()
		txtangle = value.txtori()
		x,y = value.xy()
		x = x*radius/45.0 + circle[0]
		y = y*radius/45.0 + circle[1]

		cx = circle[0]
		cy = circle[1]
		alf = math.atan2(y-cy,x-cx)
		xv = radius * math.cos(alf) + cx
		yv = radius * math.sin(alf) + cy
		xh = radius * math.cos(alf+math.pi) + cx
		yh = radius * math.sin(alf+math.pi) + cy
		xl = radius * math.cos(alf-math.pi/2.0) + cx
		yl = radius * math.sin(alf-math.pi/2.0) + cy
		xr = radius * math.cos(alf+math.pi/2.0) + cx
		yr = radius * math.sin(alf+math.pi/2.0) + cy

		self.balance_label(balance,txtangle,[0.7,0.7,0.7,1])

		good = 5.0
		set_color_range(
			[0.5,1.0,0.0,0.6],[1.0,0.6,0.0,0.7],math.fabs(value.balance())/good)

		if value.orientation() in ["LANDING","FLYING"]:
			#Line(points=[x,y, 2*cx-x, 2*cy-y],width=2.0)
			if balance>0.1:
				Line(points=[xv,yv,xh,yh],width=2.0)
		else:
			Line(points=[xv,yv,xh,yh],width=2.0)

		PushMatrix()
		Translate(x,y)
		Rotate(angle=value.phi,origin=(0,0))
		Scale(2.0*radius/9.0,origin=(0,0))
		baloon()
		PopMatrix()

#=============================================================================

class LAngleViewTriangle(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewTriangle, self).__init__(**kw)

	def draw(self,value):
		radius = self.bckgnd.get_radius()
		circle = self.bckgnd.get_circle()

		balance = value.balance()
		txtangle = value.txtori()
		x,y = value.xy()
		x = x*radius/45.0 + circle[0]
		y = y*radius/45.0 + circle[1]

		cx = circle[0]
		cy = circle[1]
		alf = math.atan2(y-cy,x-cx)
		xv = radius * math.cos(alf) + cx
		yv = radius * math.sin(alf) + cy
		xh = radius * math.cos(alf+math.pi) + cx
		yh = radius * math.sin(alf+math.pi) + cy
		xl = radius * math.cos(alf-math.pi/2.0) + cx
		yl = radius * math.sin(alf-math.pi/2.0) + cy
		xr = radius * math.cos(alf+math.pi/2.0) + cx
		yr = radius * math.sin(alf+math.pi/2.0) + cy

		self.balance_label(balance,txtangle,[0.7,0.7,0.7,1])

		good = 5.0
		set_color_range(
			[0.5,1.0,0.0,0.6],[1.0,0.6,0.0,0.7],math.fabs(balance)/good)
		#self.center_color(balance)

		if value.orientation() in ["LANDING","FLYING"]:
			x4 = radius/9.0 * math.cos(alf+math.pi) + cx
			y4 = radius/9.0 * math.sin(alf+math.pi) + cy
			x2 = radius * math.cos(alf-math.pi/2.0) + cx
			y2 = radius * math.sin(alf-math.pi/2.0) + cy
			x1 = radius * math.cos(alf+math.pi/2.0) + cx
			y1 = radius * math.sin(alf+math.pi/2.0) + cy
			if abs(balance) > 0.1:
				Line(points=[cx,cy,xv,yv],width=2.0)
				Line(points=[xv,yv,xl,yl],width=2.0)
				Line(points=[xv,yv,xr,yr],width=2.0)
				Line(points=[cx,cy,xl,yl],width=2.0)
				Line(points=[cx,cy,xr,yr],width=2.0)
		else:
			if abs(balance) > 0.1:
				Line(points=[cx,cy,xv,yv],width=2.0)
				Line(points=[cx,cy,xh,yh],width=2.0)

		PushMatrix()
		Translate(x,y)
		Rotate(angle=value.phi,origin=(0,0))
		Scale(radius/9.0,origin=(0,0))
		baloon(triangle=False)
		PopMatrix()

#=============================================================================

class LAngleViewCurved(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewCurved, self).__init__(**kw)

	def draw(self,value):
		radius = self.bckgnd.get_radius()
		circle = self.bckgnd.get_circle()

		balance = value.balance()
		txtangle = value.txtori()
		x,y = value.xy()
		x = x*radius/45.0 + circle[0]
		y = y*radius/45.0 + circle[1]

		cx = circle[0]
		cy = circle[1]
		alf = math.atan2(y-cy,x-cx)
		xv = radius * math.cos(alf) + cx
		yv = radius * math.sin(alf) + cy
		xh = radius * math.cos(alf+math.pi) + cx
		yh = radius * math.sin(alf+math.pi) + cy
		xl = radius * math.cos(alf-math.pi/2.0) + cx
		yl = radius * math.sin(alf-math.pi/2.0) + cy
		xr = radius * math.cos(alf+math.pi/2.0) + cx
		yr = radius * math.sin(alf+math.pi/2.0) + cy

		self.balance_label(balance,txtangle,[0.7,0.7,0.7,1])

		good = 5.0
		set_color_range(
			[0.5,1.0,0.0,0.6],[1.0,0.6,0.0,0.7],math.fabs(balance)/good)

		if value.orientation() in ["LANDING","FLYING"]:
			xoh = radius/9.0 * math.cos(alf+math.pi)
			yoh = radius/9.0 * math.sin(alf+math.pi)
			if abs(balance) > 0.1:
				Line(points=[cx+xoh,cy+yoh,xv,yv],width=2.0)
				Line(bezier=[xv,yv,xl+xoh,yl+yoh,cx+xoh,cy+yoh],width=2.0)
				Line(bezier=[xv,yv,xr+xoh,yr+yoh,cx+xoh,cy+yoh],width=2.0)
		else:
			if abs(balance) > 0.1:
				Line(points=[cx,cy,xv,yv],width=2.0)
				Line(points=[cx,cy,xh,yh],width=2.0)

		PushMatrix()
		Translate(x,y)
		Rotate(angle=value.phi,origin=(0,0))
		Scale(radius/9.0,origin=(0,0))
		baloon(triangle=False)
		PopMatrix()

#=============================================================================

class LAngleViewFull(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewFull, self).__init__(**kw)

	def draw(self,value):
		radius = self.bckgnd.get_radius()
		circle = self.bckgnd.get_circle()

		x,y = value.xy()
		x = x*radius/45.0 + circle[0]
		y = y*radius/45.0 + circle[1]

		cx = circle[0]
		cy = circle[1]
		alf = math.atan2(y-cy,x-cx)
		xv = radius * math.cos(alf) + cx
		yv = radius * math.sin(alf) + cy
		xh = radius * math.cos(alf+math.pi) + cx
		yh = radius * math.sin(alf+math.pi) + cy
		xl = radius * math.cos(alf-math.pi/2.0) + cx
		yl = radius * math.sin(alf-math.pi/2.0) + cy
		xr = radius * math.cos(alf+math.pi/2.0) + cx
		yr = radius * math.sin(alf+math.pi/2.0) + cy

		def anzeige_x(val):
			Line(points=[x,cy-radius,x,cy+radius],width=1.0)
			txt = "{0: 5.2f}\u00b0".format(val)
			if x<cx:
				rotated_text(txt,x,cy-radius,180,anchor=(-1.1,-1.8),font_size=20)
				rotated_text(txt,x,cy+radius,0,anchor=(1.1,-1.8),font_size=20)
			else:
				rotated_text(txt,x,cy-radius,180,anchor=(1.1,-1.8),font_size=20)
				rotated_text(txt,x,cy+radius,0,anchor=(-1.1,-1.8),font_size=20)

		def anzeige_y(val):
			Line(points=[cx-radius,y,cx+radius,y],width=1.0)
			txt = "{0: 5.2f}\u00b0".format(val)
			if y<cy:
				rotated_text(txt,cx-radius,y,90,anchor=(1.1,-1.8),font_size=20)
				rotated_text(txt,cx+radius,y,-90,anchor=(-1.1,-1.8),font_size=20)
			else:
				rotated_text(txt,cx-radius,y,90,anchor=(-1.1,-1.8),font_size=20)
				rotated_text(txt,cx+radius,y,-90,anchor=(1.1,-1.8),font_size=20)

		# transparenter Drieickspfeil
		PushMatrix()
		Translate(cx,cy)
		Rotate(angle=value.phi,origin=(0,0))
		Scale(radius,origin=(0,0))
		triangle()
		PopMatrix()

		Color(0.7, 0.7, 0.7, 1)   # hellgrau
		if value.orientation() in ["LANDING","FLYING"]:
			anzeige_x(value.roll())
			anzeige_y(value.pitch())
		else:
			Line(points=[xv,yv,xh,yh],width=1.5)
			if value.orientation() in ['TOP','BOTTOM']:
				anzeige_x(value.balance())
			else:
				anzeige_y(value.balance())

		txt = "{0: 5.2f}\u00b0".format(value.balance())
		rotated_text(txt,cx,cy,value.phi-90,anchor=(0,-3.5),font_size=56,color=[0.7, 0.7, 0.7, 1])

		# Kreuzungspunkt der linien
		set_color([0.7, 0.7, 0.7, 1])   # hellgrau
		PushMatrix()
		Translate(x,y)
		Scale(radius/60.0,origin=(0,0))
		baloon(lscale=0.0)
		PopMatrix()

		# ballon im zentrom
		PushMatrix()
		good = 5.0
		set_color_range(
			[0.5,1.0,0.0,0.6],[1.0,0.6,0.0,0.7],math.fabs(value.balance())/good)
		Translate(cx,cy)
		Rotate(angle=value.phi,origin=(0,0))
		Scale(radius/9.0,origin=(0,0))
		baloon()
		PopMatrix()

#=============================================================================

class DynamicViews(object):

	def __init__(self):
		# Liste der verfügbaren Klassen.
		self.views = []
		self.views.append(LAngleViewSimple)
		self.views.append(LAngleViewTriangle)
		self.views.append(LAngleViewCurved)
		self.views.append(LAngleViewFull)

	def count(self):
		return len(self.views)

	def view(self,index):
		# neue Instanz erzeugen und zurückgeben.
		return self.views[index]()

#=============================================================================
