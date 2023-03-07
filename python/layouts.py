
#=============================================================================

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty

#=============================================================================

from storage import ConfigDir

from staticview \
	import LCircleViewSimple,LCircleViewFine, \
		LCircleViewFineWithScale,LCircleViewAV, \
		LCircleViewBA,LCircleViewMini,LCircleViewBubble

from dynamicview \
	import LAngleViewMini,LAngleViewFull, \
		LAngleViewFull2,LAngleViewAV,LAngleViewBA,LAngleViewBubble

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
			LAngleViewMini,LCircleViewMini,[0.0, 0.0, 0.0, 0.0]))
		self.layouts.append(LLayout(
			LAngleViewFull,LCircleViewFine,[0.0, 0.4, 0.1, 1]))
		self.layouts.append(LLayout(
			LAngleViewFull2,LCircleViewFineWithScale,[0.2, 0.05, 0.3, 1]))
		self.layouts.append(LLayout(
			LAngleViewAV,LCircleViewAV,[0.9, 0.3, 0.1, 1]))
		#self.layouts.append(LLayout(
		#	LAngleViewAV,LCircleViewAV,[0.0, 0.55, 0.15, 1]))
		self.layouts.append(LLayout(
			LAngleViewBA,LCircleViewBA,[0.0, 0.0, 0.0, 0.0]))
		self.layouts.append(LLayout(
			LAngleViewBubble,LCircleViewBubble,[0.0, 0.0, 0.0, 0.0]))
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
