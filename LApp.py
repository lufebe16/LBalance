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

import math

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
		valXY = math.sqrt(valX*valX+valY*valY)
		self.phi = math.degrees(math.atan2(valY,valX));
		self.theta = 90.0
		if valXY != 0.0:
			self.theta = math.degrees(math.atan(valZ/valXY))
		self.g = math.sqrt(valX*valX+valY*valY+valZ*valZ)

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
	def __init__(self,**kw):
		super(LCircleView, self).__init__(**kw)

		self.bind(pos=self.update)
		self.bind(size=self.update)
		self.update_event = None
		self.radius = None
		self.variante = 2

	def update(self, *args):
		Clock.unschedule(self.update_event)
		self.update_event = Clock.schedule_once(self.update_scheduled, 0.2)

	def update_scheduled(self, *args):
		msiz = min(self.size[0],self.size[1])
		self.radius = msiz/2.0
		rpos = (self.pos[0]+(self.size[0]-msiz)/2,self.pos[1]+(self.size[1]-msiz)/2)
		center = (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)
		#print ('LCircleView',msiz)

		self.canvas.before.clear()
		with self.canvas.before:

			if self.variante == 0:
				Color(0.7, 0.7, 0.7, 1)   # hellgrau
				Ellipse(pos=rpos,size=(msiz,msiz))
				#StencilPush()
				#StencilUse()
				#StencilUnUse()
				#StencilPop()
				step = (msiz/2.0) / 45
				Color(0.1, 0.1, 0.1, 0.8)
				for i in range(5,45,5):
					Line(circle=(center[0],center[1],i*step),width=1.1)
				Line(circle=(center[0],center[1],45*step),width=1.9)

			if self.variante == 1:
				Color(0.5, 0.4, 1.0, 1)   # violett
				step = (msiz/2.0) / 45
				for i in range(5,45,10):
					Line(circle=(center[0],center[1],i*step),width=0.5)
				Line(circle=(center[0],center[1],45*step),width=0.7)

			if self.variante == 2:
				Color(0.7, 0.7, 0.7, 1)   # hellgrau
				step = (msiz/2.0) / 45
				for i in range(5,45,5):
					Line(circle=(center[0],center[1],i*step),width=0.5)
				Line(circle=(center[0],center[1],45*step),width=0.7)

			if self.variante == 3:
				self.radius = 0.9*msiz/2
				step = self.radius / 45

				Color(0.7, 0.7, 0.7, 1)   # hellgrau
				#step = (msiz/2.0) / 45
				for i in range(5,45,5):
					Line(circle=(center[0],center[1],i*step),width=0.5)
				Line(circle=(center[0],center[1],45*step),width=0.7)

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

	def get_radius(self):
		return self.radius

	def on_touch_down(self, touch):
		# double tap
		if touch.is_double_tap:
			self.variante += 1
			self.variante = self.variante % 4
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
        self.label_phi = LabelButton(text="",font_size=32)
        self.label_cal = LabelButton(text="",font_size=32)
        self.label_theta = LabelButton(text="",font_size=32)
        self.label_balance = LabelButton(text="",font_size=72)
        self.lcontainer = BoxLayout()
        self.lcontainer.add_widget(self.label_phi)
        self.lcontainer.add_widget(self.label_cal)
        self.lcontainer.add_widget(self.label_theta)
        self.circle_view = LCircleView()

        self.angle = 0.0
        self.value = 0.0
        self.ori = None
        self.calaStore = LCalaStore()
        self.calaResetEvent = None

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
        self.add_widget(self.label_balance)

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

        #msiz = self.circle_view.get_radius()
        #if msiz is None: return
        #msiz *= 2.0

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

        self.label_balance.text = "{0: 5.2f}\u00b0".format(balance)
        self.label_balance.update_angle(txtangle)

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

        self.label_phi.text = "phi: {0: 5.1f}\u00b0".format(self.angle)
        self.label_theta.text = "theta: {0: 5.1f}\u00b0".format(self.value)

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

        self.canvas.after.clear()
        with self.canvas.after:
          if variante == 0:
            good = 3.0
            gness = ((math.fabs(balance)+good) % 90)
            r = 0.5 + math.fabs(balance) * (1.0-0.5)/good
            g = 1.0 + math.fabs(balance) * (0.6-1.0)/good
            b = 0.0
            a = 0.6 + math.fabs(balance) * (0.7-0.6)/good
            #print(r,g,a)
            if (gness < 2.0*good):
              #Color(0.5, 1.0, 0.0, 0.6)    # hell-grün
              Color(r, g, b, a)    # hell-grün
            else:
              Color(1.0, 0.6, 0.0, 0.7)    # gelb-orange

            if self.ori.orientation() in ["LANDING","FLYING"]:
                Line(points=[x,y, 2*cx-x, 2*cy-y],width=2.0)
            else:
                Line(points=[xv,yv,xh,yh],width=2.0)

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

          if variante == 1:
            good = 3.0
            gness = ((math.fabs(balance)+good) % 90)
            r = 0.5 + math.fabs(balance) * (1.0-0.5)/good
            g = 1.0 + math.fabs(balance) * (0.6-1.0)/good
            b = 0.0
            a = 0.6 + math.fabs(balance) * (0.7-0.6)/good
            if (gness < 2.0*good):
              Color(r, g, b, a)
            else:
              Color(1.0, 0.6, 0.0, 0.7)    # gelb-orange

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
            good = 3.0
            gness = ((math.fabs(balance)+good) % 90)
            r = 0.5 + math.fabs(balance) * (1.0-0.5)/good
            g = 1.0 + math.fabs(balance) * (0.6-1.0)/good
            b = 0.0
            a = 0.6 + math.fabs(balance) * (0.7-0.6)/good
            print(r,g,a)
            if (gness < 2.0*good):
              Color(r, g, b, a)
            else:
              Color(1.0, 0.6, 0.0, 0.7)    # gelb-orange

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
            good = 3.0
            gness = ((math.fabs(balance)+good) % 90)
            r = 0.5 + math.fabs(balance) * (1.0-0.5)/good
            g = 1.0 + math.fabs(balance) * (0.6-1.0)/good
            b = 0.0
            a = 0.6 + math.fabs(balance) * (0.7-0.6)/good
            #print(r,g,a)
            if (gness < 2.0*good):
              #Color(0.5, 1.0, 0.0, 0.6)    # hell-grün
              Color(r, g, b, a)    # hell-grün
            else:
              Color(1.0, 0.6, 0.0, 0.7)    # gelb-orange

            if self.ori.orientation() in ["LANDING","FLYING"]:
                Line(points=[x,y, 2*cx-x, 2*cy-y],width=2.0)
            else:
                Line(points=[xv,yv,xh,yh],width=2.0)

            #Ellipse(pos=(x-rad,y-rad),size=(2.0*rad,2.0*rad))
            Color(0.1, 0.1, 0.1, 1)
            Line(circle=(x,y,rad/1.0-radd),width=0.9)

            # dreieck im Zentrum
            '''
            Color(0.1, 0.1, 0.1, 1)
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
            '''

            self.pitch_und_roll_linien(cx,cy,x,y,msiz)

            self.rotated_text("{0: 5.2f}".format(self.ori.pitch()),cx,y,0)
            self.rotated_text("{0: 5.2f}".format(self.ori.roll()),x,cy,90)


    def rotated_text(self,text,x,y,angle=0,font_size=16):
        l = self.label_hidden
        l.text = text
        l.texture_update()
        t = l.texture
        PushMatrix()
        Rotate(angle=angle,origin=(x,y))
        Rectangle(texture=t,pos=(x-t.size[0]/2,y-t.size[1]/2),size=t.size)
        PopMatrix()

    def pitch_und_roll_linien(self,cx,cy,x,y,msiz):
        Color(0.7, 0.7, 0.7, 1)   # hellgrau
        Line(points=[cx-msiz/2,y,cx+msiz/2,y],width=1.0)
        Line(points=[x,cy-msiz/2,x,cy+msiz/2],width=1.0)

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
           print ('py:',touch.pos[1],'msiz/2',msiz/2)
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
            phi = math.degrees(math.atan2(py,px))
            self.angle = phi
            self.value = 90-theta
            g = 9.81
            z = g * math.cos(math.radians(theta))
            r = math.sqrt(g*g - z*z)
            x = r * math.cos(math.radians(phi))
            y = r * math.sin(math.radians(phi))
            #print ('z',z)
            #print ('x',x)
            #print ('y',y)
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
