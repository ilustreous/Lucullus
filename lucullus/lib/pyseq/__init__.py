#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Marcel Hellkamp on 2008-08-20.
Copyright (c) 2008 Marcel Hellkamp. All rights reserved.
"""

import cPickle as pickle
import UserDict
from lucullus.lib.pyseq import config
from lucullus.lib.pyseq.renderer import hexcolor
import urllib2
import tempfile
import math
from StringIO import StringIO
import cairo
import time
import os
import os.path
import random

""" List of Resource plugins """
plugins = {}

def register_plugin(name, obj):
	if name not in plugins:
		plugins[name] = obj






class ResourceError(Exception): pass
class ResourceUploadError(ResourceError): pass
class ResourceQueryError(ResourceError): pass






class Session(object):
	""" A Work enviroment bound to a session_id. Holds and manages multible resources. """

	def __init__(self, savepath):
		""" Startes a new session and creates a new workpath. Every session.id is unique for a savepath.
		@param savepath writable path to create the workpath in
		@return session id (uniq string with len() = 32) """
		self.id = None
		self.savepath = savepath + "/"
		self.workpath = None
		self.filename = None

		self.resources = []
		self.ctime = time.time()
		self.mtime = time.time()
		self.atime = time.time()

		while 1:
			self.id	 = "%x" % random.getrandbits(128)
			path = self.default_path()
			if not os.path.isdir(path):
				break

		os.makedirs(path)
		self.workpath = path + "/"
		self.filename = path + "/session.pkl"

	def default_path(self):
		parts = (self.savepath, self.id[0:2], self.id[2:4], self.id)
		path = '/'.join(parts)
		return os.path.abspath(path)

	def touch(self, mtime = True):
		""" Mark the resource as modified """
		if mtime:
			self.mtime = time.time()
		self.atime = time.time()

	def new_resource(self, cls):
		""" Creates a new Resource in this session """
		if not isinstance(cls, type):
			raise AttributeError('Cannot create a resource from an object.')
		if not issubclass(cls, BaseResource):
			raise AttributeError('All resources must implement BaseResource.')

		resource = cls(self)
		self.resources.append(resource)
		self.touch()

		resource.id = self.resources.index(resource)
		return resource

	def get_resource(self, id):
		try:
			return self.resources[int(id)]
		except:
			return None






class BaseResource(object):
	""" An empty cache-, pick- and saveable data container bound to a session. """
	def __init__(self, session):
		self.ctime = time.time()
		self.mtime = time.time()
		self.atime = time.time()
		self.session = session
		self.id = None
		self.prepare()
	
	def status(self):
		""" Shoueld return a dict with some infos about this resource """
		return {}
	
	def prepare(self):
		pass

	def touch(self, mtime = True):
		""" Mark the resource as modified """
		if mtime:
			self.mtime = time.time()
		self.atime = time.time()
		
	def export(self):
		return ''






class TextResource(BaseResource):
	def prepare(self):
		self.data = ''
		self.source = None

	def api_load(self, uri):
		if uri.startswith("http://"):
			data = tempfile.TemporaryFile(mode='a+b')
			try:
				data.write(urllib2.urlopen(uri, None).read())
			except (urllib2.URLError, urllib2.HTTPError), e:
				raise ResourceQueryError('Faild do open URI: %s' % uri)

			data.seek(0)
			self.data = data.read()
			self.source = uri
			self.touch()
			return {'size':len(self.get())}
		else:
			raise ResourceQueryError('Unsupported protocol or uri syntax: %s' % uri)

	def status(self):
		""" Shoueld return a dict with some infos about this resource """
		return {'size':len(self.get())}

	def get(self):
		return self.data
		
	def getIO(self):
		return StringIO(self.data)

	def export(self):
		return self.data






class BaseView(BaseResource):
	
	def __init__(self, *l, **d):
		super(BaseView, self).__init__(*l, **d)
		self.size			= [0.0,0.0]		# Size (width,height) of the drawable area
		self.selected		= (0.0,0.0,0.0,0.0)		# Offset of the rendering window

	def status(self):
		""" Shoueld return a dict with some infos about this resource """
		return {'width':self.size[0], 'height':self.size[1]}
		
	def select(self, x=0, y=0, width = 0, height = 0):
		""" Selects an area within the real coordnates to render.
			x, y = offset
			width, height = size of the area. Skip to scale 1 to 1"""
		self.selected = (int(x), int(y), abs(int(width)), abs(int(height)))
	
	def viewport(self, x, y, width=255, height=255, relative=False):
		""" Veraltet """
		self.select(x, y, width, height)

	def render(self, io, width = 0, height = 0, format = 'png', mode='ARGB32'):
		""" Renders the (selected area of the) image into a Stream using $format and $mode and scaling down to $width and $height """
		width = abs(int(width))
		height = abs(int(height))
		sx, sy, sw, sh = self.selected
		# If target width is missing, use width of selected area or the whole drawable image. 
		width = width or sw or (self.size[0]-sx)
		height = height or sw or (self.size[1]-sy)
		# If no scaling is selected, draw 1 to 1
		sw = sw or width
		sh = sh or height

		if "ARGB32" == mode:
			surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
		elif "RGB24" == mode:
			surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
		else:
			raise NotImplementedError
			
		context = cairo.Context(surface)
		context.scale(width/sw, height/sh)
		context.translate(-sx, -sy)
		self.draw(context, clipping=(sx, sy, sw+sx, sh+sy))
		if format == 'png':
			surface.write_to_png(io)
		else:
			raise NotImplementedError

	def draw(self, context, clipping):
		''' Draws into a cairo context using real coordinates (do not scale or translate) and clipping '''
		pass






class IndexView(BaseView):
	def prepare(self, **options):
		self.lineheight = options.get('lineheight',12)
		self.index = []
		self.source = None
		self.offset = 0
		self.limit = 1024
		self.color = {}
		self.color['fontcolor'] = hexcolor('#000000FF')

	def status(self):
		s = super(IndexView, self).status()
		s['rows'] = len(self.index)
		return s

	def api_set(self, **options):
		self.lineheight = int(options.get('lineheight', self.lineheight))
		self.size[0] = max([len(i) for i in self.index] + [0]) * self.lineheight
		self.size[1] = len(self.index) * self.lineheight


	def api_load(self, source, offset=0, limit=1024):
		self.source = source
		self.offset = abs(int(offset))
		self.limit = abs(int(limit))
		src = self.session.get_resource(self.source)
		try:
			self.index = src.getIndex()
		except AttributeError, e:
			raise pyseq.ResourceQueryError('Can not load index. %s.getIndex() not found' % src.__class__.__name__)
		try:
			self.index = list(self.index)[self.offset:self.limit]
		except IndexError:
			raise pyseq.ResourceQueryError('Can not satisfy offset %d or limit %d' % (self.offset, self.limit))
		
		self.size[0] = max([len(i) for i in self.index] + [0]) * self.lineheight
		self.size[1] = len(self.index) * self.lineheight
		self.touch()
		return {'items':len(self.index)}

	def setfontoptions(self, context):
		context.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		options = cairo.FontOptions()
		#fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		#fo.set_hint_style(cairo.HINT_STYLE_NONE)
		options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		context.set_font_options(options)
		context.set_font_size(self.lineheight - 1)
		return context.font_extents()

	def draw(self, context, clipping):
		# Shortcuts
		cminx, cminy, cmaxx, cmaxy = clipping
		w,h = cmaxx-cminx, cmaxy-cminy
		c = context
		lineheight = self.lineheight
		fontsize = self.lineheight - 1
		color = self.color
		index = self.index

		# Configuration
		self.setfontoptions(c)
		real_lineheight = context.font_extents()[1]

		# Rows to consider
		row_first = int(math.floor( float(cminy) / lineheight))
		row_last  = int(math.ceil(  float(cmaxy) / lineheight))
		row_last  = min(row_last, len(self.index)-1)

		# Fill the background with #ffffff
		(r,g,b,a) = self.color.get('background',(1,1,1,1))
		c.set_source_rgb(r, g, b)
		c.rectangle(cminx, cminy, cmaxx-cminx, cmaxy-cminy)
		c.fill()

		(r,g,b,a) = self.color.get('fontcolor',(0,0,0,1))
		c.set_source_rgba(r, g, b, a)
		font_extends = context.font_extents()

		for row in range(row_first, row_last+1):
			#if row % 2:
			#	c.set_source_rgb(0.95, 0.95, 0.95)
			#	c.rectangle(0, 0, vw, self.fieldsize)
			#	c.fill()
			#	c.set_source_rgb(0, 0, 0)
			name = self.index[row]
			y = lineheight * row + lineheight - font_extends[1]
			x = 0
			context.move_to(x, y)
			context.show_text(name)
		
		return self






# Register common Plugins
register_plugin("IndexView", IndexView)
register_plugin("TextResource", TextResource)
