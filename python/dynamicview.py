

import math

from kivy.graphics import Line, Rectangle, RoundedRectangle, Ellipse, Callback, Color
from kivy.graphics import Fbo, ClearColor, ClearBuffers, InstructionGroup
from kivy.graphics import PushMatrix, PopMatrix, Scale, Rotate, Translate
from kivy.graphics.transformation import Matrix
from kivy.graphics.context_instructions import Transform
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.event import EventDispatcher
from kivy.uix.label import Label

from storage import ConfigDir
from graphics import set_color, set_color_range, baloon, triangle
from graphics import LFont, raute, welle, color_range_ext, hsva_conv
from graphics import rotated_text, RotatedText, RotatedTextWidget

from koords import normAngle

#=============================================================================
# Definiert den App Vordergrund

class LAngleView(FloatLayout):
	value = ObjectProperty()

	def __init__(self,**kw):
		self.cols = 1
		self.rows = 1
		super(LAngleView, self).__init__(**kw)
		self.bkcolor = [0.15, 0.00, 0.3, 1]
		#self.bkcolor = [0.15, 0.00, 0.0, 1]
		with self.canvas.before:
			Color(0, 0.00, 0.3, 1)   # schwarz mit blau stich
			#Color(0.15, 0.00, 0.3, 1)   # schwarz mit violett stich
			set_color(self.bkcolor)
			self.rect = Rectangle(pos=self.pos, size=self.size)

		self.bind(pos=self.update_pos)
		self.bind(size=self.update_size)
		self.bckgnd = None
		self.val_ori = None
		self.last_parent = None
		self.layout_selector = None

	def on_parent(self, inst, val):
		if val is not None:
			try:
				self.parent.bind(last_value=self.on_present)
				self.last_parent = self.parent
			except:
				try:
					self.parent.parent.bind(last_value=self.on_present)
					self.last_parent = self.parent.parent
				except:
					pass
		elif self.last_parent is not None:
			try:
				self.last_parent.unbind(last_value=self.on_present)
				self.last_parent = None
			except:
				pass

	def on_value(self, inst, newvalue):
		print('value changed - base class')
		pass

	def update_pos(self,obj,pos):
		# with floatlayout required: manage posiion of childrens
		for c in self.children:
			c.pos = pos
		self.rect.pos = self.pos

	def update_size(self,inst,size):
		# with floatlayout required: manage size of childrens
		for c in self.children:
			c.size = size
		self.rect.size = self.size

	def set_background(self,bckgnd):
		# self.clear_widgets()
		self.bckgnd = bckgnd
		self.add_widget(bckgnd,100)

	def on_present(self, inst, value):
		#print ('on_present',inst,value)
		self.present(value)

	def present(self,value):
		# orientierungsänderung weiterleiten.
		if self.val_ori != value.orientation():
			self.val_ori = value.orientation()
			self.bckgnd.val_ori = self.val_ori

		# trigger: on_value_changed
		self.value = value

	def on_touch_down(self, touch):
		if self.collide_point(touch.x,touch.y):
			if self.layout_selector is not None:
				self.layout_selector()
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

	def on_value(self, inst, value):
		if value is None: return

		self.canvas.after.clear()
		with self.canvas.after:

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
			rs = 2.0*radius/9.0
			Scale(x=rs,y=rs,origin=(0,0))
			baloon()
			PopMatrix()

#=============================================================================

class LAngleViewTriangle(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewTriangle, self).__init__(**kw)

	def on_value(self, inst, value):
		if value is None: return

		self.canvas.after.clear()
		with self.canvas.after:
			self.drawit(value)

	def drawit(self,value):
		radius = self.bckgnd.get_tacho_radius()
		circle = self.bckgnd.get_tacho_center()

		balance = value.balance()
		#txtangle = value.txtori()
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
		rotated_text(txt,pos=(cx,cy),
			angle=value.phi-90,anchor=(0,-3.5),
			font_size=anf,color=[0.7, 0.7, 0.7, 1])

		good = 5.0
		set_color_range(
			[0.5,1.0,0.0,0.6],[1.0,0.6,0.0,0.7],math.fabs(balance)/good)
		#self.center_color(balance)

		if value.orientation() in ["LANDING","FLYING"]:
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
		rs = radius/9.0
		Scale(x=rs,y=rs,origin=(0,0))
		baloon(triangle=False)
		PopMatrix()

#=============================================================================

class LAngleViewCurved(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewCurved, self).__init__(**kw)

	def on_value(self, inst, value):
		if value is None: return

		self.canvas.after.clear()
		with self.canvas.after:
			self.drawit(value)

	def drawit(self,value):
		radius = self.bckgnd.get_tacho_radius()
		circle = self.bckgnd.get_tacho_center()

		balance = value.balance()
		#txtangle = value.txtori()
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

		anf = LFont.angle()
		txt = "{0: 5.2f}\u00b0".format(value.balance())
		rotated_text(txt,pos=(cx,cy),
			angle=value.phi-90,anchor=(0,-3.5),
			font_size=anf,color=[0.7, 0.7, 0.7, 1])

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
		rs = radius/9.0
		Scale(x=rs,y=rs,origin=(0,0))
		baloon(triangle=False)
		PopMatrix()

#=============================================================================

class LAngleViewFull(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewFull, self).__init__(**kw)
		self.trianglecolor = [1,1,1,0.1]

	def on_value(self, inst, value):
		if value is None: return

		self.canvas.after.clear()
		with self.canvas.after:
			self.drawit(value)

	def drawit(self,value):
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

		smf = LFont.small()*radius/300.0
		anf = LFont.angle()*radius/300.0

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
		Translate(x=cx,y=cy)
		Rotate(angle=value.phi,origin=(0,0))
		Scale(x=radius,y=radius,origin=(0,0))
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
		rotated_text(txt,pos=(cx,cy),
			angle=value.phi-90,anchor=(0,-3.5),
			font_size=anf,color=[0.7, 0.7, 0.7, 1])

		# Kreuzungspunkt der linien
		set_color([0.7, 0.7, 0.7, 1])   # hellgrau
		PushMatrix()
		Translate(x=x,y=y)
		r = radius/60.0
		Scale(x=r,y=r,origin=(0,0))
		baloon(lscale=0.0)
		PopMatrix()

		# ballon im zentrom
		PushMatrix()
		good = 5.0
		set_color_range(
			[0.5,1.0,0.0,0.6],[1.0,0.6,0.0,0.7],math.fabs(value.balance())/good)
		Translate(x=cx,y=cy)
		Rotate(angle=value.phi,origin=(0,0))
		r = radius/9.0
		Scale(x=r,y=r,origin=(0,0))
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
			#raute(lcolor=self.pointer_color)
			self.canvas.after.add(welle(lcolor=self.pointer_color))
		else:
			set_color(self.pointer_color)
			baloon(triangle=False,line=line)

	def dirline(self,balance,xv,yv,cx,cy):
		set_color(self.pointer_color)
		if balance>0.1 or balance<-0.1:
			Line(points=[xv,yv,cx,cy],width=2.2)

	def on_value(self, inst, value):
		if value is None: return

		self.canvas.after.clear()
		with self.canvas.after:
			self.drawit(value)

	def drawit(self,value):
		radius = self.bckgnd.get_tacho_radius()
		circle = self.bckgnd.get_tacho_center()
		if radius <= 0.0: return

		# Text ausgabe.
		balance = value.balance()
		anf = LFont.angle()*radius/300.0
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
			r = radius/13.0
			Scale(x=r,y=r,origin=(0,0))
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
				Scale(x=length/8.4,y=length/17,z=1,origin=(0,0))
				Rotate(angle=90,origin=(0,0))
			else:
				Scale(x=length/17,y=length/8.4,z=1,origin=(0,0))
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

	def on_value(self, inst, value):
		if value is None: return

		self.canvas.after.clear()
		with self.canvas.after:
			ScissorPush(
				x=self.pos[0],y=self.pos[1],width=self.size[0],height=self.size[1])
			self.drawit(value)
			ScissorPop()

	def drawit(self,value):
		radius = self.bckgnd.get_tacho_radius()
		center = self.bckgnd.get_tacho_center()
		if radius <= 0.0: return

		cx = center[0]
		cy = center[1]
		phiR = math.radians(value.phi)

		anf = LFont.small()*1.5*radius/900.0

		weiss = self.deckweiss
		horizontcolor = self.horizontcolor
		pitchnrollcolor = self.pitchnrollcolor
		grb = self.gradiblau
		grg = self.gradigelb

		def xyLine(x,y,gb,gg,width=2.0):
			PushMatrix()
			Translate(x,y)
			Rotate(angle=value.phi,origin=(0,0))
			Scale(x=radius,y=radius,origin=(0,0))
			set_color(horizontcolor)
			if width>0.0:
				wid = width/radius
				Line(points=[0.0,-2.0,0.0,2.0],width=wid)
			# Achtung: die Texturfarbe wird mit der aktuellen Farbe gemischt.
			# Darum Preset auf weiss.
			set_color(weiss)
			Rectangle(texture=gb,pos=(0.0,-2.0), size=(4.0,4.0))
			Rotate(angle=180,origin=(0,0))
			set_color(weiss)
			Rectangle(texture=gg,pos=(0.0,-2.0), size=(4.0,4.0))
			PopMatrix()

		if value.theta < 90:
			x = cx + value.rollExt()*radius/45.0
			y = cy + value.pitchExt()*radius/45.0
		else:
			x = cx - value.rollExt()*radius/45.0
			y = cy - value.pitchExt()*radius/45.0

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
		Scale(x=radius,y=radius,origin=(0,0))
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
		Scale(x=radius,y=radius,origin=(0,0))
		Line(points=[-2.0,0.0,2.0,0.0],width=width/max(radius,0.01))
		PopMatrix()

		# Winkelanzeige mit Anschriften
		vx = value.valX
		if vx == 0.0: vx = 0.0001
		angleC = math.degrees(math.atan(value.valY/vx))
		scaleC = 0.12*radius
		PushMatrix()
		Translate(cx,cy)
		Scale(x=scaleC,y=scaleC,origin=(0,0))
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

from kivy.graphics.tesselator import Tesselator

class LTransform(Transform):
	def __init__(self,*args,**kwargs):
		super(LTransform, self).__init__(*args,**kwargs)

	def project(self,mat):
		self.transform(mat)

class LAngleViewMini(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewMini, self).__init__(**kw)

		self.anschrift = RotatedTextWidget()
		self.translate = None
		self.rotate =  None
		self.scale =  None
		self.line1 =  None
		self.line2 =  None
		self.scissor = None
		self.add_widget(self.anschrift)

	def scene_setup(self,cx,cy,text,value,anf,radius,wid):
		collin = [0.7,0.7,0.7,1]
		coltxt = [0.13,0.13,0.13,1]
		self.scissor = ScissorPush(
			x=self.pos[0],y=self.pos[1],width=self.size[0],height=self.size[1])
		PushMatrix()
		self.translate = Translate(cx,cy)
		self.rotate = Rotate(angle=value.phi+90,origin=(0,0))
		self.scale = Scale(x=radius,y=radius,origin=(0,0))
		set_color(collin)
		self.line1 = Line(points=[0.0,-0.2,0.0,-1.0],width=wid)
		self.line2 = Line(points=[-2.0,0.0,2.0,0.0],width=wid)
		PopMatrix()
		ScissorPop()

		tangle = (180.0+value.phi+90) % 360
		self.anschrift.setup(text,
			pos=(cx,cy),angle=tangle,anchor=(0,-1),font_size=anf,color=coltxt,
			bcolor=[0.45,0.45,0.45,1])


	def scene_update(self,cx,cy,text,value,anf,radius,wid):

		self.scissor.x = self.pos[0]
		self.scissor.y = self.pos[1]
		self.scissor.width = self.size[0]
		self.scissor.height = self.size[1]
		self.translate.x = cx
		self.translate.y = cy
		self.rotate.angle = value.phi+90.0
		self.scale.x = radius
		self.scale.y = radius
		self.line1.width = wid
		self.line2.width = wid

		tangle = (180.0+value.phi+90) % 360
		self.anschrift.update(text=text,
			pos=(cx,cy),
			angle=tangle,
			font_size=anf)

	def on_value(self,inst,value):
		radius = self.bckgnd.get_tacho_radius()
		center = self.bckgnd.get_tacho_center()
		if radius <= 0.0: return

		cx,cy = center
		anf = LFont.angle()*radius/150.0
		wid = 11.0*radius/350.0/radius
		bal = value.balance()
		text = "{0: 4.1f}\u00b0".format(bal)

		if self.scissor is None:
			self.canvas.after.clear()
			with self.canvas.after:
				self.scene_setup(cx,cy,text,value,anf,radius,wid)
		else:
			self.scene_update(cx,cy,text,value,anf,radius,wid)

#=============================================================================
# AngleViewBubble

class Bubble(Widget):
	def __init__(self,**kw):
		super(Bubble,self).__init__(**kw)
		# textur für die blase vorbereiten
		lld = [ 0xb1/255.0, 0xc8/255.0, 0.0, 0.8]
		whtd = [1.0,1.0,1.0,1.0]
		lld2 = [ 0xd9/255.0, 0xe8/255.0, 0.8, 0.7]
		tex = Gradient.centered(whtd,lld2,lld)
		radius = 10
		scale = 10
		start = 0
		end = 0

		with self.canvas:
			PushMatrix()
			self.trans = Translate(0,0)
			self.scale = Scale(x=radius*scale,y=radius*scale,origin=(0,0))
			self.color = set_color([1,1,1,1])
			self.ellps = Ellipse(
				pos=(-1,-1),size=(2,2),
				texture=tex,
				angle_start=start,angle_end=end)
			PopMatrix()

			self.bind(pos=self._updatePos)
			self.bind(size=self._updateSize)

	def _updatePos(self,obj,pos):
		self.pos = pos
	def _updateSize(self,obj,size):
		self.size = size

	def update(self,x,y,radius,scale,start=0,end=360):
		self.trans.x = x
		self.trans.y = y
		self.scale.x = radius*scale
		self.scale.y = radius*scale
		self.ellps.angle_start = start
		self.ellps.angle_end = end


class GridCircle(Widget):
	# gitter im kreis
	def __init__(self,radius=100,scale=1.0,**kw):
		super(GridCircle,self).__init__(**kw)
		circle0 = (0,0,scale)
		points1 = [1,0,scale,0]
		points2 = [-1,0,-scale,0]
		points3 = [0,1,0,scale]
		points4 = [0,-1,0,-scale]

		with self.canvas:
			PushMatrix()
			self.trans = Translate(0,0)
			self.color = set_color([0,0,0,1])

			self.scale = Scale(x=radius,y=radius,origin=(0,0))
			self.circle0 = Line(circle=circle0,width=1)
			self.line1 = Line(points=points1,width=0.3)
			self.line2 = Line(points=points2,width=0.3)
			self.line3 = Line(points=points3,width=0.3)
			self.line4 = Line(points=points4,width=0.3)
			PopMatrix()
			self.bind(pos=self._updatePos)
			self.bind(size=self._updateSize)

	def _updatePos(self,obj,pos):
		self.pos = pos
	def _updateSize(self,obj,size):
		self.size = size

	def update(self,x,y,radius,scale,lwidth=1.0):
			circle0 = (0,0,scale)
			points1 = [1,0,scale,0]
			points2 = [-1,0,-scale,0]
			points3 = [0,1,0,scale]
			points4 = [0,-1,0,-scale]
			lwidth3 = lwidth/3.0
			self.trans.x = x
			self.trans.y = y
			self.scale.x = self.scale.y = radius
			self.circle0.circle = circle0
			self.circle0.width = lwidth
			self.line1.points = points1
			self.line2.points = points2
			self.line3.points = points3
			self.line4.points = points4
			self.line1.width = lwidth3
			self.line2.width = lwidth3
			self.line3.width = lwidth3
			self.line4.width = lwidth3

	def enable(self,opaque=1):
		self.color.a = opaque


class GridBar(Widget):
	# gitterstäbe in den balken
	def __init__(self,**kw):
		super(GridBar,self).__init__(**kw)

		with self.canvas:
			PushMatrix()
			self.trans = Translate(0,0)
			self.rot = Rotate(angle=0.0,origin=(0,0))
			self.scale = Scale(x=1.0,y=1.0,origin=(0,0))
			self.color = set_color([0,0,0,1])
			self.line1 = Line(points=(1.0,1.0,1.0,-1.0),width=100)
			self.line2 = Line(points=(-1.0,1.0,-1.0,-1.0),width=100)
			PopMatrix()
			self.bind(pos=self._updatePos)
			self.bind(size=self._updateSize)

	def _updatePos(self,obj,pos):
		self.pos = pos
	def _updateSize(self,obj,size):
		self.size = size

	def update(self,x,y,radius,scale,lwidth=1.0,turn=False):
		width = lwidth/scale
		width3 = width/3.0
		angle = 0.0
		if turn:
			angle = 90.0
		sr = scale*radius
		self.trans.xy = (x,y)
		self.rot.angle = angle
		self.scale.x = sr
		self.scale.y = sr
		self.line1.width = width3
		self.line2.width = width3

	def enable(self,opaque=1):
		self.color.a = opaque


class LAngleViewBubble(LAngleView,FloatLayout):
	def __init__(self,**kw):
		super(LAngleViewBubble, self).__init__(**kw)
		self.bubbleObj = Bubble()
		self.add_widget(self.bubbleObj)
		self.gridCircleObj = GridCircle()
		self.add_widget(self.gridCircleObj)
		self.gridBarObj = GridBar()
		self.add_widget(self.gridBarObj)
		self.value = None

	# die Luftblase
	def bubble(self,x,y,radius,scale,start=0,end=360,opaque=1):
		self.bubbleObj.update(x,y,radius,scale,start=start,end=end)

	# gitterstäbe im kreis
	def grid(self,x,y,radius,scale,lwidth=1.0,opaque=1):
		self.gridBarObj.enable(0.0)
		self.gridCircleObj.enable(1.0)
		self.gridCircleObj.update(x,y,radius,scale,lwidth=lwidth)

	# gitterstäbe in den balken
	def frame(self,x,y,radius,scale,lwidth=1.0,turn=False,opaque=1):
		self.gridCircleObj.enable(0.0)
		self.gridBarObj.enable(1.0)
		self.gridBarObj.update(x,y,radius,scale,lwidth=lwidth,turn=turn)

	def textbox(self,value,x,y,angle=0,anchor=(0,0),apos=0,asel=0,radius=300.0):
		grad = "\u00b0"
		arrow = ["\u25b2","\u25b6","\u25bc","\u25c0"]
		# Anm: DejaVuSans hat diese Zeichen, Roboto nicht.
		fsiz = LFont.middle()*1.3*radius/300.0

		rotated_text(
			#"88.8"+grad+"8",
			"888888",
			pos=(x,y),
			angle=angle,
			#font_name = "RobotoMono-Regular.ttf",
			font_name = "DejaVuSans.ttf",
			font_size=fsiz,
			anchor=anchor,
			color=[0.15,0.15,0.15,1],
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
			font_size=fsiz,
			anchor=anchor,
			color=[0.0,1.0,0.05,1])

	def scene_flat(self,value,x,y,cx,cy,radius,scale):
		wid = 3.0/300.0
		bx = cx + (x-cx)*(1.0-scale)
		by = cy + (y-cy)*(1.0-scale)
		self.bubble(bx,by,radius,scale)
		self.grid(cx,cy,radius,scale,lwidth=wid)

		if self.size[1] > self.size[0]:
			bx = self.pos[0] + self.size[0]*.5
			by = (self.pos[1] + (cy-radius))/2
			self.textbox(value.roll(), bx,by,anchor=(-1.2,0),asel=1,apos=0,radius=radius)
			self.textbox(value.pitch(), bx,by,anchor=(1.2,0),asel=0,apos=1,radius=radius)
		else:
			by = self.pos[1] + self.size[1]*.5
			bx = (self.pos[0] + self.size[0] + (cx+radius))/2
			self.textbox(-value.roll(), bx,by,anchor=(1.2,0),asel=0,apos=1,angle=90,radius=radius)
			self.textbox(value.pitch(), bx,by,anchor=(-1.2,0),asel=1,apos=0,angle=90,radius=radius)

	def scene_up(self,value,x,y,cx,cy,radius,scale):
		#wid = 3.0/max(radius,0.01)
		wid = 3.0/300.0
		if self.val_ori in ['BOTTOM']:
			bx = cx + (x-cx)*(1.0-scale)
			by = cy + scale*radius
			self.bubble(bx,by,radius,scale,start=90,end=270)
			self.frame(cx,cy,radius,scale,lwidth=wid)
		elif self.val_ori in ['TOP']:
			bx = cx + (x-cx)*(1.0-scale)
			by = cy - scale*radius
			self.bubble(bx,by,radius,scale,start=270,end=450)
			self.frame(cx,cy,radius,scale,lwidth=wid)
		elif self.val_ori in ['LEFT']:
			bx = cx + scale*radius
			by = cy + (y-cy)*(1.0-scale)
			self.bubble(bx,by,radius,scale,start=180,end=360)
			self.frame(cx,cy,radius,scale,lwidth=wid,turn=True)
		elif self.val_ori in ['RIGHT']:
			bx = cx - scale*radius
			by = cy + (y-cy)*(1.0-scale)
			self.bubble(bx,by,radius,scale,start=0,end=180)
			self.frame(cx,cy,radius,scale,lwidth=wid,turn=True)

		if self.val_ori in ['BOTTOM']:
			bx = self.pos[0] + self.size[0]*.5
			by = (self.pos[1] + (cy-radius*scale))/2
			self.textbox(value.balance(), bx,by,anchor=(0,0),asel=0,apos=1,radius=radius)
		elif self.val_ori in ['TOP']:
			bx = self.pos[0] + self.size[0]*.5
			by = (self.pos[1] + self.size[1] + (cy+radius*scale))/2
			self.textbox(value.balance(), bx,by,anchor=(0,0),asel=0,apos=1,angle=180,radius=radius)
		elif self.val_ori in ['LEFT']:
			by = self.pos[1] + self.size[1]*.5
			bx = (self.pos[0] + (cx-radius*scale))/2
			self.textbox(value.balance(), bx,by,anchor=(0,0),asel=0,apos=1,angle=-90,radius=radius)
		elif self.val_ori in ['RIGHT']:
			by = self.pos[1] + self.size[1]*.5
			bx = (self.pos[0] + self.size[0] + (cx+radius*scale))/2
			self.textbox(value.balance(), bx,by,anchor=(0,0),asel=0,apos=1,angle=90,radius=radius)

	def on_value(self, inst, value):
		if value is None: return

		#print ('object:',self,'on_value called')
		self.value = value
		radius = self.bckgnd.get_meter_length()/2.0
		center = self.bckgnd.get_tacho_center()
		scale = self.bckgnd.get_meter_aspect()
		cx = center[0]
		cy = center[1]

		x,y = value.xy()
		x = x*radius/45.0 + cx
		y = y*radius/45.0 + cy

		# Graphik (löschen und) neu aufbauen:

		self.canvas.after.clear()			# brauchts noch wegen text.  !!!!
		with self.canvas.after:
			if self.val_ori in ['LANDING','FLYING']:
				self.scene_flat(value,x,y,cx,cy,radius,scale)
			else:
				self.scene_up(value,x,y,cx,cy,radius,scale)

#=============================================================================
# Kugel Drahtmodel.

class LAngleViewKugel(LAngleView):
	def __init__(self,**kw):
		super(LAngleViewKugel, self).__init__(**kw)
		self.l3d = None
		self.light = True
		self.rotation = None
		self.rotaphi = None
		self.rottext = None
		self.translation = None
		self.scale = None

	def Line3d(self,x1,y1,x2,y2,width=1.0):
		dx = x2-x1
		dy = y2-y1
		l = math.sqrt(dx*dx+dy*dy)
		#a = math.atan2(dy,dx)
		w = width

		#print ("dx,dy = {0: 5.2f},{1: 5.2f}".format(dx,dy))
		#print ("l,a = {0: 5.2f},{1: 5.2f}".format(l,a))
		#print ("width",width,w)
		#w = 1.0

		self.l3d.add(PushMatrix())
		self.l3d.add(Translate(x1,y1,0))
		self.l3d.add(Rotate(angle=math.degrees(math.atan2(dy,dx)),axis=(0,0,1),origin=(0,0,0)))
		self.l3d.add(Scale(x=l,y=1,z=1,origin=(0,0,0)))
		self.l3d.add(Line(points=(0.0,0.0,1.0,0.0),width=w))
		self.l3d.add(Rotate(angle=90.0,axis=(1,0,0),origin=(0,0,0)))
		self.l3d.add(Line(points=(0.0,0.0,1.0,0.0),width=w))
		#self.l3d.add(Rotate(angle=45.0,axis=(1,0,0),origin=(0,0,0)))
		#self.l3d.add(Line(points=(0.0,0.0,1.0,0.0),width=w))
		#self.l3d.add(Rotate(angle=45.0,axis=(1,0,0),origin=(0,0,0)))
		#self.l3d.add(Line(points=(0.0,0.0,1.0,0.0),width=w))
		self.l3d.add(PopMatrix())

	def Circle3d(self,circle=(0.0,0.0,1.0),width=1.0):
		n = 36
		r = circle[2]
		for i in range(0,n):
			ii = float(i)
			a0 = ii*2*math.pi/n
			a1 = (ii+1)*2*math.pi/n
			self.Line3d(
				r*math.cos(a0),
				r*math.sin(a0),
				r*math.cos(a1),
				r*math.sin(a1),
				width=width)

	def breiten(self,width=1.0):

		self.l3d.add(Color(0.1,0.1,0.1,1))
		self.l3d.add(PushMatrix())
		self.Circle3d(circle=(0,0,1),width=width)
		for i in range(1,6):
			s = math.sin(math.radians(i*15))
			c = math.cos(math.radians(i*15))
			self.l3d.add(Translate(0,0,s))
			if self.light:
				if i == 2:
					self.Circle3d(circle=(0,0,c),width=width)
				elif i == 5:
					self.Circle3d(circle=(0,0,c),width=width)
				else:
					self.l3d.add(Line(circle=(0,0,c),width=1.0))
			else:
				self.Circle3d(circle=(0,0,c),width=width)
			self.l3d.add(Translate(0,0,-s))
		for i in range(1,6):
			s = math.sin(math.radians(i*15))
			c = math.cos(math.radians(i*15))
			self.l3d.add(Translate(0,0,-s))
			if self.light:
				if i == 2:
					self.Circle3d(circle=(0,0,c),width=width)
				elif i == 5:
					self.Circle3d(circle=(0,0,c),width=width)
				else:
					self.l3d.add(Line(circle=(0,0,c),width=1.0))
			else:
				self.Circle3d(circle=(0,0,c),width=width)
			self.l3d.add(Translate(0,0,s))
		self.l3d.add(PopMatrix())

	def pole(self,size=0.02):
		pos = -size/2.0
		self.l3d.add(PushMatrix())
		self.l3d.add(Rotate(angle=-90.0,axis=(1,0,0),origin=(0,0,0)))
		self.l3d.add(Translate(0.0,1.0,0.0))
		self.l3d.add(Rotate(angle=90.0,axis=(1,0,0),origin=(0,0,0)))
		self.l3d.add(set_color([0.7,0.0,0.0,0.7]))
		self.l3d.add(Ellipse(pos=(pos,pos),size=(size,size)))
		self.l3d.add(PopMatrix())

		self.l3d.add(PushMatrix())
		self.l3d.add(Rotate(angle=-90.0,axis=(1,0,0),origin=(0,0,0)))
		self.l3d.add(Translate(0.0,-1.0,0.0))
		self.l3d.add(Rotate(angle=90.0,axis=(1,0,0),origin=(0,0,0)))
		self.l3d.add(set_color([0.0,0.0,0.7,0.7]))
		self.l3d.add(Ellipse(pos=(pos,pos),size=(size,size)))
		self.l3d.add(PopMatrix())

	def meridiane(self,width=1.0):
		#self.l3d.add(Color(0.1,0.1,0.1,1))
		self.l3d.add(set_color([0.1,0.1,0.1,1]))
		self.l3d.add(PushMatrix())
		self.l3d.add(Rotate(angle=90,axis=(0,1,0),origin=(0,0,0)))
		self.Circle3d(circle=(0,0,1),width=width)
		#self.ellipse(1)
		for i in range(1,12):
			self.l3d.add(Rotate(angle=15,axis=(1,0,0),origin=(0,0,0)))
			if i==6:
				self.Circle3d(circle=(0,0,1),width=width)
				#self.ellipse(1)
			else:
				if self.light:
					self.l3d.add(Line(circle=(0,0,1),width=1.0))
				else:
					self.Circle3d(circle=(0,0,1),width=width)
		self.l3d.add(PopMatrix())


	def anschrift_setup(self,canvas,value,cx,cy,radius):
		anf = LFont.angle()*1.5*radius/300.0
		coltxt = self.textcolor(value.balance())

		if self.rottext is None:
			self.rottext = RotatedText()
			self.rottext.setup(
				canvas,
				text="{0: 4.1f}\u00b0".format(value.balance()),
				pos=(cx,cy,0),
				angle=value.phi-90.0,
				anchor=(0,0),
				font_size=anf,
				color=coltxt)
				#bcolor=[0.45,0.45,0.45,0.5])

	def anschrift_update(self,value,cx,cy,radius):
		anf = LFont.angle()*1.5*radius/300.0
		coltxt = self.textcolor(value.balance())

		if self.rottext is not None:
			self.rottext.update(
				text="{0: 4.1f}\u00b0".format(value.balance()),
				pos=(cx,cy,0),
				angle=value.phi-90.0,
				font_size=anf,
				color=coltxt)

	def loadScene(self,canvas,width=1.0):
		if self.l3d is None:
			self.l3d = InstructionGroup()
			self.breiten(width=width)
			self.meridiane(width=width)
			self.pole(size=0.05)
		if self.l3d is not None:
			canvas.add(self.l3d)

	def kugel(self,value,x,y,radius,width=1.0):
		PushMatrix()
		self.translation = Translate(x,y,0)
		self.scale = Scale(x=radius*0.92,y=radius*0.92,z=0,origin=(0,0,0))

		if value is not None:
			theta = value.theta
			#if theta > 90.0: theta = (180 - theta)
			self.rotation = Rotate(angle=theta,axis=(-value.pitch(),value.roll(),0),origin=(0,0,0))
			self.rotaphi = Rotate(angle=value.phi,axis=(0,0,1),origin=(0,0,0))

		self.loadScene(self.canvas,width=width)
		PopMatrix()

	def textcolor(self,bal):
		p = math.fabs(bal)*0.2
		cr = hsva_conv([0.0,0.8,0.5,1])
		#co = hsva_conv([0.18,0.8,0.7,1])
		co = hsva_conv([0.09,0.8,0.6,1])
		cg = hsva_conv([0.32,0.8,0.4,1])
		coltxt = color_range_ext(cg,cg,cg,co,co,co,co,co,co,co,co,co,co,cr,cr,param=p)
		return coltxt

	def on_value(self, inst, value):
		if value is None: return
		radius = self.bckgnd.get_tacho_radius()
		center = self.bckgnd.get_tacho_center()
		if radius is None: return

		cx = center[0]
		cy = center[1]
		y = value.pitch()
		x = value.roll()
		x = x*radius/90.0 + cx
		y = y*radius/90.0 + cy

		size = self.size[1]/2.0
		if self.size[0] > self.size[1]: size = self.size[0]/2.0

		# Update
		if self.rotation is not None:
			if self.translation is not None:
				# nur kugel
				self.translation.x = cx
				self.translation.y = cy
				self.scale.x = size*0.92
				self.scale.y = size*0.92
			# kugel und kugelP
			self.rotation.axis=(-value.pitch(),value.roll(),0)
			self.rotation.angle = value.theta
			self.rotaphi.angle = value.phi

			self.anschrift_update(value,cx,cy,radius)
			return

		with self.canvas:
			set_color([0.1,0.1,0.1,1])  # (nicht ganz schwarz)
			if radius > 0.0:
				self.kugel(value,cx,cy,size,width=0.003)

		self.anschrift_setup(self.canvas,value,cx,cy,radius)

#=============================================================================
# Kugel Drahtmodel mit Perspektive.

from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST

class LAngleViewKugelP(LAngleViewKugel):
	def __init__(self,**kw):
		super(LAngleViewKugelP, self).__init__(**kw)
		self.rectangle = None
		self.circleText = None
		self.circleTrans = None
		with self.canvas:
			self.fbo = Fbo(with_depthbuffer=True)
			self.fbo.shader.source = 'glsl/default.glsl'

	def setup_gl_context(self, *args):
		glEnable(GL_DEPTH_TEST)

	def reset_gl_context(self, *args):
		glDisable(GL_DEPTH_TEST)

	def textPosZ(self,bal):
		bal = math.fabs(bal)
		val = 0.9-(bal/25.0)
		if val<-0.9: val = -0.9
		if val>0.9: val = 0.9
		# print("z=",val," balance",bal)
		return val

	def kugel(self,value,x,y,radius,width=1.0):
		# Fbo ist unabh. von absoluten Grössen. Die Skalierung erfolgt bei
		# der Platzierung der Textur, sodass die Kugel immer eine Kugel
		# bleibt. Wir verwenden die default buffer grösse (1024x1024)
		zscale = 1.0
		radius = 1.3
		#matvc = Matrix().view_clip(-sx,sx,-sy,sy,2.9*zscale,5.1*zscale,1)
		matvc = Matrix().view_clip(-1.0,1.0,-1.0,1.0,2.9*zscale,5.1*zscale,1)
		self.fbo['projection_mat'] = matvc
		print (matvc)

		with self.fbo:
			ClearColor(0, 0, 0, 0)
			ClearBuffers(clear_depth=True)
			Callback(self.setup_gl_context)

			PushMatrix()
			Translate(0,0,-4*zscale)
			Scale(x=radius*0.92,y=radius*0.92,z=zscale,origin=(0,0,0))

			# Kreis als Text Hintergrund
			posZ = self.textPosZ(value.balance())
			PushMatrix()
			rsiz = 0.7
			self.circleTrans = Translate(0,0,posZ-0.01)
			Color(0.45,0.45,0.45,1)
			RoundedRectangle(pos=(-rsiz/2.0,-rsiz/2.0),size=(rsiz,rsiz))
			PopMatrix()

			# Text Anzeige in die Scene einpassen
			PushMatrix()
			scfac = 300.0
			Scale(x=1.0/scfac,y=1.0/scfac,z=1.0,origin=(0,0,0))
			if self.circleText is None:
				self.circleText = RotatedText()
			self.circleText.setup(self.fbo,
				text="{0: 4.1f}\u00b0".format(value.balance()),
				pos=(0,0,posZ),
				angle=value.phi-90.0,
				anchor=(0,0),
				font_size=LFont.angle(),
				color=self.textcolor(value.balance()))
			PopMatrix()

			# die szene wir abhängig von der Lage gedreht.
			theta = value.theta
			self.rotation = Rotate(
				angle=theta,
				axis=(-value.pitch(),value.roll(),0),
				origin=(0,0,0))
			self.rotaphi = Rotate(
				angle=value.phi,
				axis=(0,0,1),
				origin=(0,0,0))

			self.loadScene(self.fbo,width=0.003)
			PopMatrix()

			Callback(self.reset_gl_context,reset_buffer=True)

		if self.size[1] > self.size[0]:
			sx = self.size[0]/self.size[1]
			sy = 1.0
		else:
			sx = 1.0
			sy = self.size[1]/self.size[0]

		PushMatrix()
		Color(1,1,1,1)
		self.scale = Scale(x=1.0/sx,y=1.0/sy,z=zscale,origin=(x,y,0))
		self.rectangle = Rectangle(texture=self.fbo.texture,pos=self.pos,size=self.size)
		PopMatrix()

	def on_value(self, inst, value):
		if value is None: return
		center = self.bckgnd.get_tacho_center()
		cx,cy = center
		if self.size[1] > self.size[0]:
			sx = self.size[0]/self.size[1]
			sy = 1.0
		else:
			sx = 1.0
			sy = self.size[1]/self.size[0]

		# Refresh
		if self.rectangle is not None:
			origin = (cx,cy,0)
			self.scale.x = 1.0/sx
			self.scale.y = 1.0/sy
			self.scale.origin = origin
			self.rectangle.texture = self.fbo.texture
			self.rectangle.pos = self.pos
			self.rectangle.size = self.size
			#center = self.bckgnd.get_tacho_center()

			posZ = self.textPosZ(value.balance())
			if self.circleText is not None:
				self.circleText.update(
					text="{0: 4.1f}\u00b0".format(value.balance()),
					pos=(0,0,posZ),
					angle=value.phi-90.0,
					color=self.textcolor(value.balance()))
			self.circleTrans.z = posZ-0.01

		radius = self.bckgnd.get_tacho_radius()
		if radius is None: return

		y = value.pitch()
		x = value.roll()
		x = x*radius/90.0 + cx
		y = y*radius/90.0 + cy

		size = self.size[1]/2.0
		if self.size[0] > self.size[1]: size = self.size[0]/2.0

		# Update
		if self.rotation is not None:
			self.rotation.axis=(-value.pitch(),value.roll(),0)
			self.rotation.angle = value.theta
			self.rotaphi.angle = value.phi
			return

		with self.canvas:
			set_color([0.1,0.1,0.1,1])  # (nicht ganz schwarz)
			if radius > 0.0:
				self.kugel(value,cx,cy,size,width=0.003)

#=============================================================================

class LAngleViewCube(LAngleView):
	textex = ObjectProperty()
	texbal = ObjectProperty()

	def __init__(self,**kw):
		super(LAngleViewCube, self).__init__(**kw)

		self.fborect = None
		self.rotation = None
		self.fboscale = None
		self.fbocolor = None
		self.rectstex = []
		self.rectsbal = []

		with self.canvas:
			self.fbo = Fbo(size=(1024,1024),with_depthbuffer=True)
			#self.fbo.shader.source = 'glsl/default.glsl'

		self.fbo.add_reload_observer(self.reinit)
		self.reinit(self.fbo)

		self.trnp = 0.5
		self.gradi = Gradient.centered([0,1,0,self.trnp],[1,1,0,self.trnp])
		self.rbow = Gradient.centered(
			[1.0,1.0,0.7,self.trnp],[0.0,1.0,0.7,self.trnp],hsva=True,
			center=(1.2,0.3),radius=1.2,size=128)

	def reinit(self,fbo):
		print ('********** reload observer call construct ************')
		self.frect = None
		self.rotation = None
		self.rectstex = []
		self.rectsbal = []

	def setup_gl_context(self, *args):
		glEnable(GL_DEPTH_TEST)

	def reset_gl_context(self, *args):
		glDisable(GL_DEPTH_TEST)

	def on_textex(self, inst, newtex):
		#print ('textex updated')
		for r in self.rectstex:
			r.texture = newtex

	def on_texbal(self, inst, newtex):
		#print ('texbal updated')
		for r in self.rectsbal:
			r.texture = newtex

	def mytext(self,val,color=[0,0,0,1],font_size=120):
		if math.fabs(val)<10.0:
			text = "{0: 3.2f}\u00b0".format(val)
		else:
			text = "{0: 4.1f}\u00b0".format(val)
		l = Label(text=text,font_size=font_size,pos=(-100,-100))
		l.color = color
		l.texture_update()
		return l.texture

	# Szene Aufbau:

	def face(self,color=[0.5,0.5,0.5,1],tex=None,grad=None):
		PushMatrix()
		Translate(0,0,0.5,origin=(0,0,0))
		if grad is not None:
			set_color([1,1,1,1])
			Rectangle(texture=grad,pos=(-0.5,-0.5),size=(1.0,1.0))
		else:
			set_color(color)
			Rectangle(pos=(-0.5,-0.5),size=(1.0,1.0))
		if tex is not None:
			Translate(0,0,0.01,origin=(0,0,0))
			set_color([1,1,1,1])
			rect = Rectangle(texture=tex,pos=(-0.5,-0.3),size=(1.0,0.6))
			if tex is self.textex:
				self.rectstex.append(rect)
			if tex is self.texbal:
				self.rectsbal.append(rect)
		PopMatrix()

	def rects(self,tex1=None,tex2=None,
			grad1=None,grad2=None,
			color1=[0.5,0.5,0.5,1],color2=[0.5,0.5,0.5,1]):
		PushMatrix()
		self.face(color=color1,tex=tex1,grad=grad1)
		Rotate(angle=180,origin=(0,0,0),axis=(0.0,0.0,1.0))
		Rotate(angle=180,origin=(0,0,0),axis=(1.0,0.0,0.0))
		self.face(color=color2,tex=tex2,grad=grad2)
		PopMatrix()

	def cube(self):
		invers = False
		if invers:
			Rotate(angle=180,origin=(0,0,0),axis=(0.0,0.0,1.0))
			Rotate(angle=180,origin=(0,0,0),axis=(1.0,0.0,0.0))
		self.rects(color1=[1,0,0,self.trnp],color2=[1,0,0,self.trnp],
			grad1=self.rbow,grad2=self.rbow,
			tex1=self.textex,tex2=self.textex)
		if invers:
			Rotate(angle=-90,origin=(0,0,0),axis=(1.0,0.0,0.0))
		else:
			Rotate(angle=90,origin=(0,0,0),axis=(1.0,0.0,0.0))
		self.rects(color1=[0,1,0,self.trnp],color2=[0,1,0,self.trnp],
			grad1=self.gradi,grad2=self.gradi,
			tex1=self.texbal,tex2=self.texbal)
		if invers:
			Rotate(angle=-90,origin=(0,0,0),axis=(0.0,1.0,0.0))
		else:
			Rotate(angle=90,origin=(0,0,0),axis=(0.0,1.0,0.0))
		self.rects(color1=[0,0,1,self.trnp],color2=[0,0,1,self.trnp],
			tex1=self.texbal,tex2=self.texbal)

	# Update
	def on_value(self, inst, value):

		self.textex = self.mytext(value.theta)
		self.texbal = self.mytext(value.bala)
		# ANM: object properties -> update über events.

		cx,cy = self.bckgnd.get_tacho_center()
		if self.size[1] > self.size[0]:
			sx = self.size[1]/self.size[0]
			sy = 1.0
		else:
			sx = 1.0
			sy = self.size[0]/self.size[1]

		# Scene ist bereits konstruiert -> Update.
		if self.rotation is not None:
			self.rotation.axis = (-value.pitch(),value.roll(),0)
			self.rotation.angle = value.theta
			self.fboscale.x = sx
			self.fboscale.y = sy
			self.fboscale.origin = (cx,cy,0)
			self.fborect.texture = self.fbo.texture
			self.fborect.pos = self.pos
			self.fborect.size = self.size
			return

		# Hier definieren wir die perspektive. Wir skalieren die Szene
		# in z mit 1, d.h zw. -1 und +1, stellen sie dann 4 z-Einheiten weg
		# von der Kamera und setzen vorderes und hinteres clipping auf
		# 3 (near) resp. 5 (far) z-einheiten.

		zscale = 1.0
		matvc = Matrix().view_clip(-1.0,1.0,-1.0,1.0,3*zscale,5*zscale,1)
		self.fbo['projection_mat'] = matvc
		print (matvc)

		with self.fbo:
			ClearColor(0, 0, 0, 0)
			ClearBuffers(clear_depth=True)
			Callback(self.setup_gl_context)

			PushMatrix()
			# die folgenden 2 Befehle müssen mit der view-clip matrix
			# abgeglichen sein - sonst sieht man ganz schnell nichts mehr!
			Transform().translate(0,0,-4*zscale)
			Scale(x=1.2,y=1.2,z=zscale,origin=(0,0,0))

			self.rotation = Rotate(
				angle=value.theta,
				axis=(-value.pitch(),value.roll(),0),
				origin=(0,0,0))

			self.cube()

			PopMatrix()
			Callback(self.reset_gl_context,reset_buffer=True)

		print(self.fbo.texture)

		#self.canvas.after.clear()
		#with self.canvas.after:
		with self.canvas:
			PushMatrix()
			self.fbocolor = Color(1,1,1,1)
			self.fboscale = Scale(x=sx,y=sy,z=zscale,origin=(cx,cy,0))
			self.fborect = Rectangle(texture=self.fbo.texture,pos=self.pos,size=self.size)
			PopMatrix()

#=============================================================================
