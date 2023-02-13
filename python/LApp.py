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
# helpers.

from koords import kart,polar,polarDeg,normAngle,LValue

# =============================================================================
# graphic helpers

from graphics import rotated_text, set_color, set_color_range, baloon, triangle

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

from calibration import LCalaStore

#=============================================================================
# Definiert den App Hintergrund.

from staticview import LCircleView, StaticViews

#=============================================================================
# Definiert den App Vordergrund

from dynamicview import LAngleView, DynamicViews

#=============================================================================

class LWorkWindow(BoxLayout):
	def __init__(self,**kw):
		super(LWorkWindow, self).__init__(**kw)

		with self.canvas.before:
			Color(0, 0.00, 0.1, 1)   # schwarz mit blau stich
			#Color(0.15, 0.00, 0.3, 1)   # schwarz mit violett stich
			self.rect = Rectangle(pos=self.pos, size=self.size)

		self.bind(pos=self.update)
		self.bind(size=self.update)
		self.update_event = None

		# platzhalter für Status und Menüzeile (TBD)
		self.label_cal = LabelButton(text="LBalance",font_size=32)
		self.lcontainer = BoxLayout()

		# statische und variable views (background/foreground).
		self.circle_view = None
		self.angle_view = None
		self.static_views = StaticViews()
		self.dynamic_views = DynamicViews()

		# Kalibrierung
		self.ori = None
		self.calaStore = LCalaStore()
		self.calaResetEvent = None
		self.val_ori = "LANDING"

		# Variantesteurerung (vorläufig)
		self.variant = 3
		self.static_variant = 1

	def update(self, *args):
		Clock.unschedule(self.update_event)
		self.update_event = Clock.schedule_once(self.update_scheduled, 0.2)

	def update_scheduled(self, *args):
		self.rect.pos = self.pos
		self.rect.size = self.size

		self.clear_widgets()
		if self.size[0]>=self.size[1]:
			self.orientation='horizontal'
			self.lcontainer.orientation="vertical"
			self.lcontainer.size_hint=(0.1,1)
			self.lcontainer.clear_widgets()
			self.lcontainer.add_widget(self.label_cal)
			smin = self.size[1]
		else:
			self.orientation='vertical'
			self.lcontainer.orientation="horizontal"
			self.lcontainer.size_hint=(1,0.1)
			self.lcontainer.clear_widgets()
			self.lcontainer.add_widget(self.label_cal)
			smin = self.size[0]

		self.circle_view =  self.static_views.view(self.static_variant)
		self.angle_view = self.dynamic_views.view(self.variant)

		self.add_widget(self.lcontainer)
		self.add_widget(self.angle_view)
		self.angle_view.set_background(self.circle_view)

	def refresh(self, valX, valY, valZ):
		rv = LValue(valX,valY,valZ)
		rc = self.calaStore.handleCalibration(rv)
		self.ori = rc

		#cal = self.calaStore.isCalibrated(self.ori)
		#if cal is not None:
		#    self.label_cal.text = 'corr: '+cal
		#else:
		#    self.label_cal.text = ''

		cal = self.calaStore.numCalibrated(self.ori)
		if cal > 0:
			self.label_cal.text = str(cal)+' x calibrated'
		else:
			self.label_cal.text = 'LBalance'

		self.draw_line()
		#self.angle_view.draw_line(rc)

	def draw_line(self):
		if self.ori is None: return
		if self.circle_view is None: return
		if self.circle_view.get_radius() is None: return

		if self.val_ori != self.ori.orientation():
			self.val_ori = self.ori.orientation()
			self.circle_view.val_ori = self.val_ori

		self.angle_view.present(self.ori)
		return


	def on_touch_down(self, touch):
		# calibrieren, nur wenn im Zentrum innerhalb er erste 10 degrees:
		msiz = min(self.size[0],self.size[1])
		center = self.circle_view.get_circle()
		if center is not None:
			#center = (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)
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
				self.variant = self.variant % self.dynamic_views.count()
				self.update()
			else:
				self.static_variant += 1
				self.static_variant = self.static_variant % self.static_views.count()
				self.update()
				#for c in self.children:
				#  c.on_touch_down(touch)

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
