

import math
from array import array
from itertools import chain
from colorsys import hsv_to_rgb, rgb_to_hsv

from kivy.graphics.texture import Texture

from graphics import color_range_ext, hsva_to_rgba, rgba_to_hsva, hsva_conv

# =============================================================================
# 2d buffer for rgba textures.

class rgba2d(object):
	def __init__(self,size=64):
		self.size = size
		buf = [0 for i in range(size*size*4)]
		self.arr = array('B', buf)
		#print(len(self.arr))

	def get(self,x,y,hsva=False):
		ret = [self.arr[(y*self.size+x)*4+i]/255.0 for i in range(4)]
		return ret

	def put(self,x,y,val):
		k = 0
		for i in val:
			self.arr[int((y*self.size+x)*4+k)] = int(i*255)
			k += 1

# =============================================================================

class Gradient(object):

	@staticmethod
	def horizontal(*args,size=None,hsva=False,hsft=0.0):
		if size is None:
			size = len(args)
		texture = Texture.create(size=(size, 1), colorfmt='rgba')

		lst = []
		for x in range(0,size):
			val = color_range_ext(*args,param=(float(x)/float(size-1)))
			if hsva: val = hsva_conv(val,hsft=hsft)
			lst.extend([int(val[i]*255) for i in range(4)])

		#lst = []
		#for c in args:
		#	d = c
		#	if hsva: d = hsva_conv(c,hsft=hsft)
		#	lst.extend([int(d[i]*255) for i in range(4)])

		buf = bytes(lst)
		texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
		return texture

	@staticmethod
	def vertical(*args,size=None,hsva=False,hsft=0.0):
		if size is None:
			size = len(args)
		texture = Texture.create(size=(1, size), colorfmt='rgba')

		lst = []
		for x in range(0,size):
			val = color_range_ext(*args,param=(float(x)/float(size-1)))
			if hsva: val = hsva_conv(val,hsft=hsft)
			lst.extend([int(val[i]*255) for i in range(4)])

		buf = bytes(lst)
		texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
		return texture

	@staticmethod
	def centered(*args,size=64,center=(0.5,0.5),hsva=False,hsft=0.0):
		texsize = size
		#print('texsize',texsize,len(args))
		tex = Texture.create(size=(texsize, texsize))
		texarr = rgba2d(texsize)
		for x in range(0,texsize,1):
			dx = abs(int(math.floor(center[0]*texsize)-x))
			for y in range(0,texsize,1):
				dy = abs(int(math.floor(center[1]*texsize)-y))
				r = math.sqrt(dx*dx+dy*dy)
				p = 2*r/texsize

				val = color_range_ext(*args,param=p)
				if hsva: val = hsva_conv(val,hsft=hsft)
				texarr.put(x,y,val)

		tex.blit_buffer(texarr.arr, colorfmt='rgba', bufferfmt='ubyte')
		return tex

# =============================================================================
