

import math
from colorsys import hsv_to_rgb, rgb_to_hsv

from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.graphics import *
from kivy.graphics.tesselator import Tesselator
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

# =============================================================================
# graphic helpers

class RotatedText(object):
	def __init__(self,**kwargs):

		# saved settings
		self.rt_angle = None
		self.rt_pos = None
		self.rt_text = "<empty>"
		self.rt_font_size = 16
		self.rt_font_name = None
		self.rt_anchor = (0,0)
		self.rt_color = [1,1,1,1]
		self.rt_bgnd = False
		self.rt_bcolor = [0,0,0,1]

		# saved drawing instructions:
		self.rotation = None
		self.textrect = None
		self.bgndrect = None
		self.bgndcolor = None

		#varianten
		self.mode = 1

	def setup(self,text=None,pos=None,angle=None,
			font_size=None,font_name=None,anchor=None,color=None,
			bgnd=None,bcolor=None):

		if angle is None: angle = 0.0
		self.rt_angle = angle
		if pos is None: pos=(0.0,0.0)
		self.rt_pos = pos
		if text is None: text = "<empty>"
		self.rt_text = text
		if font_size is None: font_size = 90
		self.rt_font_size = font_size
		self.rt_font_name = font_name
		if anchor is None: anchor = (0,0)
		self.rt_anchor = anchor
		if color is None: color = [1,1,1,1]
		self.rt_color = color
		if bgnd is None: bgnd = False
		self.rt_bgnd = bgnd
		if bcolor is None: bcolor = [0,0,0,1]
		self.rt_bcolor = bcolor

		l = Label(pos=(-200,-200))
		l.text = self.rt_text
		if self.mode==0:
			l.font_size = self.rt_font_size
		elif self.mode == 1:
			l.font_size = 90
		l.color = self.rt_color
		if self.rt_font_name is not None:
			l.font_name = self.rt_font_name
		l.texture_update()
		t = l.texture
		if self.mode==1:
			size = (self.rt_font_size*t.size[0]/t.size[1],self.rt_font_size)

		x = self.rt_pos[0]
		y = self.rt_pos[1]
		if self.mode == 0:
			xo = t.size[0] * (self.rt_anchor[0]-1) / 2.0
			yo = t.size[1] * (self.rt_anchor[1]-1) / 2.0
		elif self.mode == 1:
			xo = size[0] * (self.rt_anchor[0]-1) / 2.0
			yo = size[1] * (self.rt_anchor[1]-1) / 2.0

		PushMatrix()
		self.rotation = Rotate(angle=self.rt_angle,origin=(x,y))
		if self.rt_bgnd:
			Translate(0,0,-0.001)
			self.bgndcolor = set_color(self.rt_bcolor)
			self.bgndrect = Rectangle(pos=(x+xo,y+yo),size=t.size)
			Translate(0,0,0.001)
		set_color([1,1,1,1])
		if self.mode == 0:
			self.textrect = Rectangle(texture=t,pos=(x+xo,y+yo),size=t.size)
		elif self.mode == 1:
			self.textrect = Rectangle(texture=t,pos=(x+xo,y+yo),size=size)
		PopMatrix()
		l.text = ""

	def update(self,text=None,pos=None,angle=None,
			font_size=None,font_name=None,anchor=None,color=None,
			bgnd=None,bcolor=None):

		if self.rotation is None:
			return

		if angle is not None: self.rt_angle = angle
		if pos is not None: self.rt_pos = pos
		if text is not None: self.rt_text = text
		if font_size is not None: self.rt_font_size = font_size
		if anchor is not None: self.rt_anchor = anchor
		if color is not None: self.rt_color = color
		if bgnd is not None: self.rt_bgnd = bgnd
		if bcolor is not None: self.rt_bcolor = bcolor

		l = Label(pos=(-200,-200))
		l.text = self.rt_text
		if self.mode == 0:
			l.font_size = self.rt_font_size
		elif self.mode == 1:
			l.font_size = 90
		l.color = self.rt_color
		if self.rt_font_name is not None:
			l.font_name = self.rt_font_name
		l.texture_update()
		t = l.texture
		if self.mode == 1:
			size = (self.rt_font_size*t.size[0]/t.size[1],self.rt_font_size)

		x = self.rt_pos[0]
		y = self.rt_pos[1]
		if self.mode == 0:
			xo = t.size[0] * (self.rt_anchor[0]-1) / 2.0
			yo = t.size[1] * (self.rt_anchor[1]-1) / 2.0
		elif self.mode == 1:
			xo = size[0] * (self.rt_anchor[0]-1) / 2.0
			yo = size[1] * (self.rt_anchor[1]-1) / 2.0

		self.rotation.angle = self.rt_angle
		if self.rt_bgnd and self.bgndrect is not None:
			self.bgndcolor.r = self.rt_bcolor[0]
			self.bgndcolor.g = self.rt_bcolor[1]
			self.bgndcolor.b = self.rt_bcolor[2]
			self.bgndcolor.a = self.rt_bcolor[3]
			self.bgndrect.pos = (x+xo,y+yo)
		self.textrect.texture = t
		self.textrect.pos = (x+xo,y+yo)
		if self.mode == 0:
			self.textrect.size = t.size
		else:
			self.textrect.size = size
		l.text = ""


def rotated_text(text="<empty>",pos=(0,0),angle=0,
		font_size=16,font_name="",anchor=(0,0),color=[1,1,1,1],
		bgnd=False,bcolor=[0,0,0,1]):
	x = pos[0]
	y = pos[1]
	l = Label(text=text,font_size=font_size,pos=(-100,-100))
	l.color = color
	if font_name:
		l.font_name = font_name
	#print ("fontsdir",LabelBase.get_system_fonts_dir())
	l.texture_update()
	#print("FontName ********* ",l.font_name)
	t = l.texture
	xo = t.size[0] * (anchor[0]-1) / 2.0
	yo = t.size[1] * (anchor[1]-1) / 2.0
	PushMatrix()
	Rotate(angle=angle,origin=(x,y))
	if bgnd:
		set_color(bcolor)
		Rectangle(pos=(x+xo,y+yo),size=t.size)
		set_color([1,1,1,1])
	Rectangle(texture=t,pos=(x+xo,y+yo),size=t.size)
	PopMatrix()
	l.text = ""


def rectangle(pos=(-1.0,-1.0),size=(2.0,2.0),width=1.0):
	w = size[0]
	h = size[1]
	p = pos
	Line(points=(
		p[0],p[1],
		p[0]+w,p[1],
		p[0]+w,p[1]+h,
		p[0],p[1]+h,
		p[0],p[1]),
		width=width)

# =============================================================================
# hsv helpers

def hsva_to_rgba(val):
	abc = list(hsv_to_rgb(val[0],val[1],val[2]))
	abc.append(val[3])
	return abc

def rgba_to_hsva(val):
	abc = list(rgb_to_hsv(val[0],val[1],val[2]))
	abc.append(val[3])
	return abc

def hsva_conv(c,hsft=0.0):
	d = c.copy()
	if hsft!=0.0:
		def floormod(v,d): return v - math.floor(v / d)
		d[0] = floormod(d[0] + hsft,1.0)
	return hsva_to_rgba(d)

# =============================================================================

def set_color(color=[0,0,0,0]):
	return Color(color[0],color[1],color[2],color[3])

def color_range(cfrom=[0,0,0,0],cto=[1,1,1,1],param=0.5):
	if param<0.0: return cfrom
	elif param > 1.0: return cto
	else:
		return [ (cfrom[i]+param*(cto[i]-cfrom[i])) for i in range(0,4) ]

def color_range_ext(*args,param=0.5):
	s = len(args)
	if param<0.0: return args[0]
	elif param >= 1.0: return args[s-1]
	else:
		s = s-1
		ps = param*s
		i = math.floor(ps)
		p = ps - i
		if i < s:
			return color_range(args[i],args[i+1],p)
		else:
			return args[s]	# (darf eigentlich nicht vorkommen).

def set_color_range(cfrom=[0,0,0,0],cto=[1,1,1,1],param=0.5):
	return set_color(color_range(cfrom,cto,param))

# =============================================================================
# object creation

def baloon(lcolor=[0.1,0.1,0.1,1],lwidth=1.0,lscale=0.9,triangle=True,line=False):
	Ellipse(pos=(-1,-1),size=(2,2))
	PushMatrix()
	set_color(lcolor)
	Scale(lscale,origin=(0,0))
	Line(circle=(0,0,1.0),width=lwidth)
	if triangle:
		ex = math.cos(math.radians(30))
		Line(points=[1.0,0.0,-0.5,-ex],width=lwidth)
		Line(points=[1.0,0.0,-0.5,ex],width=lwidth)
		Line(points=[-0.5,-ex,-0.5,ex],width=lwidth)
		Line(points=[1.0,0.0,-1.0,0.0],width=lwidth)
	if line:
		Line(points=[0.0,-1.5,0.0,1.5],width=lwidth)
	PopMatrix()

def triangle(lcolor=[1,1,1,0.1]):
	set_color(lcolor)
	vertices = [1.0,0.0,0,0, 0.0,-1.0,0,0, 0.0,1.0,0,0]
	indices = [0,1,2]
	Mesh(vertices=vertices, indices=indices).mode = 'triangle_fan'

def raute(lcolor=[1,1,1,0.1]):
	set_color(lcolor)
	vertices = [1.0,0.0,0,0, 0.0,1.0,0,0, -1.0,0.0,0,0,
							1.0,0.0,0,0,  0.0,-1.0,0,0, -1.0,0.0,0,0]
	indices = [0,1,2,4,5,6]
	Mesh(vertices=vertices, indices=indices).mode = 'triangle_fan'

__welle = None
def welle(lcolor=[1,1,1,0.1]):
	global __welle
	if __welle is None:
		__welle = InstructionGroup()
		__welle.add(Color(lcolor[0],lcolor[1],lcolor[2],lcolor[3]))

		shape = []
		for i in range(-9,10):
			shape.append((math.cos(math.radians(float(i)*20.0))+1.0)*0.5)
			shape.append(float(i)/9.0)
		for i in range(-9,10):
			shape.append((-math.cos(math.radians(float(-i)*20.0))-1.0)*0.5)
			shape.append(float(-i)/9.0)

		tess = Tesselator()
		tess.add_contour(shape)
		if not tess.tesselate():
			print("Tesselator didn't work :(")
			tess = None

		if tess is not None:
			for vertices, indices in tess.meshes:
				__welle.add(Mesh(vertices=vertices,indices=indices,mode="triangle_fan"))

	return __welle

# =============================================================================
# fonts.

class LFontSizer(EventDispatcher):
	scdim = NumericProperty(480)

	def __init__(self,**kw):
		super(LFontSizer,self).__init__(**kw)

	def set_screen_size(self,dim):
		print ('screen_size =',dim)
		self.scdim = dim

	def small(self):
		return self.scdim // 25

	def middle(self):
		return self.scdim // 15

	def angle(self):
		return self.scdim // 10

	def bind_widget(self,widget,func):
		def fsb(widget,func):
			def sf(a,b):
				widget.font_size = func()
			return sf
		self.bind(scdim=fsb(widget, func))

LFont = LFontSizer()

# =============================================================================
