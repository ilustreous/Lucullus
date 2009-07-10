#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Marcel Hellkamp on 2008-08-20.
Copyright (c) 2008 Marcel Hellkamp. All rights reserved.
"""

import cPickle as pickle
import UserDict
from lucullus.base import config
from lucullus.base.renderer import hexcolor
import urllib2
import tempfile
import math
from StringIO import StringIO
import cairo
import time
import os
import os.path
import random
import inspect

""" List of Resource plugins """
plugins = {}

def register_plugin(name, cls):
	if not isinstance(cls, type):
		cls = cls.__class__
	if not issubclass(cls, BaseResource):
		raise AttributeError('Resources must implement BaseResource.')
	if name not in plugins:
		plugins[name] = cls



class ResourceError(Exception): pass
class ResourceUploadError(ResourceError): pass
class ResourceQueryError(ResourceError): pass
class ResourceQueryNoApiError(ResourceQueryError): pass
class ResourceQueryOptionsError(ResourceQueryError): pass


class BaseResource(object):
	""" An empty cache-, pick- and saveable data container bound to a session. """
	def __init__(self):
		self.mtime = time.time()
		self.atime = time.time()
		self.prepare()

	def state(self):
		""" Should return a dict with some infos about this resource """
		return {}

	def prepare(self):
		""" Called on resource creation """
		pass

	def touch(self, mtime = True):
		""" Mark the resource as modified """
		if mtime:
			self.mtime = time.time()
		self.atime = time.time()

	def configure(self, **options):
		''' May change the resources state but does not return anything '''
		pass

	def query(self, name, **options):
		''' May change the resources state and returns a result dict '''

		try:
			c = getattr(self, "api_" + name)
		except (AttributeError), e:
			raise QueryNoApiError("Resource %s does not implement %s()" % (self.__class__.__name__, name))
		
		# Parameter testing
		provided = set(options.keys())
		available, onestar, twostar, defaults = inspect.getargspec(c)
		available.remove('self')
		if not defaults:
			requied = set(available)
		else:
			requied = set(available[0:-len(defaults)])
		available = set(available)
		missing = requied - provided
		if missing:
			raise QueryOptionsError('Missing arguments: %s' % ','.join(missing))
		unknown = provided - available
		if unknown and not twostar:
			raise QueryOptionsError('Unknown arguments: %s' % ','.join(unknown))

		self.touch(False)
		return c(**options)






class BaseView(BaseResource):
	
	def __init__(self, *l, **d):
		super(BaseView, self).__init__(*l, **d)

	def size(self):
		""" Should return the absolute size of the drawable area in pixel. """
		return (0,0)
		
	def offset(self):
		""" Should return the (x,y) offset of the drawable area in pixel. """
		return (0,0)

	def state(self):
		w, h = self.size()
		ox, oy = self.offset()
		return {'width':w, 'height':h, 'offset':[ox, oy], 'size':[w, h]}

	def render(self, context, x=0, y=0, width=0, height=0):
		""" Renders the selected area of the data into a cairo context. """






class IndexView(BaseView):
	def prepare(self, **options):
		self.fontsize = 12 
		self.index = []
		self.color = {}
		self.color['fontcolor'] = hexcolor('#000000FF')

	def size(self):
		w = max([len(i) for i in self.index] + [0]) * self.fontsize
		h = len(self.index) * self.fontsize
		return (w,h)

	def state(self):
		s = super(IndexView, self).state()
		s['rows'] = len(self.index)
		return s

	def configure(self, **options):
		self.fontsize = int(options.get('fontsize', self.fontsize))
		if 'keys' in options and isinstance(options['keys'], list):
			self.index = map(str, options['keys'])

	def setfontoptions(self, context):
		context.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		options = cairo.FontOptions()
		#fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		#fo.set_hint_style(cairo.HINT_STYLE_NONE)
		options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		context.set_font_options(options)
		context.set_font_size(self.fontsize - 1)
		return context.font_extents()

	def render(self, context, x, y, w, h):
		# Shortcuts
		cminx, cminy, cmaxx, cmaxy = x, y, x+w, y+h
		c = context
		lineheight = self.fontsize
		fontsize = self.fontsize - 1
		color = self.color
		index = self.index

		# Configuration
		self.setfontoptions(c)
		real_lineheight = context.font_extents()[1]

		# Rows to consider
		row_first = int(math.floor( float(cminy) / lineheight))
		row_last  = int(math.ceil(	float(cmaxy) / lineheight))
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
		self.step		= 14
		self.marks		= 1
		self.digits		= 10
		self.fontsize	= 12
		self.color = {}
		self.color['fontcolor'] = hexcolor('#000000FF')

	def api_set(self, **options):
		self.step		= int(options.get('step', self.step))
		self.marks		= int(options.get('marks', self.marks))
		self.digits		= int(options.get('digits', self.digits))
		self.fontsize	= int(options.get('fontsize', self.fontsize))

	def size(self):
		return (2**16, self.fontsize + 5)
		
	def offset(self):
		return (0,0)

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



# Register common Plugins
register_plugin("Index", IndexView)
register_plugin("Ruler", RulerView)
