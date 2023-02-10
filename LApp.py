#!/usr/bin/python

# -*- mode: python; coding: utf-8; -*-

import os
#print ('KIVY_HOME: '+os.environ['KIVY_HOME'])

import logging

from kivy.graphics import *
from kivy.app import App
from kivy.uix.image import Image as KivyImage
from kivy.animation import Animation
from kivy.uix.actionbar import *
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty

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
# graphic helpers

def rotated_text(text,x,y,angle=0,font_size=16,anchor=(0,0),color=[1,1,1,1]):
	l = Label(text=text,font_size=font_size,pos=(-100,-100))
	l.color = color
	l.texture_update()
	t = l.texture
	xo = t.size[0] * (anchor[0]-1) / 2.0
	yo = t.size[1] * (anchor[1]-1) / 2.0
	PushMatrix()
	Rotate(angle=angle,origin=(x,y))
	Rectangle(texture=t,pos=(x+xo,y+yo),size=t.size)
	PopMatrix()

def set_color(color=[0,0,0,0]):
	Color(color[0],color[1],color[2],color[3])

def set_color_range(cfrom=[0,0,0,0],cto=[1,1,1,1],param=0.5):
	if param<0.0: color = cfrom
	elif param > 1.0: color = cto
	else:
		color = [ (cfrom[i]+param*(cto[i]-cfrom[i])) for i in range(0,4) ]
	Color(color[0],color[1],color[2],color[3])

# =============================================================================
# kivy EventDispatcher passes keywords, that to not correspond to properties
# to the base classes. Finally they will reach 'object'. With python3 (but not
# python2) 'object' throws an exception 'takes no parameters' in that a
# situation. We therefore underlay a base class (right outside), which
# swallows up remaining keywords. Thus the keywords do not reach 'object' any
# more.


class LBase(object):
	def __init__(self, **kw):
		super(LBase, self).__init__()

#=============================================================================

class LabelButton(ButtonBehavior, Label, LBase):

	def __init__(self, **kw):
		super(LabelButton, self).__init__(**kw)

		with self.canvas.before:
			PushMatrix()
			self.rotate = Rotate(angle=0.0,origin=(744.0,299.0))
		with self.canvas.after:
			PopMatrix()
		self.bind(pos=self.update)
		self.bind(size=self.update)

	def update(self,*args):
		mid = (self.size[0]/2.0,self.size[1]/2.0)
		cntr = (self.pos[0]+mid[0],self.pos[1]+mid[1])
		self.rotate.origin = cntr

	def update_angle(self,angle):
		self.rotate.angle = angle

	def on_press(self):
		#self.source = 'atlas://data/images/defaulttheme/checkbox_on'
		pass

	def on_release(self):
		#self.source = 'atlas://data/images/defaulttheme/checkbox_off'
		pass

#=============================================================================

def normAngle(angle):
	while angle < -180.0: angle += 360.0
	while angle >= 180.0: angle -=360.0
	if angle > 90.0: angle = 180.0 - angle
	if angle < -90.0: angle = -180.0 - angle
	return angle

#=============================================================================

class LCala(object):

	def __init__(self):
		self.cala_angle = 0.0		# durchschnit gemessener abweichungen.
		self.cala_cnt = 0				# anzahl werte

	def reset(self):
		self.cala_angle = 0.0
		self.cala_cnt = 0

	def addValue(self,angle,soll):
		self.cala_cnt += 1
		delta = angle-soll
		# wir berechnen die resultierende Abweichung
		self.cala_angle = ((self.cala_cnt-1)*self.cala_angle + delta) / self.cala_cnt

	def getValue(self):
		# wir geben den Korrekturwert zurück
		return -self.cala_angle;

	def getCount(self):
		return self.cala_cnt;

#=============================================================================

class LCalaStore(object):

	def __init__(self):
		self.store = {}
		self.accept_one = False

	def reset(self):
		self.store = {}
		self.accept_one = False
		print ("LCalaStore: reset()")

	def accept(self):
		self.accept_one = True
		print ("LCalaStore: accept()")

	def numCalibrated(self,values):
		ori = values.orientation()
		if ori not in self.store: return 0

		cntX = self.store[ori]['X'].getCount()
		cntY = self.store[ori]['Y'].getCount()
		return max(cntX,cntY)

	def isCalibrated(self,values):
		ori = values.orientation()
		if ori not in self.store: return None

		valX = round(self.store[ori]['X'].getValue(),1)
		valY = round(self.store[ori]['Y'].getValue(),1)
		valZ = 0.0
		vz2 = values.g*values.g-valX*valX-valY*valY
		if vz2 > 0.0:
			valZ = round(values.g-math.sqrt(vz2),1)

		return str(valX)+'/'+str(valY)+'/'+str(valZ)

	def addCalibration(self,rawValue):
		if not self.accept_one: return

		ori = rawValue.orientation()
		if  ori not in self.store:
			self.store[ori] = { 'X':LCala(),'Y':LCala() }
		if ori in ["LANDING","FLYING"]:
			self.store[ori]['X'].addValue(rawValue.valX,0)
			self.store[ori]['Y'].addValue(rawValue.valY,0)
		elif ori in ["TOP","BOTTOM"]:
			self.store[ori]['X'].addValue(rawValue.valX,0)
		else:
			self.store[ori]['Y'].addValue(rawValue.valY,0)
		print ("LCalaStore: new value added")
		self.accept_one = False

	def calibrate(self,rawValue):
		ori = rawValue.orientation()
		if ori not in self.store: return rawValue

		valX = self.store[ori]['X'].getValue()
		valY = self.store[ori]['Y'].getValue()
		# die Korrektur der z-Komponente errechnet sich über g.
		valZ = 0.0
		vz2 = rawValue.g*rawValue.g-valX*valX-valY*valY
		if vz2 > 0.0:
			valZ = rawValue.g-math.sqrt(vz2)

		return LValue(rawValue.valX+valX,rawValue.valY+valY,rawValue.valZ+valZ)

	def handleCalibration(self,rawValue):
		self.addCalibration(rawValue)
		return self.calibrate(rawValue)

#=============================================================================

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
		self.center = [0,0]
		self.radius = None

	def on_val_ori(self,*args):
		self.update()

	def update(self, *args):
		Clock.unschedule(self.update_event)
		self.update_event = Clock.schedule_once(self.update_scheduled, 0.2)

	def update_scheduled(self, *args):
		self.msiz = msiz = min(self.size[0],self.size[1])
		self.radius = msiz/2.0
		rpos = (self.pos[0]+(self.size[0]-msiz)/2,self.pos[1]+(self.size[1]-msiz)/2)
		self.center = center = (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)
		#print ('LCircleView',msiz)

		self.canvas.before.clear()
		with self.canvas.before:

			if self.variante == 0:
				Color(0.5, 0.4, 1.0, 1)   # violett
				step = (msiz/2.0) / 45
				for i in range(5,45,10):
					Line(circle=(center[0],center[1],i*step),width=0.5)
				Line(circle=(center[0],center[1],45*step),width=0.7)

			if self.variante == 1:
				Color(0.7, 0.7, 0.7, 1)   # hellgrau
				step = (msiz/2.0) / 45
				for i in range(5,45,5):
					Line(circle=(center[0],center[1],i*step),width=0.5)
				Line(circle=(center[0],center[1],45*step),width=0.7)

			if self.variante == 2:
				self.radius = 0.9*msiz/2
				step = self.radius / 45
				m = msiz/2
				r = self.radius

				Color(0.7, 0.7, 0.7, 1)   # hellgrau
				for i in range(5,45,5):
					Line(circle=(center[0],center[1],i*step),width=0.5)
				Line(circle=(center[0],center[1],45*step),width=0.7)

				for i in range(-45,46,1):
					if i % 10 == 0:
						Line(points=[center[0]-m,center[1]+i*step,center[0]-r,center[1]+i*step],width=0.5)
						Line(points=[center[0]+m,center[1]+i*step,center[0]+r,center[1]+i*step],width=0.5)
						Line(points=[center[0]+i*step,center[1]-m,center[0]+i*step,center[1]-r],width=0.5)
						Line(points=[center[0]+i*step,center[1]+m,center[0]+i*step,center[1]+r],width=0.5)
					elif i % 5 == 0:
						Line(points=[center[0]-m+5,center[1]+i*step,center[0]-r,center[1]+i*step],width=0.5)
						Line(points=[center[0]+m-5,center[1]+i*step,center[0]+r,center[1]+i*step],width=0.5)
						Line(points=[center[0]+i*step,center[1]-m+5,center[0]+i*step,center[1]-r],width=0.5)
						Line(points=[center[0]+i*step,center[1]+m-5,center[0]+i*step,center[1]+r],width=0.5)
					else:
						Line(points=[center[0]-m+15,center[1]+i*step,center[0]-r,center[1]+i*step],width=0.5)
						Line(points=[center[0]+m-15,center[1]+i*step,center[0]+r,center[1]+i*step],width=0.5)
						Line(points=[center[0]+i*step,center[1]-m+15,center[0]+i*step,center[1]-r],width=0.5)
						Line(points=[center[0]+i*step,center[1]+m-15,center[0]+i*step,center[1]+r],width=0.5)

				axis = 1
				if self.val_ori in ['LEFT','TOP']: axis = -1
				self.draw_skala(axis_dir=axis)
				'''
				fs = 20
				for i in range(-45,46,1):
					if i % 10 == 0:
						rotated_text(str(i),center[0]-r,center[1]+i*step,font_size=fs)
						rotated_text(str(i),center[0]+r,center[1]+i*step,font_size=fs)
						rotated_text(str(i),center[0]+i*step,center[1]-r,font_size=fs)
						rotated_text(str(i),center[0]+i*step,center[1]+r,font_size=fs)

						#Line(points=[center[0]-m,center[1]+i*step,center[0]-r,center[1]+i*step],width=0.5)
						#Line(points=[center[0]+m,center[1]+i*step,center[0]+r,center[1]+i*step],width=0.5)
						#Line(points=[center[0]+i*step,center[1]-m,center[0]+i*step,center[1]-r],width=0.5)
						#Line(points=[center[0]+i*step,center[1]+m,center[0]+i*step,center[1]+r],width=0.5)
				'''


			if self.variante == 5:
				Color(0.5, 0.4, 1.0, 1)
				Bezier(points=(center[0],center[1],
							center[0]+msiz, center[1],
							center[0]+msiz/15.0, center[1]+msiz/15.0,
							center[0], center[1]+msiz,
							center[0],center[1]),loop=False)
				step = (msiz/2.0) / 45
				for i in range(5,45,10):
					Line(circle=(center[0],center[1],i*step),width=0.5)
				Line(circle=(center[0],center[1],45*step),width=0.7)

	def draw_skala(self,angle=None,axis_dir=1):
		fs = 20
		step = self.radius / 45
		c = self.center
		r = self.radius
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

	def get_radius(self):
		return self.radius

	def on_touch_down(self, touch):
		# double tap
		if touch.is_double_tap:
			self.variante += 1
			self.variante = self.variante % 3
			self.update()
		return False

#=============================================================================

class LWorkWindow(BoxLayout):
	def __init__(self,**kw):
		super(LWorkWindow, self).__init__(**kw)

		with self.canvas.before:
			Color(0, 0.00, 0.3, 1)   # schwarz mit blau stich
			Color(0.15, 0.00, 0.3, 1)   # schwarz mit violett stich
			#Color(0, 0.05, 0.1, 1)   # schwarz mit blau-grün stich
			#Color(0, 1, 1, 0.4)
			#Color(0.0, 0.0, 0.0, 1)   # schwarz
			self.rect = Rectangle(pos=self.pos, size=self.size)

		self.bind(pos=self.update)
		self.bind(size=self.update)
		self.update_event = None

		self.label_hidden = Label(pos=(-200,-200))
		#self.label_phi = LabelButton(text="",font_size=32)
		self.label_cal = LabelButton(text="",font_size=32)
		#self.label_theta = LabelButton(text="",font_size=32)
		#self.label_balance = LabelButton(text="",font_size=72)
		self.lcontainer = BoxLayout()
		#self.lcontainer.add_widget(self.label_phi)
		self.lcontainer.add_widget(self.label_cal)
		#self.lcontainer.add_widget(self.label_theta)
		self.circle_view = LCircleView()

		self.angle = 0.0
		self.value = 0.0
		self.ori = None
		self.calaStore = LCalaStore()
		self.calaResetEvent = None
		self.val_ori = "LANDING"

		self.variant = 0

	def update_content(self):
		self.clear_widgets()
		if self.size[0]>=self.size[1]:
		  self.orientation='horizontal'
		  self.lcontainer.orientation="vertical"
		  smin = self.size[1]
		else:
		  self.orientation='vertical'
		  self.lcontainer.orientation="horizontal"
		  smin = self.size[0]

		#self.circle_view = LCircleView()
		self.circle_view = LCircleView(size_hint=(None,None),width=smin,height=smin)
		self.add_widget(self.lcontainer)
		#self.add_widget(LCircleView(size_hint=(None,None),width=smin,height=smin))
		self.add_widget(self.circle_view)
		#self.add_widget(self.label_balance)
		self.add_widget(BoxLayout())

	def update(self, *args):
		Clock.unschedule(self.update_event)
		self.update_event = Clock.schedule_once(self.update_scheduled, 0.2)

	def update_deferred(self):
		self.rect.pos = self.pos
		self.rect.size = self.size
		self.update_content()
		self.draw_line()

	def update_scheduled(self, *args):
		self.update_deferred()
		return

	def refresh(self, valX, valY, valZ):
		rv = LValue(valX,valY,valZ)
		rc = self.calaStore.handleCalibration(rv)
		self.ori = rc
		self.draw_line()

	def draw_line(self):
		if self.ori is None: return
		if self.circle_view is None: return
		if self.circle_view.get_radius() is None: return

		if self.val_ori != self.ori.orientation():
			self.val_ori = self.ori.orientation()
			self.circle_view.val_ori = self.val_ori

		x = self.value
		y = self.angle
		#msiz = min(self.size[0],self.size[1])
		msiz = 2.0*self.circle_view.get_radius()
		rad = msiz/9.0
		center = (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)

		balance = (self.value-center[0])/100
		self.value = self.ori.theta
		self.angle = self.ori.phi

		txtangle = 0.0
		balance = self.ori.balance()
		x,y = self.ori.xy()
		txtangle = self.ori.txtori()

		x = x*msiz/2.0/45.0 + center[0]
		y = y*msiz/2.0/45.0 + center[1]

		#self.label_balance.text = "{0: 5.2f}\u00b0".format(balance)
		#self.label_balance.update_angle(txtangle)

		#cal = self.calaStore.isCalibrated(self.ori)
		#if cal is not None:
		#    self.label_cal.text = 'corr: '+cal
		#else:
		#    self.label_cal.text = ''

		cal = self.calaStore.numCalibrated(self.ori)
		if cal > 0:
			self.label_cal.text = str(cal)+' x calibrated'
		else:
			self.label_cal.text = ''

		#self.label_phi.text = "phi: {0: 5.1f}\u00b0".format(self.angle)
		#self.label_theta.text = "theta: {0: 5.1f}\u00b0".format(self.value)

		#else:
		#    self.label_phi.text = 'phi: '+str(round(self.angle,1))
		#    self.label_theta.text = 'theta: '+str(round(self.value,1))

		variante = self.variant
		radd = rad*0.1

		cx = center[0]
		cy = center[1]
		alf = math.atan2(y-cy,x-cx)
		xv = msiz/2.0 * math.cos(alf) + cx
		yv = msiz/2.0 * math.sin(alf) + cy
		xh = msiz/2.0 * math.cos(alf+math.pi) + cx
		yh = msiz/2.0 * math.sin(alf+math.pi) + cy
		xl = rad*4.5 * math.cos(alf-math.pi/2.0) + cx
		yl = rad*4.5 * math.sin(alf-math.pi/2.0) + cy
		xr = rad*4.5 * math.cos(alf+math.pi/2.0) + cx
		yr = rad*4.5 * math.sin(alf+math.pi/2.0) + cy

		def balance_label(color):
			lbx = self.size[0]/2.0
			lby = (self.size[1]-msiz)/4.0
			if self.orientation=='horizontal':
				lby = self.size[1]/2.0
				lbx = self.size[0]-(self.size[0]-msiz)/4.0
			rotated_text("{0: 5.2f}\u00b0".format(balance),
					lbx,lby,txtangle,font_size=72,color=color)

		self.canvas.after.clear()
		with self.canvas.after:
			if variante == 0:

				balance_label([0.7,0.7,0.7,1])
				self.center_color(balance)

				if self.ori.orientation() in ["LANDING","FLYING"]:
					#Line(points=[x,y, 2*cx-x, 2*cy-y],width=2.0)
					if balance>0.1:
						Line(points=[xv,yv,xh,yh],width=2.0)
				else:
					Line(points=[xv,yv,xh,yh],width=2.0)

				''
				PushMatrix()
				Translate(x,y)
				Rotate(angle=self.ori.phi,origin=(0,0))
				Scale(msiz/18.0,origin=(0,0))
				self.baloon()
				PopMatrix()

				'''
				PushMatrix()
				Scale(0.5,origin=(x,y))
				Ellipse(pos=(x-rad,y-rad),size=(2.0*rad,2.0*rad))
				Color(0.1, 0.1, 0.1, 1)
				Line(circle=(x,y,rad/1.0-radd),width=0.9)

				exv = 2.0 * 0.9 * (xv - cx) / 9.0 + x
				eyv = 2.0 * 0.9 * (yv - cy) / 9.0 + y
				exh = 2.0 * 0.9 * (xh - cx) / 9.0 + x
				eyh = 2.0 * 0.9 * (yh - cy) / 9.0 + y
				exl = 2.0 * 0.9 * rad*4.5 * math.cos(alf-math.pi/1.5) / 9.0 + x
				eyl = 2.0 * 0.9 * rad*4.5 * math.sin(alf-math.pi/1.5) / 9.0 + y
				exr = 2.0 * 0.9 * rad*4.5 * math.cos(alf+math.pi/1.5) / 9.0 + x
				eyr = 2.0 * 0.9 * rad*4.5 * math.sin(alf+math.pi/1.5) / 9.0 + y
				Line(points=[exv,eyv,exl,eyl],width=0.9)
				Line(points=[exv,eyv,exr,eyr],width=0.9)
				Line(points=[exl,eyl,exr,eyr],width=0.9)
				Line(points=[exv,eyv,exh,eyh],width=0.9)
				PopMatrix()
				'''

			if variante == 1:
				balance_label([0.7,0.7,0.7,1])
				self.center_color(balance)

				if self.ori.orientation() in ["LANDING","FLYING"]:
					x4 = msiz/18.0 * math.cos(alf+math.pi) + cx
					y4 = msiz/18.0 * math.sin(alf+math.pi) + cy
					x2 = rad*4.5 * math.cos(alf-math.pi/2.0) + center[0]
					y2 = rad*4.5 * math.sin(alf-math.pi/2.0) + center[1]
					x1 = rad*4.5 * math.cos(alf+math.pi/2.0) + center[0]
					y1 = rad*4.5 * math.sin(alf+math.pi/2.0) + center[1]
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

				Ellipse(pos=(x-rad/2.0,y-rad/2.0),size=(rad,rad))
				Color(0.1, 0.1, 0.1, 1)
				Line(circle=(x,y,rad/2.0-radd),width=0.9)

			if variante == 2:
				balance_label([0.7,0.7,0.7,1])
				self.center_color(balance)

				if self.ori.orientation() in ["LANDING","FLYING"]:
					xoh = msiz/18.0 * math.cos(alf+math.pi)
					yoh = msiz/18.0 * math.sin(alf+math.pi)
					if abs(balance) > 0.1:
						Line(points=[cx+xoh,cy+yoh,xv,yv],width=2.0)
						#Line(points=[xv,yv,xl,yl],width=2.0)
						#Line(points=[xv,yv,xr,yr],width=2.0)
						Line(bezier=[xv,yv,xl+xoh,yl+yoh,cx+xoh,cy+yoh],width=2.0)
						Line(bezier=[xv,yv,xr+xoh,yr+yoh,cx+xoh,cy+yoh],width=2.0)
						#Line(bezier=[xv,yv,xl,yl,x4,y4],width=2.0)
						#Line(bezier=[xv,yv,xr,yr,x4,y4],width=2.0)
						#Line(points=[cx,cy,xl,yl],width=2.0)
						#Line(points=[cx,cy,xr,yr],width=2.0)
				else:
					if abs(balance) > 0.1:
						Line(points=[cx,cy,xv,yv],width=2.0)
						Line(points=[cx,cy,xh,yh],width=2.0)

				Ellipse(pos=(x-rad/2.0,y-rad/2.0),size=(rad,rad))
				Color(0.1, 0.1, 0.1, 1)
				Line(circle=(x,y,rad/2.0-radd),width=0.9)

			if variante == 3:
				if self.ori.orientation() in ["LANDING","FLYING"]:
					#Line(points=[cx,cy, xv, yv],width=2.0)
					Color(1,1,1,0.1)
					vertices = [xl,yl,0,0,xr,yr,0,0,xv,yv,0,0]
					indices = [0,1,2]
					Mesh(vertices=vertices, indices=indices).mode = 'triangle_fan'

					Color(0.7, 0.7, 0.7, 1)   # hellgrau
					Line(points=[x,cy-msiz/2,x,cy+msiz/2],width=1.0)
					Line(points=[cx-msiz/2,y,cx+msiz/2,y],width=1.0)
					'''
					if x<cx:
						rotated_text("{0: 5.2f}".format(self.ori.pitch()),cx+msiz/4,y,0,anchor=(0,1),font_size=32)
					else:
						rotated_text("{0: 5.2f}".format(self.ori.pitch()),cx-msiz/4,y,0,anchor=(0,1),font_size=32)
					if y<cy:
						rotated_text("{0: 5.2f}".format(self.ori.roll()),x,cy+msiz/4,90,anchor=(0,1),font_size=32)
					else:
						rotated_text("{0: 5.2f}".format(self.ori.roll()),x,cy-msiz/4,90,anchor=(0,1),font_size=32)
					'''
					rotated_text("{0: 5.2f}".format(balance),cx,cy,self.angle-90,anchor=(0,-3.5),font_size=56,color=[0.7, 0.7, 0.7, 1])

				else:
					Color(0.7, 0.7, 0.7, 1)   # hellgrau
					Line(points=[xv,yv,xh,yh],width=2.0)
					if self.ori.orientation() in ['TOP','BOTTOM']:
						Line(points=[x,cy-msiz/2,x,cy+msiz/2],width=1.0)
					else:
						Line(points=[cx-msiz/2,y,cx+msiz/2,y],width=1.0)

					#rotated_text("{0: 5.2f}".format(balance),(cx+xh)/2,(cy+yh)/2,txtangle,anchor=(0,+1),font_size=56,color=[0.7, 0.7, 0.7, 1])
					rotated_text("{0: 5.2f}".format(balance),(cx),(cy),txtangle,anchor=(0,-3.5),font_size=56,color=[0.7, 0.7, 0.7, 1])

				#main_angle = -45.0+self.ori.phi-(self.ori.phi-45) % 90.0

				set_color([0.7, 0.7, 0.7, 1])   # hellgrau
				PushMatrix()
				Translate(x,y)
				#Rotate(angle=45.0+self.ori.phi-(self.ori.phi-45) % 90.0,origin=(0,0))
				Scale(msiz/120.0,origin=(0,0))
				self.baloon(lscale=0.0)
				PopMatrix()

				PushMatrix()
				self.center_color(balance)
				Translate(cx,cy)
				Rotate(angle=self.ori.phi,origin=(0,0))
				Scale(msiz/18.0,origin=(0,0))
				self.baloon()
				PopMatrix()


	# grephic helpers

	def baloon(self,lcolor=[0.1,0.1,0.1,1],lwidth=1.0,lscale=0.9):
		Ellipse(pos=(-1,-1),size=(2,2))
		PushMatrix()
		set_color(lcolor)
		Scale(lscale,origin=(0,0))
		Line(circle=(0,0,1.0),width=lwidth)
		ex = math.cos(math.radians(30))
		Line(points=[1.0,0.0,-0.5,-ex],width=lwidth)
		Line(points=[1.0,0.0,-0.5,ex],width=lwidth)
		Line(points=[-0.5,-ex,-0.5,ex],width=lwidth)
		Line(points=[1.0,0.0,-1.0,0.0],width=lwidth)
		PopMatrix()


	def center_color(self,balance):
		good = 5.0
		set_color_range(
			[0.5,1.0,0.0,0.6],[1.0,0.6,0.0,0.7],math.fabs(balance)/good)
		return

	def on_touch_down(self, touch):
		# calibrieren, nur wenn im Zentrum innerhalb er erste 10 degrees:
		msiz = min(self.size[0],self.size[1])
		center = (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)
		dx = math.fabs(touch.pos[0] - center[0])
		dy = math.fabs(touch.pos[1] - center[1])
		if (msiz/90*10 > math.sqrt(dx*dx+dy*dy)):
			self.calaStore.accept();

		# calibration zurücksetzen vorbereiten.
		self.calaResetEvent =\
			Clock.schedule_once(lambda dt: self.calaStore.reset(),1.5)

		# double tap
		if touch.is_double_tap:
		   #print ('py:',touch.pos[1],'msiz/2',msiz/2)
		   if touch.pos[1] < msiz/2.0:
			   self.variant += 1
			   self.variant = self.variant % 4
		   else:
			   for c in self.children:
				   c.on_touch_down(touch)
		   pass

		# desktop Variante:
		app = Cache.get('LAppCache', 'mainApp')
		if app.sensor_reader is None:
			# wir rechnen x,y,z anhand der touch pos zurück.
			rad = min(self.size[1],self.size[0])/2
			px = (touch.pos[0] - self.size[0]/2) / rad * 45
			py = (touch.pos[1] - self.size[1]/2)  / rad * 45
			theta = math.sqrt(px*px+py*py)
			phi = math.atan2(py,px)
			x,y,z = kart(9.81,phi,math.radians(theta))
			self.ori = LValue(x,y,z)
			self.draw_line()

		return False

	def on_touch_up(self, touch):

		# calibrations reset stoppen, wenn tap zu kurz:
		if (touch.time_end-touch.time_start) < 1.0:
		   Clock.unschedule(self.calaResetEvent)
		return False

#=============================================================================

class LStack:
	def __init__(self):
		self.items = []

	def isEmpty(self):
		return self.items == []

	def push(self, item):
		self.items.append(item)

	def pop(self):
		return self.items.pop()

	def peek(self):
		return self.items[len(self.items) - 1]

	def size(self):
		return len(self.items)

#=============================================================================

class LMainWindow(BoxLayout, LBase):
	def __init__(self, **kw):
		super(LMainWindow, self).__init__(orientation='vertical')
		self.workContainer = BoxLayout(orientation='horizontal')
		self.workArea = None
		self._w = '.'
		self.bmenu = True
		if 'bmenu' in kw:
			self.bmenu = kw['bmenu']
		self.title = "<title>"
		if 'frametitle' in kw:
			self.title = kw['frametitle']

		if (self.bmenu):
			self.add_widget(self.menuArea)
		self.add_widget(self.workContainer)

		self.workStack = LStack()
		self.app = None

	# Menubar:

	def setMenu(self, menu):
		self.menuArea.setMenu(menu)

	def getMenu(self):
		return self.menuArea.getMenu()

	# Toolbar:

	def setTool(self, toolbar, pos=0):
		if (self.toolBar != None):
			self.workContainer.remove_widget(self.toolBar)
		if (toolbar != None):
			self.workContainer.add_widget(toolbar)
		self.toolBar = toolbar

	# Workarea:

	def pushWork(self, widget):
		self.workStack.push(self.workArea)
		self.setWork(widget)

	def popWork(self):
		if self.workStack.size() > 0:
			self.setWork(self.workStack.pop())
		pass

	def setWork(self, widget):
		if (self.workArea != None):
			self.workContainer.remove_widget(self.workArea)
		if (widget != None):
			self.workContainer.add_widget(widget)
		self.workArea = widget

	def getWork(self):
		return self.workArea

	def on_touch_down(self, touch):
		for c in self.children:
			if (c.on_touch_down(touch)): return True
		return False

#=============================================================================

from kivy.cache import Cache
from kivy.utils import platform

class LApp(App):
	def __init__(self, **kw):
		super(LApp, self).__init__()
		self.mainWindow = LMainWindow(**kw)
		logging.info('top = %s' % str(self.mainWindow))
		Cache.register('LAppCache', limit=10)
		Cache.append('LAppCache', 'mainWindow', self.mainWindow, timeout=0)
		Cache.append('LAppCache', 'mainApp', self, timeout=0)

	def _stop_loading_screen(self,dt):
		if platform=='android':
			#os.environ['HOME'] = '/sdcard'
			from android.loadingscreen import hide_loading_screen
			hide_loading_screen()
		else:
			print ('would stop now loading screen hier on android')

	def stop_loading_screen(self):
		Clock.schedule_once(self._stop_loading_screen,0.01);

	def build(self):
		logging.info("LApp: build")
		#self.stop_loading_screen()
		self._stop_loading_screen(5)
		return self.mainWindow

	def on_start(self):
		logging.info("LApp: on_start")

	def on_stop(self):
		logging.info("LApp: on_stop")
		# Achtung wird u.U. 2 mal aufgerufen !!!

	def on_pause(self):
		logging.info("LApp: on_pause")
		# return True: wenn wir wirklich in pause gehen. Dann wird auch
		# resume aufgerufen falls die app wieder aktiviert wird.
		# return False: app wird gestoppt (on_stop wird aufgerufen)
		#return True

	def on_resume(self):
		logging.info("LApp: on_resume")
