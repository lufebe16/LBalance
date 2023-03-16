

import math

from kivy.graphics import *
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

from storage import ConfigDir
from graphics import set_color, set_color_range, baloon, triangle, rotated_text, LFont, raute
from koords import normAngle

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
		pass

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
				pos=(lbx,lby),angle=txtangle,font_size=anf,color=color,anchor=anchor)

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
		rotated_text(txt,pos=(cx,cy),angle=value.phi-90,anchor=(0,-3.5),font_size=anf,color=[0.7, 0.7, 0.7, 1])

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
		rotated_text(txt,pos=(cx,cy),angle=value.phi-90,anchor=(0,-3.5),font_size=anf,color=[0.7, 0.7, 0.7, 1])

		good = 5.0
		set_color_range(
			[0.5,1.0,0.0,0.6],[1.0,0.6,0.0,0.7],math.fabs(balance)/good)

		if value.orientation() in ["LANDING","FLYING"]:
			xoh = radius/9.0 * math.cos(alf+math.pi)
			yoh = radius/9.0 * math.sin(alf+math.pi)
			if abs(balance) > 0.1:
				Line(points=[cx+xoh,cy+yoh,xv,yv],width=2.0)
				#Line(bezier=[xv,yv,xl+xoh,yl+yoh,cx+xoh,cy+yoh],width=2.0)
				#Line(bezier=[xv,yv,xr+xoh,yr+yoh,cx+xoh,cy+yoh],width=2.0)
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
				rotated_text(txt+rar,pos=(x,cy-radius),angle=180,anchor=(-1.1,-1.8),font_size=smf)
				rotated_text(lar+txt,pos=(x,cy+radius),angle=0,anchor=(1.1,-1.8),font_size=smf)
			else:
				rotated_text(lar+txt,pos=(x,cy-radius),angle=180,anchor=(1.1,-1.8),font_size=smf)
				rotated_text(txt+rar,pos=(x,cy+radius),angle=0,anchor=(-1.1,-1.8),font_size=smf)

		def anzeige_y(val):
			Line(points=[cx-radius,y,cx+radius,y],width=1.0)
			txt = "{0: 5.2f}\u00b0".format(val)
			if y<cy:
				rotated_text(lar+txt,pos=(cx-radius,y),angle=90,anchor=(1.1,-1.8),font_size=smf)
				rotated_text(txt+rar,pos=(cx+radius,y),angle=-90,anchor=(-1.1,-1.8),font_size=smf)
			else:
				rotated_text(txt+rar,pos=(cx-radius,y),angle=90,anchor=(-1.1,-1.8),font_size=smf)
				rotated_text(lar+txt,pos=(cx+radius,y),angle=-90,anchor=(1.1,-1.8),font_size=smf)

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
		rotated_text(txt,pos=(cx,cy),angle=value.phi-90,anchor=(0,-3.5),font_size=anf,color=[0.7, 0.7, 0.7, 1])

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
		self.pointer_color = [0.8,0.0,0.0,1.0]
		self.text_color = [0.95,0.95,0.95,1]

	def pointer(self,line=False):
		original = self.val_ori not in ['LANDING','FLYING']
		if original:
			raute(lcolor=self.pointer_color)
		else:
			set_color(self.pointer_color)
			baloon(triangle=False,line=line)

	def dirline(self,balance,xv,yv,cx,cy):
		set_color(self.pointer_color)
		if balance>0.1 or balance<-0.1:
			Line(points=[xv,yv,cx,cy],width=2.2)

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
				pos=(lbx,lby),angle=ngl,font_size=anf,color=self.text_color,anchor=(0,-1.2))

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

			self.dirline(balance,xv,yv,cx,cy)

			PushMatrix()
			Translate(x,y)
			Rotate(angle=value.phi,origin=(0,0))
			Scale(radius/13.0,origin=(0,0))
			self.pointer()
			PopMatrix()

		else:
			length = self.bckgnd.get_meter_length()
			center = self.bckgnd.get_meter_center()

			x,y = value.xy()
			x = x*length/45.0 + center[0]
			y = y*length/45.0 + center[1]

			PushMatrix()
			Translate(x,y)
			if value.orientation() in ["LEFT","RIGHT"]:
				Scale(length/8.4,length/17,1,origin=(0,0))
				Rotate(angle=90,origin=(0,0))
			else:
				Scale(length/17,length/8.4,1,origin=(0,0))
			self.pointer(line=True)
			PopMatrix()

#=============================================================================

class LAngleViewAValt(LAngleViewAV):
	def __init__(self,**kw):
		super(LAngleViewAValt, self).__init__(**kw)
		#self.pointer_color = [8.0,8.,8.0,1.0]
		self.pointer_color = [0.0,0.0,0.0,1.0]
		self.text_color = [0.95,0.95,0.95,1]

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
					[0.0,0.0,1.0,0.1],
					[0.0,0.0,1.0,0.1],
					[0.0,0.0,1.0,0.1],
					[0.0,0.0,0.0,0.1])
		self.gradigelb = Gradient.horizontal(
					[1.0,1.0,0.0,0.1],
					[1.0,1.0,0.0,0.1],
					[1.0,1.0,0.0,0.1],
					[0.0,0.0,0.0,0.1])

	def draw(self,value):

		radius = self.bckgnd.get_tacho_radius()
		center = self.bckgnd.get_tacho_center()
		cx = center[0]
		cy = center[1]
		phiR = math.radians(value.phi)

		anf = LFont.small()*1.5

		weiss = self.deckweiss
		horizontcolor = self.horizontcolor
		pitchnrollcolor = self.pitchnrollcolor
		grb = self.gradiblau
		grg = self.gradigelb

		def xyLine(x,y,gb,gg,width=2.0):
			PushMatrix()
			Translate(x,y)
			Rotate(angle=value.phi,origin=(0,0))
			Scale(radius,origin=(0,0))
			set_color(horizontcolor)
			if width>0.0:
				Line(points=[0.0,-2.0,0.0,2.0],width=width/max(radius,0.01))
			# Achtung: die Texturfarbe wird mit der aktuellen Farbe gemischt.
			# Darum Preset auf weiss.
			set_color(weiss)
			Rectangle(texture=gb,pos=(0.0,-2.0), size=(4.0,4.0))
			Rotate(angle=180,origin=(0,0))
			set_color(weiss)
			Rectangle(texture=gg,pos=(0.0,-2.0), size=(4.0,4.0))
			PopMatrix()

		x = value.rollExt()
		y = value.pitchExt()
		#print ('roll,pitch,ext',x,y)

		x = x*radius/45.0 + cx
		y = y*radius/45.0 + cy
		#print ('dx,dy',x-cx,y-cy)

		# künstl Horizont:
		if self.val_ori in ['LANDING']:
			xyLine(x,y,grb,grb,width=0.0)
		elif self.val_ori in ['BOTTOM','TOP','LEFT','RIGHT']:
			if value.theta < 90.0:
				xyLine(x-2*radius*math.cos(phiR),y-2*radius*math.sin(phiR),grb,grg)
			else:
				xyLine(x+2*radius*math.cos(phiR),y+2*radius*math.sin(phiR),grb,grg)
		else: # FLYING
			xyLine(x,y,grg,grg,width=0.0)

		# pitch und roll mit Anschriften
		set_color(pitchnrollcolor)
		wid = 1.5
		Line(points=[x,self.parent.pos[1],x,self.parent.pos[1]+self.parent.size[1]],width=wid)
		Line(points=[self.parent.pos[0],y,self.parent.pos[0]+self.parent.size[0],y],width=wid)
		Ellipse(pos=(x-10,y-10),size=(20,20))

		rotated_text("{0: 5.2f}\u00b0".format(value.roll()),
			pos=(x,self.pos[1]),anchor=(-1,1),font_size=anf,color=pitchnrollcolor)
		rotated_text("{0: 5.2f}\u00b0".format(value.pitch()),
			pos=(self.pos[0],y),anchor=(1,1),font_size=anf,color=pitchnrollcolor)

		# Ebenenwinkel mit Anschrift
		set_color(weiss)
		width = 0.7
		PushMatrix()
		Translate(cx,cy)
		Rotate(angle=value.phi+90,origin=(0,0))
		Scale(radius,origin=(0,0))
		Line(points=[0.0,0.27,0.0,1.0],width=width/max(radius,0.01))
		Line(points=[-2.0,0.0,27.0,0.0],width=width/max(radius,0.01))
		PopMatrix()
		tx = cx+0.27*radius*math.cos(phiR+math.pi)
		ty = cy+0.27*radius*math.sin(phiR+math.pi)
		#rotated_text("{0: 5.2f}\u00b0".format(90-theta),
		rotated_text("{0: 5.2f}\u00b0".format(value.theta),
			pos=(tx,ty),angle=value.phi-90,anchor=(-1,0),font_size=anf,color=weiss)

		# Balance
		set_color(weiss)
		PushMatrix()
		Translate(cx,cy)
		Scale(radius,origin=(0,0))
		Line(points=[-2.0,0.0,2.0,0.0],width=width/max(radius,0.01))
		PopMatrix()

		# Winkelanzeige mit Anschriften
		vx = value.valX
		if vx == 0.0: vx = 0.0001
		angleC = math.degrees(math.atan(value.valY/vx))
		scaleC = 0.12*radius
		PushMatrix()
		Translate(cx,cy)
		Scale(scaleC,origin=(0,0))
		Line(circle=(0,0,1.1,90,180-angleC),width=width/max(scaleC,0.01))
		Line(circle=(0,0,1.02,180-angleC,270),width=width/max(scaleC,0.01))
		PopMatrix()

		angleCR = math.radians((angleC-90)/2.0)
		tx = cx+0.14*radius*math.cos(angleCR)
		ty = cy+0.14*radius*math.sin(angleCR)
		rotated_text("{0: 5.2f}\u00b0".format(90.0-angleC),
			pos=(tx,ty),angle=0,anchor=(1,-1),font_size=anf,color=weiss)

		angleCR = math.radians(180+(angleC+90)/2.0)
		tx = cx+0.14*radius*math.cos(angleCR)
		ty = cy+0.14*radius*math.sin(angleCR)
		rotated_text("{0: 5.2f}\u00b0".format(90.0+angleC),
			pos=(tx,ty),angle=0,anchor=(-1,-1),font_size=anf,color=weiss)

#=============================================================================

from kivy.graphics.scissor_instructions import ScissorPush, ScissorPop

class LAngleViewMini(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewMini, self).__init__(**kw)

	def draw(self,value):
		radius = self.bckgnd.get_tacho_radius()
		center = self.bckgnd.get_tacho_center()
		cx = center[0]
		cy = center[1]
		anf = LFont.angle()*2.7

		collin = [0.7,0.7,0.7,1]
		coltxt = [0.13,0.13,0.13,1]
		bal = value.balance()

		ScissorPush(
			x=self.pos[0],y=self.pos[1],width=self.size[0],height=self.size[1])

		rotated_text("{0: 4.1f}\u00b0".format(bal),
			pos=(cx,cy),angle=value.phi-90.0,anchor=(0,-1),font_size=anf,color=coltxt)

		wid = 11.0
		PushMatrix()
		Translate(cx,cy)
		Rotate(angle=value.phi+90,origin=(0,0))
		Scale(radius,origin=(0,0))
		set_color(collin)
		Line(points=[0.0,-0.2,0.0,-1.0],width=wid/max(radius,0.01))
		Line(points=[-2.0,0.0,2.0,0.0],width=wid/max(radius,0.01))
		PopMatrix()

		ScissorPop()

#=============================================================================

from gradient import Gradient

class LAngleViewBubble(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewBubble, self).__init__(**kw)

		# textur für die blase vorbereiten
		lld = [ 0xb1/255.0, 0xc8/255.0, 0.0, 0.8]
		whtd = [1.0,1.0,1.0,1.0]
		lld2 = [ 0xd9/255.0, 0xe8/255.0, 0.8, 0.7]
		self.tex_bubble = Gradient.centered(whtd,lld2,lld)

	# die Luftblase
	def bubble(self,x,y,radius,scale,start=0,end=360):
		PushMatrix()
		Translate(x,y)
		Scale(radius*scale,origin=(0,0))
		set_color([1,1,1,1])
		Ellipse(pos=(-1,-1),size=(2,2),texture=self.tex_bubble,
									angle_start=start,angle_end=end)
		PopMatrix()

	# gitter im kreis
	def grid(self,x,y,radius,scale,lwidth=1.0):
		PushMatrix()
		Translate(x,y)
		Scale(radius,origin=(0,0))
		set_color([0,0,0,1])
		Line(circle=(0,0,scale),width=lwidth)
		Line(points=(scale,0,1,0),width=lwidth/3.0)
		Line(points=(-scale,0,-1,0),width=lwidth/3.0)
		Line(points=(0,scale,0,1),width=lwidth/3.0)
		Line(points=(0,-scale,0,-1),width=lwidth/3.0)
		PopMatrix()

	# gitterstäbe in den balken
	def frame(self,x,y,radius,scale,lwidth=1.0,turn=False):
		PushMatrix()
		Translate(x,y)
		if turn:
			Rotate(angle=90,origin=(0,0))
		Scale(radius,origin=(0,0))
		set_color([0,0,0,1])
		Line(points=(scale,scale,scale,-scale),width=lwidth/3.0)
		Line(points=(-scale,scale,-scale,-scale),width=lwidth/3.0)
		PopMatrix()

	def textbox(self,value,x,y,angle=0,anchor=(0,0),apos=0,asel=0):
		grad = "\u00b0"
		arrow = ["\u25b2","\u25b6","\u25bc","\u25c0"]
		# Anm: DejaVuSans hat diese Zeichen, Roboto nicht.

		rotated_text(
			"88888"+grad,
			pos=(x,y),
			angle=angle,
			#font_name = "RobotoMono-Regular.ttf",
			font_name = "DejaVuSans.ttf",
			font_size=LFont.middle()*1.3,
			anchor=anchor,
			color=[0.1,0.1,0.1,1],
			bgnd=True,
			bcolor=[0,0,0,1])

		svalue = "{0:04.1f}".format(math.fabs(value))
		if value < 0: asel += 2
		if apos == 0:
			text = arrow[asel]+svalue+"\u00b0"
		else:
			text = svalue+"\u00b0"+arrow[asel]
		rotated_text(
			text=text,
			pos=(x,y),
			angle=angle,
			#font_name = "RobotoMono-Regular.ttf",
			font_name = "DejaVuSans.ttf",
			font_size=LFont.middle()*1.3,
			anchor=anchor,
			color=[0.0,1.0,0.05,1])

	def draw(self,value):
		radius = self.bckgnd.get_meter_length()/2.0
		center = self.bckgnd.get_tacho_center()
		scale = self.bckgnd.get_meter_aspect()
		cx = center[0]
		cy = center[1]
		anf = LFont.angle()*2.7

		x,y = value.xy()
		x = x*radius/45.0 + cx
		y = y*radius/45.0 + cy

		# bubble und grid.
		if self.val_ori in ['LANDING','FLYING']:
			bx = cx + (x-cx)*(1.0-scale)
			by = cy + (y-cy)*(1.0-scale)
			self.bubble(bx,by,radius,scale)
			self.grid(cx,cy,radius,scale,lwidth=3.0/max(radius,0.01))
		elif self.val_ori in ['BOTTOM']:
			bx = cx + (x-cx)*(1.0-scale)
			by = cy + scale*radius
			self.bubble(bx,by,radius,scale,start=90,end=270)
			self.frame(cx,cy,radius,scale,lwidth=3.0/max(radius,0.01))
		elif self.val_ori in ['TOP']:
			bx = cx + (x-cx)*(1.0-scale)
			by = cy - scale*radius
			self.bubble(bx,by,radius,scale,start=270,end=450)
			self.frame(cx,cy,radius,scale,lwidth=3.0/max(radius,0.01))
		elif self.val_ori in ['LEFT']:
			bx = cx + scale*radius
			by = cy + (y-cy)*(1.0-scale)
			self.bubble(bx,by,radius,scale,start=180,end=360)
			self.frame(cx,cy,radius,scale,lwidth=3.0/max(radius,0.01),turn=True)
		elif self.val_ori in ['RIGHT']:
			bx = cx - scale*radius
			by = cy + (y-cy)*(1.0-scale)
			self.bubble(bx,by,radius,scale,start=0,end=180)
			self.frame(cx,cy,radius,scale,lwidth=3.0/max(radius,0.01),turn=True)

		# anschriften.
		if self.val_ori in ['LANDING','FLYING']:
			if self.size[1] > self.size[0]:
				bxl = self.pos[0] + self.size[0]*.25
				bxr = self.pos[0] + self.size[0]*.75
				by = (self.pos[1] + (cy-radius))/2
				self.textbox(value.roll(), bxl,by,anchor=(0,0),asel=1,apos=0)
				self.textbox(value.pitch(), bxr,by,anchor=(0,0),asel=0,apos=1)
			else:
				byl = self.pos[1] + self.size[1]*.25
				byr = self.pos[1] + self.size[1]*.75
				bx = (self.pos[0] + self.size[0] + (cx+radius))/2
				self.textbox(-value.roll(), bx,byr,anchor=(0,0),asel=0,apos=1,angle=90)
				self.textbox(value.pitch(), bx,byl,anchor=(0,0),asel=1,apos=0,angle=90)
		elif self.val_ori in ['BOTTOM']:
			bx = self.pos[0] + self.size[0]*.5
			by = (self.pos[1] + (cy-radius*scale))/2
			self.textbox(value.balance(), bx,by,anchor=(0,0),asel=0,apos=1)
		elif self.val_ori in ['TOP']:
			bx = self.pos[0] + self.size[0]*.5
			by = (self.pos[1] + self.size[1] + (cy+radius*scale))/2
			self.textbox(value.balance(), bx,by,anchor=(0,0),asel=0,apos=1,angle=180)
		elif self.val_ori in ['LEFT']:
			by = self.pos[1] + self.size[1]*.5
			bx = (self.pos[0] + (cx-radius*scale))/2
			self.textbox(value.balance(), bx,by,anchor=(0,0),asel=0,apos=1,angle=-90)
		elif self.val_ori in ['RIGHT']:
			by = self.pos[1] + self.size[1]*.5
			bx = (self.pos[0] + self.size[0] + (cx+radius*scale))/2
			self.textbox(value.balance(), bx,by,anchor=(0,0),asel=0,apos=1,angle=90)

#=============================================================================
