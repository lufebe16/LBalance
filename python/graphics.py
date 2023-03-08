

import math

from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.graphics import *
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

# =============================================================================
# graphic helpers

def rotated_text(text="<empty>",pos=(0,0),angle=0,font_size=16,font_name="",anchor=(0,0),color=[1,1,1,1],bgnd=False,bcolor=[0,0,0,1]):
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

def set_color(color=[0,0,0,0]):
	Color(color[0],color[1],color[2],color[3])

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

def set_color_range(cfrom=[0,0,0,0],cto=[1,1,1,1],param=0.5):
	set_color(color_range(cfrom,cto,param))

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
