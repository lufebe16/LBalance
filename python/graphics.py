

import math
from colorsys import hsv_to_rgb, rgb_to_hsv

from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, PushMatrix, PopMatrix, InstructionGroup
from kivy.graphics import Translate, Rotate, Scale
from kivy.graphics import Rectangle, RoundedRectangle, Mesh, Ellipse, Line
from kivy.graphics.tesselator import Tesselator
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

# =============================================================================
# graphic helpers

class RotatedText(object):
	def __init__(self,**kwargs):

		# saved settings
		self.rt_angle = 0.0
		self.rt_pos = (0.0,0.0)
		self.rt_text = "<empty>"
		self.rt_font_size = 90
		self.rt_font_name = None
		self.rt_anchor = (0,0)
		self.rt_color = [1,1,1,1]
		self.rt_bcolor = [0,0,0,0]

		# saved drawing instructions:
		self.translation = None
		self.rotation = None
		self.textrect = None
		self.bgndrect = None
		self.bgndcolor = None
		self.bround = False

	def __eval(self,text=None,pos=None,angle=None,
			font_size=None,font_name=None,anchor=None,color=None,
			bcolor=None):

		if angle is not None: self.rt_angle = angle
		if pos is not None: self.rt_pos = pos
		if text is not None: self.rt_text = text
		if font_size is not None: self.rt_font_size = font_size
		if font_name is not None: self.rt_font_name = font_name
		if anchor is not None: self.rt_anchor = anchor
		if color is not None: self.rt_color = color
		if bcolor is not None: self.rt_bcolor = bcolor

		l = Label(pos=(-200,-200))
		l.text = self.rt_text
		l.font_size = self.rt_font_size
		l.color = self.rt_color
		if self.rt_font_name is not None:
			l.font_name = self.rt_font_name
		l.texture_update()
		t = l.texture
		x = self.rt_pos[0]
		y = self.rt_pos[1]
		z = 0
		try: z = self.rt_pos[2]
		except: pass
		xo = t.size[0] * (self.rt_anchor[0]-1) / 2.0
		yo = t.size[1] * (self.rt_anchor[1]-1) / 2.0
		l.text = ""

		#print(t,x,y,z,xo,yo)
		return (t,x,y,z,xo,yo)

	def setup(self,canvas,text=None,pos=None,angle=None,
			font_size=None,font_name=None,anchor=None,color=None,
			bcolor=None,bround=False):

		t,x,y,z,xo,yo = self.__eval(text=text,pos=pos,angle=angle,
			font_size=font_size,font_name=font_name,anchor=anchor,
			color=color,bcolor=bcolor)
		self.bround = bround

		with canvas:
			PushMatrix()
			self.translation = Translate(x=x,y=y,z=z)
			self.rotation = Rotate(angle=self.rt_angle,origin=(0,0))
			Translate(0,0,-0.001)
			self.bgndcolor = set_color(self.rt_bcolor)
			if self.bround:
				self.bgndrect = RoundedRectangle(
					pos=(xo,yo),
					size=t.size,
					segments=20,
					radius=[t.size[1],])
			else:
				self.bgndrect = Rectangle(pos=(xo,yo),size=t.size)
			Translate(0,0,0.001)
			set_color([1,1,1,1])
			self.textrect = Rectangle(texture=t,pos=(xo,yo),size=t.size)
			PopMatrix()

	def update(self,text=None,pos=None,angle=None,
			font_size=None,font_name=None,anchor=None,color=None,
			bcolor=None):

		if self.translation is None:
			return

		t,x,y,z,xo,yo = self.__eval(text=text,pos=pos,angle=angle,
			font_size=font_size,font_name=font_name,anchor=anchor,
			color=color,bcolor=bcolor)

		self.translation.xyz = (x,y,z)
		self.rotation.angle = self.rt_angle
		self.bgndcolor.rgba = self.rt_bcolor
		self.bgndrect.pos = (xo,yo)
		self.bgndrect.size = t.size
		if self.bround:
			self.bgndrect.radius = [t.size[1],]
		self.textrect.texture = t
		self.textrect.pos = (xo,yo)
		self.textrect.size = t.size

class RotatedTextWidget(Widget,RotatedText):
	def __init__(self,**kwargs):
		super(RotatedTextWidget,self).__init__(**kwargs)

	def setup(self,text=None,pos=None,angle=None,
			font_size=None,font_name=None,anchor=None,color=None,
			bcolor=None,bround=False):

		super().setup(self.canvas,
			text,pos,angle,font_size,font_name,anchor,color,bcolor,bround)


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
	Scale(x=lscale,y=lscale,origin=(0,0))
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

	# Anmerkung zu Mesh:
	# Mesh nimmt noch einen dritten parameter: fmt. Damit werden
	# die Zuordungen der Arraywerte (pro gruppe) zu opengl-shader variablen
	# beschrieben. Die Voreinstellung in kivy ist:
	#   fmt = [(b'vPosition', 2, 'float'), (b'vTexCoords0', 2, 'float'),]
	# und passt damit auf den standard shader.
	# (Wer sich nicht scheut eine eigenen shader zu adaptieren, kann hier
	# z.B. 3d koordinaten einführen.)

def welle(lcolor=[1,1,1,0.1]):
	if True:
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

from kivy.metrics import Metrics

class LFontSizer(EventDispatcher):
	scdim = NumericProperty(480)

	def __init__(self,**kw):
		super(LFontSizer,self).__init__(**kw)

	def set_screen_size(self,dim):
		print ('screen_size =',dim)
		self.scdim = dim

	def small(self,size=None):
		return self.norm(12,size=size)

	def middle(self,size=None):
		return self.norm(35,size=size)

	def angle(self,size=None):
		return self.norm(70,size=size)

	def norm(self,val,size=None):
		if size is None:
			n = val * self.scdim / 720.0
		else:
			n = val * size / 720.0
		n = n * 2.0 / Metrics.dp
		# 1.0: desktops default
		# 2.0: android (phones,tablets) default
		s = str(int(n))+'sp'
		return s

	def bind_widget(self,widget,func):
		def fsb(widget,func):
			def sf(a,b):
				widget.font_size = func()
			return sf
		self.bind(scdim=fsb(widget, func))

LFont = LFontSizer()

# =============================================================================
