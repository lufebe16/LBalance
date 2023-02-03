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
		self.cala_angle = 0.0
		self.cala_cnt = 0

	def reset(self):
		self.cala_angle = 0.0
		self.cala_cnt = 0

	def addValue(self,angle,soll):
		delta = angle-soll
		self.cala_cnt += 1
		self.cala_angle = ((self.cala_cnt-1)*self.cala_angle + delta) / self.cala_cnt

	def getValue(self):
		return self.cala_angle;

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

	def addCalibration(self,rawValue):
		if not self.accept_one: return

		ori = rawValue.orientation()
		if  ori not in self.store:
			self.store[ori] = LCala()
		if ori in ["LANDING","FLYING"]:
			self.store[ori].addValue(rawValue.theta,rawValue.refval)
		else:
			self.store[ori].addValue(rawValue.phi,rawValue.refval)
		print ("LCalaStore: one value accepted")
		self.accept_one = False

	def calibrate(self,rawValue):
		ori = rawValue.orientation()
		if ori not in self.store: return rawValue

		val = self.store[ori].getValue()
		if ori in ["LANDING","FLYING"]:
			return LValue(rawValue.phi,rawValue.theta-val)
		else:
			return LValue(rawValue.phi-val,rawValue.theta)

#=============================================================================

class LValue(object):

	def __init__(self,phi,theta):
		self.phi = phi
		self.theta = theta

		def norm45(angle):
			angle = normAngle(angle)
			if angle < -45: angle = -45
			if angle > 45: angle = 45
			return angle

		self.refval = 0.0
		self.bala = 0.0
		self.ori = "LANDING"
		if (self.theta > 45.0):
			self.ori = "LANDING"
			self.refval = 90.0
			self.bala = norm45(90.0-self.theta)
		elif (self.theta < -45.0):
			self.ori = "FLYING"
			self.refval = -90.0
			self.bala = norm45(-90.0-self.theta)
		elif (self.phi < 135.0 and self.phi > 45.0):
			self.ori = "BOTTOM"
			self.refval = 90.0
			self.bala = norm45(90.0-self.phi)
		elif (self.phi < 45.0 and self.phi > -45.0):
			self.ori = "LEFT"
			self.refval = 0.0
			self.bala = norm45(-self.phi)
		elif (self.phi < -45.0 and self.phi > -135.0):
			self.ori = "TOP"
			self.refval = -90.0
			self.bala = norm45(-90.0-self.phi)
		elif (self.phi > 135.0 or self.phi < -135.0):
			self.ori = "RIGHT"
			self.refval = 180.0
			self.bala = norm45(180.0-self.phi)

	def pitch(self):
		return (90.0-math.fabs(self.theta)) * math.sin(math.radians(self.phi))

	def roll(self):
		return (90.0-math.fabs(self.theta)) * math.cos(math.radians(self.phi))

	def balance(self):
		return self.bala

	def orientation(self):
		return self.ori

	def refv(self):
		return self.refval

#=============================================================================
# Definiert den App Hintergrund.

class LCircleView(Widget):
	def __init__(self,**kw):
		super(LCircleView, self).__init__(**kw)

		self.bind(pos=self.update)
		self.bind(size=self.update)
		self.update_event = None

	def update(self, *args):
		Clock.unschedule(self.update_event)
		self.update_event = Clock.schedule_once(self.update_scheduled, 0.2)

	def update_scheduled(self, *args):
		msiz = min(self.size[0],self.size[1])
		rpos = (self.pos[0]+(self.size[0]-msiz)/2,self.pos[1]+(self.size[1]-msiz)/2)
		center = (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)
		print ('LCircleView',msiz)

		self.canvas.before.clear()
		with self.canvas.before:
			Color(0.7, 0.7, 0.7, 1)   # hellgrau
			#Color(0.4, 0.4, 0.4, 1)   # grau
			#Color(0.9, 0.9, 0.9, 1)   # weiss
			#Color(0.8, 0.9, 0.3, 1)   # gelb
			Ellipse(pos=rpos,size=(msiz,msiz))
			#StencilPush()
			#StencilPop()
			step = (msiz/2.0) / 45
			Color(0.1, 0.1, 0.1, 0.8)
			for i in range(5,45,5):
				Line(circle=(center[0],center[1],i*step),width=1.1)
			Line(circle=(center[0],center[1],45*step),width=1.9)

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

        self.label_phi = LabelButton(text="")
        self.label_theta = LabelButton(text="")
        self.label_balance = LabelButton(text="")
        self.lcontainer = BoxLayout()
        self.lcontainer.add_widget(self.label_phi)
        self.lcontainer.add_widget(self.label_theta)

        self.angle = 0.0
        self.value = 0.0
        self.balance = 0.0
        self.ori = None
        self.valRaw = None
        self.valCal = None
        self.calaStore = LCalaStore()

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

        self.add_widget(self.lcontainer)
        self.add_widget(LCircleView(size_hint=(None,None),width=smin,height=smin))
        self.add_widget(self.label_balance)
        pass

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

    def refresh(self, phi, theta):
        self.value = theta
        self.angle = phi

        # TBD:
        # if calibrated:
        # modify phi and theta:

        self.valRaw = LValue(phi,theta)
        self.calaStore.addCalibration(self.valRaw)

        self.valCal = self.calaStore.calibrate(self.valRaw)
        self.ori = self.valCal

        self.draw_line()

    def draw_line(self):
        x = self.value
        y = self.angle
        msiz = min(self.size[0],self.size[1])
        rad = msiz/9.0
        center = (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)

        if self.ori is not None:
            txtangle = 0.0
            self.balance = self.ori.balance()
            self.label_balance.text = 'balance: '+str(round(self.balance,1))
            if self.ori.orientation()=="LANDING":
                x = self.ori.roll()
                y = self.ori.pitch()
            elif self.ori.orientation()=="FLYING":
                x = self.ori.roll()
                y = self.ori.pitch()
            elif self.ori.orientation()=="TOP":
                txtangle = 180.0
                x = -self.balance
                y = 0
            elif self.ori.orientation()=="BOTTOM":
                x = self.balance
                y = 0
            elif self.ori.orientation()=="LEFT":
                txtangle = -90.0
                y = -self.balance
                x = 0
            elif self.ori.orientation()=="RIGHT":
                txtangle = 90.0
                y = self.balance
                x = 0
            x = x*msiz/2.0/45.0 + center[0]
            y = y*msiz/2.0/45.0 + center[1]

            self.label_balance.update_angle(txtangle)
            self.label_phi.update_angle(txtangle)
            self.label_theta.update_angle(txtangle)

        radd = rad*0.1
        self.canvas.after.clear()
        with self.canvas.after:
            good = 0.3
            if (((math.fabs(self.balance)+good) % 90) < 2.0*good) and self.ori is not None:
              #Color(0.75, 1.0, 0.1, 0.6)    # gelb-grün
              Color(0.5, 1.0, 0.1, 0.6)    # hell-grün
            else:
              Color(1, 0.2, 0.2, 0.7)       # lachs-rot

            #Color(0.5, 1.0, 0.1, 0.6)    # gelb-grün
            Line(points=[center[0],center[1],x,y],width=2.0)
            Line(points=[center[0],center[1],
                center[0]-(x-center[0]),
                center[1]-(y-center[1])],width=2.0)

            Ellipse(pos=(x-rad,y-rad),size=(2.0*rad,2.0*rad))
            Color(0.1, 0.1, 0.1, 1)
            Line(circle=(x,y,rad/1.0-radd),width=0.9)
            Line(circle=(x,y,rad/2.0-radd),width=0.9)
            #Line(circle=(x,y,msiz/2.0),width=0.9)

        self.label_phi.text = 'phi: '+str(round(self.angle,1))
        self.label_theta.text = 'theta: '+str(round(self.value,1))


    def on_touch_down(self, touch):

        print('LWorkWindow: touch_down %s' % str(touch.time_start))
        print('LWorkWindow: touch_down %s' % str(touch.time_end))
        print('LWorkWindow: touch_down on %s' % str(touch.pos))
        print('LWorkWindow: sensor %s,%s' % (str(self.angle),str(self.value)))
        return False

    def on_touch_up(self, touch):
        print('LWorkWindow: touch_up %s' % str(touch.time_start))
        print('LWorkWindow: touch_up %s' % str(touch.time_end))
        if (touch.time_end-touch.time_start) > 2:
            print ("long tap")
            self.calaStore.reset();
        else:
            self.calaStore.accept();
            print ('normal tap')

        app = Cache.get('LAppCache', 'mainApp')
        if app.sensor_reader is not None:
            pass

            # Idee: wenn ins zentrum getippt wird: kalibartionswert
            # hinzufügen. Bei long tap wieder zurcksetzen.
        else:
            self.angle = touch.pos[1]
            self.value = touch.pos[0]
            self.draw_line()
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
