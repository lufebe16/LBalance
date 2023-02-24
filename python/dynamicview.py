

import math

from kivy.graphics import *
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

from graphics import set_color, set_color_range, baloon, triangle, rotated_text, LFont, raute

#=============================================================================
# Definiert den App Vordergrund

class LAngleView(BoxLayout):
	def __init__(self,**kw):
		super(LAngleView, self).__init__(**kw)
		self.bkcolor = [0.15, 0.00, 0.3, 1]
		with self.canvas.before:
			#Color(0, 0.00, 0.3, 1)   # schwarz mit blau stich
			#Color(0.15, 0.00, 0.3, 1)   # schwarz mit violett stich
			set_color(self.bkcolor)
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

	def balance_label(self,balance,txtangle,color,anchor=(0,0)):
		anf = LFont.angle()
		lbx = self.size[0]/2.0
		lby = self.size[1]/12
		if self.size[0] > self.size[1]:
			lby = self.size[1]/2.0
			lbx = self.size[0]/12
		rotated_text("{0: 5.2f}\u00b0".format(balance),
				lbx,lby,txtangle,font_size=anf,color=color,anchor=anchor)

#=============================================================================

class LAngleViewSimple(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewSimple, self).__init__(**kw)

	def draw(self,value):

		radius = self.bckgnd.get_tacho_radius()
		circle = self.bckgnd.get_tacho_center()

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
		radius = self.bckgnd.get_tacho_radius()
		circle = self.bckgnd.get_tacho_center()

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

		anf = LFont.angle()
		txt = "{0: 5.2f}\u00b0".format(value.balance())
		rotated_text(txt,cx,cy,value.phi-90,anchor=(0,-3.5),font_size=anf,color=[0.7, 0.7, 0.7, 1])

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
		radius = self.bckgnd.get_tacho_radius()
		circle = self.bckgnd.get_tacho_center()

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

		anf = LFont.angle()
		txt = "{0: 5.2f}\u00b0".format(value.balance())
		rotated_text(txt,cx,cy,value.phi-90,anchor=(0,-3.5),font_size=anf,color=[0.7, 0.7, 0.7, 1])

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
		self.trianglecolor = [1,1,1,0.1]

	def draw(self,value):
		radius = self.bckgnd.get_tacho_radius()
		circle = self.bckgnd.get_tacho_center()

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

		smf = LFont.small()
		anf = LFont.angle()

		lar = "<|"
		rar = "|>"

		def anzeige_x(val):
			Line(points=[x,cy-radius,x,cy+radius],width=1.0)
			txt = "{0: 5.2f}\u00b0".format(val)
			if x<cx:
				rotated_text(txt+rar,x,cy-radius,180,anchor=(-1.1,-1.8),font_size=smf)
				rotated_text(lar+txt,x,cy+radius,0,anchor=(1.1,-1.8),font_size=smf)
			else:
				rotated_text(lar+txt,x,cy-radius,180,anchor=(1.1,-1.8),font_size=smf)
				rotated_text(txt+rar,x,cy+radius,0,anchor=(-1.1,-1.8),font_size=smf)

		def anzeige_y(val):
			Line(points=[cx-radius,y,cx+radius,y],width=1.0)
			txt = "{0: 5.2f}\u00b0".format(val)
			if y<cy:
				rotated_text(lar+txt,cx-radius,y,90,anchor=(1.1,-1.8),font_size=smf)
				rotated_text(txt+rar,cx+radius,y,-90,anchor=(-1.1,-1.8),font_size=smf)
			else:
				rotated_text(txt+rar,cx-radius,y,90,anchor=(-1.1,-1.8),font_size=smf)
				rotated_text(lar+txt,cx+radius,y,-90,anchor=(1.1,-1.8),font_size=smf)

		# transparenter Drieickspfeil
		PushMatrix()
		Translate(cx,cy)
		Rotate(angle=value.phi,origin=(0,0))
		Scale(radius,origin=(0,0))
		triangle(self.trianglecolor)
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
		rotated_text(txt,cx,cy,value.phi-90,anchor=(0,-3.5),font_size=anf,color=[0.7, 0.7, 0.7, 1])

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

class LAngleViewFull2(LAngleViewFull):
	def __init__(self,**kw):
		super(LAngleViewFull2, self).__init__(**kw)
		self.trianglecolor = [0.3, 0.1, 0.4, 0.5]

#=============================================================================

class LAngleViewAV(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewAV, self).__init__(**kw)

	def draw(self,value):

		# Text ausgabe.
		balance = value.balance()
		anf = LFont.angle()
		lbx = self.pos[0]+self.size[0]/2.0
		lby = self.pos[1]+(self.size[1]-self.size[0])/2.0
		ngl = 0
		if self.size[0] > self.size[1]:
			lby = self.pos[1]+self.size[1]/2.0
			lbx = self.pos[0]+self.size[0]-(self.size[0]-self.size[1])/2.0
			ngl = 90
		rotated_text("{0: 5.2f}\u00b0".format(balance),
				lbx,lby,ngl,font_size=anf,color=[0.95,0.95,0.95,1],anchor=(0,-1.2))

		# Zeiger Darstellungen.
		if value.orientation() in ["LANDING","FLYING"]:

			radius = self.bckgnd.get_tacho_radius()
			circle = self.bckgnd.get_tacho_center()

			x,y = value.xy()
			x = x*radius/45.0 + circle[0]
			y = y*radius/45.0 + circle[1]

			cx = circle[0]
			cy = circle[1]
			alf = math.atan2(y-cy,x-cx)
			xv = radius * math.cos(alf) + cx
			yv = radius * math.sin(alf) + cy

			set_color([0.8,0,0,1])
			if balance>0.1:
				Line(points=[xv,yv,cx,cy],width=2.2)

			PushMatrix()
			Translate(x,y)
			Rotate(angle=value.phi,origin=(0,0))
			Scale(radius/14.0,origin=(0,0))
			raute(lcolor=[0.8,0,0,1])
			PopMatrix()

		else:
			length = self.bckgnd.get_meter_length()
			center = self.bckgnd.get_meter_center()

			# sowas wär modularer:
			# p in [-1.0..1.0]
			# x,y = self.bckgnd.get_meter_position(p)

			x,y = value.xy()
			x = x*length/45.0 + center[0]
			y = y*length/45.0 + center[1]

			PushMatrix()
			Translate(x,y)
			if value.orientation() in ["LEFT","RIGHT"]:
				Scale(length/7,length/14,1,origin=(0,0))
			else:
				Scale(length/14,length/7,1,origin=(0,0))
			raute(lcolor=[0.8,0,0,1])
			PopMatrix()


#=============================================================================

from koords import LValue
from gradient import Gradient
#from  kivy.utils import get_color_from_hex

class LAngleViewBA(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewBA, self).__init__(**kw)

		#Farben
		self.deckweiss = [1,1,1,1]
		self.horizontcolor = [0.0,0.0,1.0,1]
		self.pitchnrollcolor = [1,1,0,1]
		self.gradiblau = Gradient.horizontal(
					[0.0,0.0,1.0,0.2],
					[0.0,0.0,1.0,0.2],
					[0.0,0.0,1.0,0.2],
					[0.0,0.0,0.0,0.2])
		self.gradigelb = Gradient.horizontal(
					[1.0,1.0,0.0,0.2],
					[1.0,1.0,0.0,0.2],
					[1.0,1.0,0.0,0.2],
					[0.0,0.0,0.0,0.2])

	def draw(self,value):

		radius = self.bckgnd.get_tacho_radius()
		center = self.bckgnd.get_tacho_center()
		cx = center[0]
		cy = center[1]

		x = value.rollExt()
		y = value.pitchExt()
		x = x*radius/45.0 + center[0]
		y = y*radius/45.0 + center[1]

		deckweiss = self.deckweiss
		horizontcolor = self.horizontcolor
		pitchnrollcolor = self.pitchnrollcolor
		gradiblau = self.gradiblau
		gradigelb = self.gradigelb

		def xyLine(x,y,width=2.0):
			PushMatrix()
			Translate(x,y)
			Rotate(angle=value.phi,origin=(0,0))
			Scale(radius,origin=(0,0))
			set_color(horizontcolor)
			Line(points=[0.0,-3.0,0.0,3.0],width=width/max(radius,0.01))
			#set_color([0.0,0.0,1.0,0.2])
			#Rectangle(pos=(0.0,-1.0), size=(0.7,2.0))
			set_color(deckweiss)
			Rectangle(texture=gradiblau,pos=(0.0,-1.0), size=(1.0,2.0))
			Rotate(angle=180,origin=(0,0))
			#set_color([1.0,1.0,0.0,0.2])
			#Rectangle(pos=(0.0,-1.0), size=(0.7,2.0))
			set_color(deckweiss)
			Rectangle(texture=gradigelb,pos=(0.0,-1.0), size=(1.0,2.0))
			PopMatrix()

		# künstl horizont:
		phiR = math.radians(value.phi)
		xyLine(x,y)
		xyLine(x+2*radius*math.cos(phiR),y+2*radius*math.sin(phiR))
		xyLine(x-2*radius*math.cos(phiR),y-2*radius*math.sin(phiR))

		# pitch und roll
		set_color(pitchnrollcolor)
		wid = 1.5
		Line(points=[x,self.parent.pos[1],x,self.parent.pos[1]+self.parent.size[1]],width=wid)
		Line(points=[self.parent.pos[0],y,self.parent.pos[0]+self.parent.size[0],y],width=wid)
		Ellipse(pos=(x-10,y-10),size=(20,20))

		# TBD: Winkel anschriften

		#print (self.val_ori)

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

from staticview \
	import LCircleViewSimple,LCircleViewFine, \
		LCircleViewFineWithScale,LCircleViewAV, \
		LCircleViewBA

import json

class LLayout(object):
	def __init__(self, dv, bg, sc):
		self.layout = {
			"foreground": dv,
			"background": bg,
			"statuscolor": sc
			}

	def background(self):
		return self.layout["background"]()

	def foreground(self):
		return self.layout["foreground"]()

	def statuscolor(self):
		return self.layout["statuscolor"]


class LLayouts(EventDispatcher):
	selected = NumericProperty(0)

	def __init__(self,**kw):
		super(LLayouts,self).__init__(**kw)
		self.layouts = []
		self.layouts.append(LLayout(
			LAngleViewCurved,LCircleViewSimple,[0.7, 0.1, 0.1, 1]))
		self.layouts.append(LLayout(
			LAngleViewFull,LCircleViewFine,[0.0, 0.4, 0.1, 1]))
		self.layouts.append(LLayout(
			#LAngleViewFull,LCircleViewFineWithScale,[0.0, 0.4, 0.1, 1]))
			LAngleViewFull2,LCircleViewFineWithScale,[0.2, 0.05, 0.3, 1]))
		self.layouts.append(LLayout(
			LAngleViewAV,LCircleViewAV,[0.8, 0.1, 0.1, 1]))
		self.layouts.append(LLayout(
			LAngleViewBA,LCircleViewBA,[0.15, 0.15, 0.15, 0.5]))
		self.read()

	def current(self):
		return self.layouts[self.selected]

	def next(self):
		self.selected = (self.selected+1) % len(self.layouts)
		self.save()

	def count(self):
		return len(self.layouts)

	def layout(self,index):
		return self.layouts[index]

	def save(self):
		try:
			fp = open("ww_layout.json",'w')
			json.dump(self.selected,fp)
		except:
			pass

	def read(self):
		try:
			fp = open("ww_layout.json",'r')
			if fp:
				sel = json.load(fp)
				if sel>=self.count(): sel = 0
				if sel<0: sel = 0
				self.selected = sel
		except:
			pass

Layouts = LLayouts()

#=============================================================================
