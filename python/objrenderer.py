'''
Derived from 3D Rotating Monkey Head example.
============================================

- Rendering into an Fbo framebuffer in order to allow normal placement
	and scaling in a widget as usual.
- Adapted the corresponding glsl file to also work with android.
'''

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST
from kivy.graphics import RenderContext, Callback, PushMatrix, PopMatrix, \
	Color, Translate, Rotate, Scale, Mesh, UpdateNormalMatrix, Fbo, Rectangle, \
	ClearColor, ClearBuffers
# from kivy.graphics.context_instructions import Transform
from objloader import ObjFile


class ObjRenderer(Widget):
	def __init__(self, objfile=None, **kwargs):
		super(ObjRenderer,self).__init__(*kwargs)

		if objfile is None:
			self.scene = ObjFile(resource_find("data/feder1.obj"))
		else:
			self.scene = ObjFile(resource_find(objfile))

		self.scale_xyz = (1,1,1)

		self.fbo = Fbo(size=(1024,1024),with_depthbuffer=True)
		self.fbo.shader.source = 'glsl/obj3d.glsl'
		self.fbo.add_reload_observer(self.setup_scene)

		matvc = Matrix().view_clip(-1.0,1.0,-1.0,1.0,1,120,1)
		self.fbo['projection_mat'] = matvc
		self.canvas.add(self.fbo)		# ohne gehts nicht ?!

		with self.fbo:
			ClearColor(0, 0, 0, 0)
			ClearBuffers(clear_depth=True)
			self.cb = Callback(self.setup_gl_context)
			self.setup_scene(self.fbo)
			self.cb = Callback(self.reset_gl_context,reset_buffer=True)

		with self.canvas:
			PushMatrix()
			self.fbocolor = Color(1,1,1,1)
			self.fborect = Rectangle(
				texture=self.fbo.texture,pos=self.pos,size=self.size)
			PopMatrix()

		Clock.schedule_interval(self.update_scene, 1 / 30.)

	def setup_gl_context(self, *args):
		glEnable(GL_DEPTH_TEST)

	def reset_gl_context(self, *args):
		glDisable(GL_DEPTH_TEST)

	def setScale(self,xy=None,xyz=None):
		self.scale_xyz = (1,1,1)
		if xyz is not None:
			self.scale_xyz = xyz
		elif xy is not None:
			self.scale_xyz = (xy[0],xy[1],1)

	def update_scene(self, delta):

		# these are not used (see obj3d.glsl).
		#self.fbo['diffuse_light'] = (1.0, 1.0, 0.8)
		#self.fbo['ambient_light'] = (0.1, 0.1, 0.1)

		# put the scene at the center.
		px,py = self.pos
		sx,sy = self.size
		siz = min(sx,sy)
		self.fborect.texture = self.fbo.texture
		self.fborect.pos = (px+(sx-siz)/2.0,py+(sy-siz)/2.0)
		self.fborect.size = (siz,siz)

		# move it
		self.rot.angle += delta * 100
		self.scale.x = self.scale_xyz[0] 
		self.scale.y = self.scale_xyz[1]
		self.scale.z = self.scale_xyz[2]

	def setup_scene(self,fbo):
		with self.fbo:
			PushMatrix()
			self.col = Color(1,0.98,0.77,1)
			self.trans = Translate(0, 0, -22)
			self.scale = Scale(x=1,y=1,z=1)
			self.rot = Rotate(angle=90, axis=(1,1,-1), origin=(0,0,6))
			m = list(self.scene.objects.values())[0]
			UpdateNormalMatrix()
			self.mesh = Mesh(
				vertices=m.vertices,
				indices=m.indices,
				fmt=m.vertex_format,
				mode='triangles',
			)
			PopMatrix()
