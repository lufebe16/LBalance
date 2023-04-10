#!/usr/bin/python

# -*- mode: python; coding: utf-8; -*-

import os
import math
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
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty

# =============================================================================
# übersetzung.

import gettext
t = gettext.translation('base', 'locales', fallback=True)
_ = t.gettext

# =============================================================================
# helpers.

from storage import ConfigDir
from koords import kart,polar,polarDeg,normAngle,LValue
from graphics import rotated_text, triangle, LFont, set_color
from calibration import CalaStore
from staticview import LCircleView
from dynamicview import LAngleView
from layouts import Layouts

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
		print ('on_press')
		return False

	def on_release(self):
		#self.source = 'atlas://data/images/defaulttheme/checkbox_off'
		print ('on_release')
		return False

#=============================================================================

class CalaButton(LabelButton):
	def __init__(self, **kw):
		super(CalaButton, self).__init__(**kw)
		CalaStore.bind(cala_state=self.cala_update)
		#self.color = [0,0,0,1]
		#self.color = [0.8,0.8,0.8,1]

	def cala_update(self,obj,val):
		if isinstance(val,LValue):
			cal = CalaStore.numCalibrated(val)
			if cal>0:
				self.text = _('Calibrated ({0:}x)').format(cal)
			else:
				self.text = _('Calibration')

	def on_press(self):
		print ('on_press cala')
		CalaStore.accept();
		return False

	def on_release(self):
		print ('on_release cala')
		return False

	def on_touch_down(self, touch):
		super(CalaButton,self).on_touch_down(touch)
		if self.collide_point(touch.x,touch.y):
			print ('on_touch_down cala')
		return False

	def on_touch_up(self, touch):
		super(CalaButton,self).on_touch_up(touch)
		if self.collide_point(touch.x,touch.y):
			print ('on_touch_up cala')
			if (touch.time_end-touch.time_start) > 0.5:
				CalaStore.reset()
		return False

#=============================================================================

class LayoutButton(LabelButton):
	def __init__(self, **kw):
		super(LayoutButton, self).__init__(**kw)
		self.color_save = None

	def on_press(self):
		#self.source = 'atlas://data/images/defaulttheme/checkbox_on'
		print ('on_press layout')
		#self.color_save = self.color
		#self.color = [1,0,0,1]
		#Layouts.next()
		return False

	def on_release(self):
		#self.source = 'atlas://data/images/defaulttheme/checkbox_off'
		print ('on_release layout')
		#Layouts.next()
		return False

	def on_touch_down(self, touch):
		if self.collide_point(touch.x,touch.y):
			print ('on_touch_down Layout')
		#super().on_touch_down(touch)
		return False

	def on_touch_up(self, touch):
		if self.collide_point(touch.x,touch.y):
			print ('on_touch_up Layout')
			if (touch.time_end-touch.time_start) > 0.5:
				print ('on_touch_up Layout - long press')
				Layouts.set_menu()
				return True
			else:
				Layouts.next()
		#super().on_touch_up(touch)
		return False

#=============================================================================

class LStatusLine(BoxLayout,LBase):
	def __init__(self,**kw):
		super(LStatusLine, self).__init__(**kw)
		self.background_color = [0.0, 0.4, 0.1, 1]
		with self.canvas.before:
			set_color(self.background_color)
			Rectangle(pos=self.pos, size=self.size)
		self.bind(pos=self.update_rect)
		self.bind(size=self.update_rect)

		self.g = LabelButton(text="g",halign="center",valign="bottom")
		self.phi = LabelButton(text="phi",halign="center")
		self.theta = LabelButton(text="theta",halign="center")
		self.xVal = LabelButton(text="xVal",halign="center")
		self.yVal = LabelButton(text="yVal",halign="center")
		self.zVal = LabelButton(text="zVal",halign="center")

		LFont.bind_widget(self.g, LFont.small)
		LFont.bind_widget(self.phi, LFont.small)
		LFont.bind_widget(self.theta, LFont.small)
		LFont.bind_widget(self.xVal, LFont.small)
		LFont.bind_widget(self.yVal, LFont.small)
		LFont.bind_widget(self.zVal, LFont.small)

		self.add_widget(self.g)
		self.add_widget(self.phi)
		self.add_widget(self.theta)
		self.add_widget(self.xVal)
		self.add_widget(self.yVal)
		self.add_widget(self.zVal)

		Layouts.bind(selected=self.update_rect)

	def update_rect(self,*args):
		self.background_color = Layouts.layout().statuscolor()
		self.canvas.before.clear()
		with self.canvas.before:
			set_color(self.background_color)
			Rectangle(pos=self.pos, size=self.size)

	def set_ori(self,angle):
		self.g.update_angle(angle)
		self.phi.update_angle(angle)
		self.theta.update_angle(angle)
		self.xVal.update_angle(angle)
		self.yVal.update_angle(angle)
		self.zVal.update_angle(angle)

	def update(self,g,phi,theta,x,y,z):
		self.g.text="g\n{0: 5.2f}".format(g)
		self.phi.text="phi\n{0: 5.2f}\u00b0".format(phi)
		self.theta.text="theta\n{0: 5.2f}\u00b0".format(theta)
		self.xVal.text="x\n{0: 5.2f}".format(x)
		self.yVal.text="y\n{0: 5.2f}".format(y)
		self.zVal.text="z\n{0: 5.2f}".format(z)

#=============================================================================

class LHeaderLine(BoxLayout,LBase):
	def __init__(self,**kw):
		super(LHeaderLine, self).__init__(**kw)
		self.background_color = [0.0, 0.4, 0.05, 1]
		with self.canvas.before:
			#Color(0, 0.00, 0.1, 1)   # schwarz mit blau stich
			#Color(0.15, 0.00, 0.3, 1)   # schwarz mit violett stich
			set_color(self.background_color)   # blaugrün
			Rectangle(pos=self.pos, size=self.size)
		self.bind(pos=self.update_rect)
		self.bind(size=self.update_rect)

		self.title = LabelButton(text="LBalance")
		self.cala = CalaButton(text=_("Calibrate"),halign="center")
		self.layout = LayoutButton(text=_("Layout"))

		LFont.bind_widget(self.title, LFont.small)
		LFont.bind_widget(self.cala, LFont.small)
		LFont.bind_widget(self.layout, LFont.small)

		self.add_widget(self.title)
		self.add_widget(self.cala)
		self.add_widget(self.layout)
		Layouts.bind(selected=self.update_rect)

	def update_rect(self,*args):
		self.background_color = Layouts.layout().statuscolor()
		self.canvas.before.clear()
		with self.canvas.before:
			set_color(self.background_color)
			Rectangle(pos=self.pos, size=self.size)

	def set_ori(self,angle):
		self.title.update_angle(angle)
		self.cala.update_angle(angle)
		self.layout.update_angle(angle)

#=============================================================================
# Versuch einer einfachen bias korrektur.
# -> funktioniert nicht zufriedenstellend.
# (man müsste auch noch die winkel berücksichtigen. Sind die Achsen
# eventuell nicht genau orthogonal?) -> der grund der esten variante ist
# dass hir max und min keine gute basis ist: wir messen so den tiefsten
# und den höchsten wert + max. streubereich!
# Variante 2 versucht von den reinen achsen den durchschnittlichen
# minimal- und maximalwert zu ermitteln. Das braucht aber eine
# sehr lange zeit zum einmessen, d.h. man muss lange mit dem Gerät
# herumturnen. Dann aber werden recht gute Werte erreicht. Ist für die
# Praxis aber ungeeignet.
from smoother import Smoother

class LSensorCalibration(object):

	class summer(object):
		def __init__(self,name):
			self.name = name
			self.val = 0.0
			self.smooth = Smoother(200.0)
			self.setup = True
			# das gibt mit einmaligem updateTime unten genau 200
			# schritte bis zum halben verfall.

		def add(self,val):
			if self.val == 0.0:
				self.smooth.updateTime(0)
			elif self.setup:
				self.smooth.updateTime(1)
				self.setup = False
			self.val = self.smooth.updateValue(self.val,val)

		def average(self):
			print (self.name, self.val)
			return self.val

	def __init__(self):
		self.max = [0.0,0.0,0.0]
		self.min = [0.0,0.0,0.0]
		self.maxPhi = [0.0,0.0,0.0]
		self.minPhi = [0.0,0.0,0.0]
		self.maxTheta = [0.0,0.0,0.0]
		self.minTheta = [0.0,0.0,0.0]
		self.refOri = { "landing": self.summer("landing"),
										"flying": self.summer("flying"),
										"bottom": self.summer("bottom"),
										"top": self.summer("top"),
										"left": self.summer("left"),
										"right": self.summer("right")
									}

	def handleSensorCalibration2(self,vals):
		x,y,z = vals[0],vals[1],vals[2]
		rxyz = math.sqrt(x*x + y*y + z*z)
		# nur wenn wir in der nähe der Achse sind wird aufgezeichnet.
		if math.fabs(z) > 0.999 * rxyz:
			if z > 0.0:
				self.refOri["landing"].add(z)
			else:
				self.refOri["flying"].add(z)
		if math.fabs(y) > 0.999 * rxyz:
			if y > 0.0:
				self.refOri["bottom"].add(y)
			else:
				self.refOri["top"].add(y)
		if math.fabs(x) > 0.999 * rxyz:
			if x > 0.0:
				self.refOri["left"].add(x)
			else:
				self.refOri["right"].add(x)


	def handleSensorCalibration(self,vals):
		lv = LValue(vals[0],vals[1],vals[2])
		for i in range(0,3):
			if self.max[i] <= vals[i]:
				self.max[i] = vals[i]
				self.maxPhi[i] = lv.phi
				self.maxTheta[i] = lv.theta
			if self.min[i] >= vals[i]:
				self.min[i] = vals[i]
				self.minPhi[i] = lv.phi
				self.minTheta[i] = lv.theta

			print('sensor max[{0:}]: {1: 5.2f},{2: 5.2f},{3: 5.2f}'.format(i,self.max[i],self.maxPhi[i],self.maxTheta[i]))
			print('sensor min[{0:}]: {1: 5.2f},{2: 5.2f},{3: 5.2f}'.format(i,self.min[i],self.minPhi[i],self.minTheta[i]))

	def corr(self,vals):

		print ("corr")
		self.max[2] = self.refOri["landing"].average()
		self.min[2] = self.refOri["flying"].average()
		self.max[1] = self.refOri["bottom"].average()
		self.min[1] = self.refOri["top"].average()
		self.max[0] = self.refOri["left"].average()
		self.min[0] = self.refOri["right"].average()

		cVals = vals
		for i in range(0,3):
			if self.max[i] == 0: continue
			if self.min[i] == 0: continue
			bias = (self.max[i]+self.min[i])/2.0
			gain = (self.max[i]-self.min[i])/2.0/9.81
			if gain == 0.0: continue
			cVals[i] = (vals[i]-bias)/gain

			print('sensor[{0:}]: {1: 5.2f},{2: 5.2f}'.format(i,bias,gain))
			print('sensor[{0:}]: {1: 5.2f} -> {2: 5.2f}'.format(i,vals[i],cVals[i]))
		return cVals

SensorCalibration = LSensorCalibration()

#=============================================================================

import random

class LWorkWindow(BoxLayout):
	last_value = ObjectProperty()

	def __init__(self,**kw):
		super(LWorkWindow, self).__init__(**kw)

		with self.canvas.before:
			Color(0, 0.00, 0.1, 1)   # schwarz mit blau stich
			Color(0.15, 0.00, 0.3, 1)   # schwarz mit violett stich
			Color(0.15, 0.00, 0.3, 0.0)   # schwrz transparent.
			self.rect = Rectangle(pos=self.pos, size=self.size)

		self.bind(pos=self.update)
		self.bind(size=self.update)
		self.update_event = None

		self.statusLine = LStatusLine()
		self.headerLine = LHeaderLine()

		# statische und variable views (background/foreground).
		self.angle_view = None
		Layouts.bind(selected=self.update)

		self.ori = None
		self.calaResetEvent = None
		self.stack_layout = None

		# object property init
		self.last_value = None

		#print(Window.render_context)
		#print(Window.render_context['projection_mat'])

	def update(self, *args):
		Clock.unschedule(self.update_event)
		self.update_event = Clock.schedule_once(self.update_scheduled, 0.2)

	def update_scheduled(self, *args):
		self.rect.pos = self.pos
		self.rect.size = self.size

		if self.stack_layout is not None:
			self.stack_layout.clear_widgets()
			self.stack_layout = None

		self.clear_widgets()
		if self.size[0]>=self.size[1]:
			smin = self.size[1]
			hswh = self.size[0]/15
			self.orientation='horizontal'
			self.headerLine.orientation="vertical"
			self.headerLine.size_hint=(None,1)
			self.headerLine.width=hswh
			self.headerLine.set_ori(90)
			self.statusLine.orientation="vertical"
			self.statusLine.size_hint=(None,1)
			self.statusLine.width=hswh
			self.statusLine.set_ori(90)
		else:
			smin = self.size[0]
			hswh = self.size[1]/15
			self.orientation='vertical'
			self.headerLine.orientation="horizontal"
			self.headerLine.size_hint=(1,None)
			self.headerLine.height=hswh
			self.headerLine.set_ori(0)
			self.statusLine.orientation="horizontal"
			self.statusLine.size_hint=(1,None)
			self.statusLine.height=hswh
			self.statusLine.set_ori(0)

		LFont.set_screen_size(smin)
		self.add_widget(self.headerLine)

		menu = Layouts.get_menu()
		if menu:
			self.stack_layout = StackLayout()
			self.angle_view = self.stack_layout
			self.add_widget(self.angle_view)
			for i in range(0,Layouts.count()):
				w = Layouts.get_widget(i)
				w.size_hint=(0.33,0.33)
				self.angle_view.add_widget(w)
		else:
			self.angle_view = Layouts.get_widget(Layouts.current())
			self.angle_view.size_hint=(1.0,1.0)
			self.add_widget(self.angle_view)

		self.add_widget(self.statusLine)

	def refresh(self, valX, valY, valZ):

		#SensorCalibration.handleSensorCalibration([valX,valY,valZ])
		#SensorCalibration.handleSensorCalibration2([valX,valY,valZ])
		#vals = SensorCalibration.corr([valX,valY,valZ])
		#rv = LValue(vals[0],vals[1],vals[2])

		rv = LValue(valX,valY,valZ)
		rc = CalaStore.handleCalibration(rv)
		self.statusLine.update(rc.g,rc.phi,rc.theta,rc.valX,rc.valY,rc.valZ)

		if rc is None: return
		if self.angle_view is None: return
		#print('angleview: ',self.angle_view)

		if self.last_value is not None:
			if math.fabs(self.last_value.phi-rc.phi) < 0.005: return
			if math.fabs(self.last_value.theta-rc.theta) < 0.005: return

		ori = rc.orientation()
		if ori in ['LANDING','FLYING']:
			self.headerLine.title.text = _('Flat')
		elif ori in ['TOP']:
			self.headerLine.title.text = _('Down')
		elif ori in ['BOTTOM']:
			self.headerLine.title.text = _('Up')
		elif ori in ['LEFT']:
			self.headerLine.title.text = _('Left')
		elif ori in ['RIGHT']:
			self.headerLine.title.text = _('Right')

		# trigger update on registered clients (angle_views):
		self.last_value = rc
		#self.angle_view.present(rc)

	def on_touch_down(self, touch):

		#print ('LApp: on_touch_down')

		# desktop Variante:
		app = Cache.get('LAppCache', 'mainApp')
		if app.sensor_reader is None:
			# wir rechnen x,y,z anhand der touch pos zurück.

			# nur double tap weitergeben.
			if touch.is_double_tap:
				for c in self.children:
					c.on_touch_down(touch)

			try:
				rad = self.angle_view.bckgnd.get_tacho_radius()
				cent = self.angle_view.bckgnd.get_tacho_center()
			except:
				rad = self.size[0]/3.0
				if rad>self.size[1]/3.0: rad = self.size[1]/3.0
				cent = (self.size[0]/2.0,self.size[1]/2.0)

			if rad>0.0:
				px = (touch.pos[0] - cent[0]) / rad * 45
				py = (touch.pos[1] - cent[1])  / rad * 45
				theta = math.sqrt(px*px+py*py)
				phi = math.atan2(py,px)

				x,y,z = kart(9.81,phi,math.radians(theta))
				self.refresh(x,y,z)

		# Android variante.
		else:
			for c in self.children:
				if c.on_touch_down(touch): return

		return False

	def on_touch_up(self, touch):
		for c in self.children:
			if c.on_touch_up(touch): return
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
import json

class LApp(App):
	def __init__(self, **kw):
		super(LApp, self).__init__()
		self.mainWindow = LMainWindow(**kw)
		logging.info('top = %s' % str(self.mainWindow))
		Cache.register('LAppCache', limit=10)
		Cache.append('LAppCache', 'mainWindow', self.mainWindow, timeout=0)
		Cache.append('LAppCache', 'mainApp', self, timeout=0)

		if not platform=='android':
			Window.bind(size=self.saveSize)
			self.restoreSize()

	def saveSize(self,*args):
		try:
			fp = open(ConfigDir.get()+"/ww_window.json",'w')
			json.dump(Window.size,fp)
		except:
			pass

	def restoreSize(self):
		try:
			fp = open(ConfigDir.get()+"/ww_window.json",'r')
			if (fp):
				size = json.load(fp)
				Window.size = size
		except:
			pass

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
