

import math
from array import array
from itertools import chain

from kivy.graphics.texture import Texture

from graphics import color_range_ext

# =============================================================================
# 2d buffer for rgba textures.

class rgba2d(object):
	def __init__(self,size=64):
		self.size = size
		buf = [0 for i in range(size*size*4)]
		self.arr = array('B', buf)
		print(len(self.arr))

	def get(self,x,y):
		return [self.arr[(y*self.size+x)*4+i]/255.0 for i in range(4)]

	def put(self,x,y,val):
		k = 0
		for i in val:
			self.arr[int((y*self.size+x)*4+k)] = int(i*255)
			k += 1

# =============================================================================

class Gradient(object):

	@staticmethod
	def horizontal(*args):
		texture = Texture.create(size=(len(args), 1), colorfmt='rgba')
		buf = bytes([int(v * 255) for v in chain(*args)])  # flattens

		texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
		return texture

	@staticmethod
	def vertical(*args):
		texture = Texture.create(size=(1, len(args)), colorfmt='rgba')
		buf = bytes([int(v * 255) for v in chain(*args)])  # flattens
		texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
		return texture

	@staticmethod
	def centered(*args,center=(0.5,0.5)):
		texsize = 128
		tex = Texture.create(size=(texsize, texsize))
		texarr = rgba2d(texsize)
		for x in range(0,texsize,1):
			#dx = abs(texsize//2-x)
			dx = abs(int(center[0]*texsize)-x)
			for y in range(0,texsize,1):
				#dy = abs(texsize//2-y)
				dy = abs(int(center[1]*texsize)-y)
				r = math.sqrt(dx*dx+dy*dy)
				p = 2*r/texsize
				texarr.put(x,y,color_range_ext(*args,param=p))

		tex.blit_buffer(texarr.arr, colorfmt='rgba', bufferfmt='ubyte')
		return tex

# =============================================================================
