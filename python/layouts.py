
#=============================================================================

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty

#=============================================================================

from storage import ConfigDir

from staticview \
	import LCircleViewSimple,LCircleViewFine, \
		LCircleViewFineWithScale,LCircleViewAV,LCircleViewAValt, \
		LCircleViewBA,LCircleViewMini,LCircleViewBubble

from dynamicview \
	import LAngleViewMini,LAngleViewFull,LAngleViewAValt, \
		LAngleViewFull2,LAngleViewAV,LAngleViewBA,LAngleViewBubble, \
		LAngleViewKugel, LAngleViewKugelP, LAngleViewCube, LAngleViewText

import json

class LLayout(object):
	def __init__(self, dv, bg, sc):
		self.layout = {
			"foreground": dv,
			"background": bg,
			"statuscolor": sc,
			"cache": None
			}

	def background(self):
		return self.layout["background"]()

	def foreground(self):
		return self.layout["foreground"]()

	def statuscolor(self):
		return self.layout["statuscolor"]

	def cache(self):
		return self.layout["cache"]

	def set_cache(self,widget):
		self.layout["cache"] = widget

from kivy.uix.gridlayout import GridLayout

class LLayouts(EventDispatcher):
	selected = NumericProperty(0)

	def __init__(self,**kw):
		super(LLayouts,self).__init__(**kw)
		self.layouts = []
		self.layouts.append(LLayout(
			LAngleViewMini,LCircleViewMini,[0.0, 0.0, 0.0, 0.0]))
		self.layouts.append(LLayout(
			LAngleViewFull,LCircleViewFine,[0.0, 0.4, 0.1, 1]))
		self.layouts.append(LLayout(
			LAngleViewFull2,LCircleViewFineWithScale,[0.2, 0.05, 0.3, 1]))
		self.layouts.append(LLayout(
			LAngleViewAValt,LCircleViewAValt,[0.3, 0.55, 0.45, 1]))
		self.layouts.append(LLayout(
			LAngleViewBA,LCircleViewBA,[0.0, 0.0, 0.0, 0.0]))
		self.layouts.append(LLayout(
			LAngleViewBubble,LCircleViewBubble,[0.0, 0.0, 0.0, 0.0]))
		self.layouts.append(LLayout(
			LAngleViewKugelP,LCircleViewMini,[0.2, 0.2, 0.2, 1.0]))
		self.layouts.append(LLayout(
			LAngleViewCube,LCircleViewMini,[0.2, 0.2, 0.2, 1.0]))
		''
		self.layouts.append(LLayout(
			LAngleViewText,LCircleViewMini,[0.2, 0.2, 0.2, 1.0]))
		''
		#self.layouts.append(LLayout(
		#	LAngleViewAV,LCircleViewAV,[0.8, 0.0, 0.0, 1.0]))

		self.read()

	def get_widget(self,index):
		layout = self.layout(index)
		angle_view = layout.cache()
		if angle_view is None:
			angle_view = layout.foreground()
			angle_view.layout_selector = lambda: self.select(index)
			circle_view = layout.background()
			angle_view.set_background(circle_view)
			layout.set_cache(angle_view)
		return angle_view

	def next(self):
		self.selected = (self.selected+1) % len(self.layouts)
		self.save()
		return self.selected

	def current(self):
		return self.selected

	def select(self,index):
		print('select ...',index)
		self.selected = index % len(self.layouts)
		self.save()

	def count(self):
		return len(self.layouts)

	def layout(self,index=None):
		if index is None:
			return self.layouts[self.selected]
		return self.layouts[index % len(self.layouts)]

	def get_menu(self):
		return self.selected == -1

	def set_menu(self):
			self.selected = -1

	def save(self):
		try:
			fp = open(ConfigDir.get()+"/ww_layout.json",'w')
			json.dump(self.selected,fp)
		except:
			pass

	def read(self):
		try:
			fp = open(ConfigDir.get()+"/ww_layout.json",'r')
			if fp:
				sel = json.load(fp)
				if sel>=self.count(): sel = 0
				if sel<0: sel = 0
				self.selected = sel
		except:
			print ('Configdir: read error in ',ConfigDir.get())
			pass

Layouts = LLayouts()

#=============================================================================
