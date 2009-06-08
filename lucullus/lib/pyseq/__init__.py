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

		self.resources = {}
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

	def new_resource(self, cls, name = None):
		""" Creates a new Resource in this session """
		if not isinstance(cls, type):
			raise AttributeError('Cannot create a resource from an object.')
		if not issubclass(cls, BaseResource):
			raise AttributeError('All resources must implement BaseResource.')

		c = 0
		while not name or name in self.resources:
			c += 1
			name = 'tmp%d' % c
		name = str(name)
		resource = cls(self)
		resource.id = name
		self.resources[name] = resource
		self.touch()
		return resource

	def get_resource(self, id):
		try:
			return self.resources[str(id)]
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

	def getApiMethod(self, name):
		return getattr(self, "api_" + name)





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

	def size(self):
		""" Should return the absolute size of the drawable area in pixel. """
		return (0,0)
		
	def status(self):
		w, h = self.size()
		ox, oy = self.offset()
		return {'width':w, 'height':h, 'offset':[ox, oy], 'size':[w, h]}
		
	def offset(self):
		""" Should return the (x,y) offset of the drawable area in pixel. """
		return (0,0)

	def render(self, context, x=0, y=0, width=0, height=0):
		""" Renders the selected area of the data into a cairo context. """





class IndexView(BaseView):
	def prepare(self, **options):
		self.lineheight = options.get('lineheight',12)
		self.index = []
		self.source = None
		self.color = {}
		self.color['fontcolor'] = hexcolor('#000000FF')

	def size(self):
		w = max([len(i) for i in self.index] + [0]) * self.lineheight
		h = len(self.index) * self.lineheight
		return (w,h)

	def status(self):
		s = super(IndexView, self).status()
		s['rows'] = len(self.index)
		return s

	def api_set(self, **options):
		self.lineheight = int(options.get('lineheight', self.lineheight))

	def api_load(self, source, offset=0, limit=1024):
		self.source = source
		src = self.session.get_resource(self.source)
		try:
			self.index = src.getIndex()
		except AttributeError, e:
			raise pyseq.ResourceQueryError('Can not load index. %s.getIndex() not found' % src.__class__.__name__)
		self.index = list(self.index)
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

	def render(self, context, x, y, w, h):
		# Shortcuts
		cminx, cminy, cmaxx, cmaxy = x, y, x+w, y+h
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


class RulerView(BaseView):
	def prepare(self):
		self.step       = 14
		self.marks      = 1
		self.digits     = 10
		self.fontsize   = 12
		self.skip       = 0
		self.color = {}
		self.color['fontcolor'] = hexcolor('#000000FF')

	def api_set(self, **options):
		self.step       = int(options.get('step', self.step))
		self.marks      = int(options.get('marks', self.marks))
		self.digits     = int(options.get('digits', self.digits))
		self.skip       = int(options.get('skip', self.skip))
		self.fontsize   = int(options.get('fontsize', self.fontsize))

	def size(self):
		return (2**16, self.fontsize + 5)
		
	def offset(self):
		return (-2**15 + self.skip,0)

	def render(self, context, x, y, w, h):
		cminx, cminy, cmaxx, cmaxy = x, y, x+w, y+h
		c = context

		first = x - x % self.step
		last = x+w + (x+w) % self.step
		c.set_source_rgb(1, 1, 1)
		c.paint()

		fo = cairo.FontOptions()
		fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		fo.set_hint_style(cairo.HINT_STYLE_NONE)
		fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		c.set_font_options(fo)
		c.set_font_size(self.fontsize)
		font_extends = context.font_extents()
		
		c.set_source_rgb(0, 0, 0)
		for mark in xrange(first - self.step*self.digits, last + self.step*self.digits, self.step):
			if (mark % (self.step * self.digits)) == 0:
				name = str(mark / self.step)
				text_width, text_height = c.text_extents(name)[2:4]
				c.move_to(mark - text_width/2, font_extends[3])
				c.show_text(name)

		for mark in xrange(first, last, self.step):
			if (mark % (self.step * self.marks)) == 0:
				c.rectangle(mark,font_extends[3]+4,1,h)
			if (mark % (self.step * self.digits)) == 0:
				c.rectangle(mark,font_extends[3]+2,2,h)
			c.fill()

			
		return self

		"""
		# Rows to consider
		row_first = int(math.floor( float(vy-ay)	/ fieldsize))
		row_last  = int(math.ceil(	float(vy-ay+vh) / fieldsize))
		col_first = int(math.floor( float(vx-ax)	/ fieldsize))
		col_last  = int(math.ceil(	float(vx-ax+vw) / fieldsize))

		# To prevent cutting numbers at the view border, we have to look bejond the borders
		col_last	+= 10 - col_last % 10 + 1
		col_first	-= col_first % 10 + 1


		# Font settings
		c.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		fo = cairo.FontOptions()
		fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		fo.set_hint_style(cairo.HINT_STYLE_NONE)
		fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		c.set_font_options(fo)
		if not self.fontsize:
			fsize = sum(c.font_extents()[0:2])
			fsize = float(fieldsize) * 0.75 * (fieldsize / fsize)
			self.fontsize = fsize
		c.set_font_size(self.fontsize)
		c.set_source_rgb(0, 0, 0)
		font_extends = context.font_extents()

		for i in range(col_first,col_last):
			# Draw marks
			x = i * fieldsize + fieldsize/2
			if (i % 5) == 0:
				c.rectangle(x,20-5,1,ah)
			elif (i % 10) == 0:
				c.rectangle(x-1,20-5,3,ah)
			else:
				c.rectangle(x,20-2,1,ah)
			c.fill()

			# Draw Numbers			
			if (i % 10) == 0:
				name = str(i)
				text_width, text_height = c.text_extents(name)[2:4]
				x = i * fieldsize + fieldsize/2 - text_width/2
				y = 20 - font_extends[1] - 5
				c.move_to(x, y)
				c.show_text(name)

		return self
		"""



# Register common Plugins
register_plugin("IndexView", IndexView)
register_plugin("RulerView", RulerView)
register_plugin("TextResource", TextResource)
