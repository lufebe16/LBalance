

import math

from kivy.uix.label import Label
from kivy.graphics import *

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

def baloon(lcolor=[0.1,0.1,0.1,1],lwidth=1.0,lscale=0.9,triangle=True):
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
	PopMatrix()

def triangle(lcolor=[1,1,1,0.1]):
	set_color(lcolor)
	vertices = [1.0,0.0,0,0, 0.0,-1.0,0,0, 0.0,1.0,0,0]
	indices = [0,1,2]
	Mesh(vertices=vertices, indices=indices).mode = 'triangle_fan'

# =============================================================================
