#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Marcel Hellkamp on 2008-08-20.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import cPickle as pickle
import UserDict
from lucullus.lib.pyseq import config
from lucullus.lib.pyseq.renderer import hexcolor



try:
	import memcache
except ImportError:
	memcache = False
	print "WARNING: Memcache module not found. You might want to install it for better performance."

from StringIO import StringIO
import urllib2
import cairo
import time



""" List of Resource plugins """
plugins = {}

def register_plugin(name, obj):
	if name not in plugins:
		plugins[name] = obj


class ResourceError(Exception): pass
class ResourceUploadError(ResourceError): pass
class ResourceQueryError(ResourceError): pass


import os, os.path, random

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
	
	def prepare(self):
		pass

	def touch(self, mtime = True):
		""" Mark the resource as modified """
		if mtime:
			self.mtime = time.time()
		self.atime = time.time()
		
	def export(self):
		return ''




import urllib2
import tempfile

class TextResource(BaseResource):
	def prepare(self):
		self.data = None
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

	def get(self):
		return self.data
		
	def getIO(self):
		return StringIO(self.data)

	def export(self):
		return self.data

register_plugin("TextResource", TextResource)





class BaseView(BaseResource):
	
	def __init__(self, *l, **d):
		super(BaseView, self).__init__(*l, **d)
		self.size			= (0.0,0.0)			# Size (width,height) of the drawable area
		self.selected		= (0.0,0.0,0.0,0.0)		# Offset of the rendering window

	def getSize(self):
		return (0.0,0.0)
		
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








""" List of Project Plugins (outdated)"""
projects = {}

def add_project(name, obj):
	if name not in projects:
		projects[name] = obj









import math

class IndexView(BaseView):
	def prepare(self, **options):
		self.lineheight = options.get('lineheight',12)
		self.index = []
		self.source = None
		self.offset = 0
		self.limit = 1024
		self.color = {}
		self.color['fontcolor'] = hexcolor('#000000FF')

	def api_load(self, **options):
		self.source = options.get('rid')
		self.offset = int(options.get('offset',0))
		self.limit = int(options.get('limit',1024))
		src = self.session.get(self.source)
		try:
			self.index = src.getIndex()
		except AttributeError, e:
			raise pyseq.ResourceQueryError('Can not load index. %s.getIndex() not found' % src.__class__.__name__)
		try:
			self.index = list(self.index)[self.offset:self.limit]
		except IndexError:
			raise pyseq.ResourceQueryError('Can not satisfy offset %d or limit %d' % (self.offset, self.limit))
		self.touch()
		return {'items':len(self.index)}

	def setfontoptions(self, context):
		context.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		options = cairo.FontOptions()
		#fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		#fo.set_hint_style(cairo.HINT_STYLE_NONE)
		options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		context.set_font_options(options)
		context.set_font_size(self.lineheight - 2)
		return context.font_extents()

	def draw(self, context, clipping):
		# Shortcuts
		cminx, cminy, cmaxx, cmaxy = clipping
		w,h = cmaxx-cminx, cmaxy-cminy
		c = context
		lineheight = self.lineheight
		fontsize = self.lineheight - 2
		color = self.color
		index = self.index

		# Configuration
		self.setfontoptions(c)
		real_lineheight = context.font_extents()[1]

		# Rows to consider
		row_first = int(math.floor( float(cminy) / fieldsize))
		row_last  = int(math.ceil(  float(cmaxy) / fieldsize))
		row_last  = min(row_last, len(self.index))

		# Fill the background with #ffffff
		(r,g,b,a) = self.color.get('background',(0,0,0,1))
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
			y = self.fieldsize * row + self.fieldsize - font_extends[1]
			x = 0
			context.move_to(x, y)
			context.show_text(name)
		
		return self

register_plugin("IndexView", IndexView)











































class Ressource(object):
	""" Persistent Object container with get() and set(data) which saves its data to a pickle file and caches to memcache """
	memcache = None
	
	def __init__(self, filename, initial = None):
		self.filename = filename
		self.data = initial
		if self.data:
			self.save()

	def __getstate__(self):
		return {'filename': self.filename, 'data':None}

	def __call__(self, data = None):
		if data:
			return self.set(data)
		else:
			return self.fetch()

	def set(self, data = None):
		self.data = data
		self.save()
		return self

	def save(self):
		print "presave"
		pickle.dump(self.data, open(self.filename, 'wb'), pickle.HIGHEST_PROTOCOL)
		print "postsave", self.filename
		if Ressource.memcache:
			Ressource.memcache.delete(self.filename.encode('utf-8'))
			
	def fetch(self):
		if not self.data:
			if Ressource.memcache:
				self.data = Ressource.memcache.get(self.filename.encode('utf-8'))
			if not self.data:
				try:
					f = open(self.filename, 'rb')
					self.data = pickle.load(f)
					f.close()
				except (IOError, pickle.UnpicklingError):
					print "IOError on file", self.filename
					self.data = None
				if Ressource.memcache:
					Ressource.memcache.set(self.filename.encode('utf-8'), self.data)
		return self.data






class CacheDict(UserDict.DictMixin):
	mc = None
	
	""" Dict that saves each of its values in separate files (pickle) and caches to memcache.
		Used for fast onDemand unpickling of single values instead of loading the full dict every time.
		CacheDict ist pickable itself.
		
		dict[key] += 1 # marks a value to be saved later
		dict[key] = newvalue # marks
		dict[key].append(1) # does not mark the value !!!
		dict.mark(key) # marks explicit
		dict.save() # saves all marked values
		del dict # does a dict.save()
		
		Be careful. Automatic saving only happens on garbage collection (which could be to late).
		"""
		
	def __init__(self, path, prefix = 'cd_', suffix = '.pkl'):
		self.path = path
		self.data = {}
		self.changed = []
		self.prefix = prefix
		self.suffix = suffix
		
	def __len__(self):
		return len(self.data)
	
	def __getitem__(self, key):
		data = self.data[key] # Raises KeyError on error
		if data == None:
			filename = self.filename(key)
			if CacheDict.mc:
				print "memcache get ", filename
				data = CacheDict.mc.get(filename.encode('utf-8'))
			if data == None:
				print "unpickling", filename
				data = pickle.load(open(filename,'rb'))
				print "done"
				if CacheDict.mc:
					CacheDict.mc.set(filename.encode('utf-8'), data)
			if data == None:
				del self.data[key]
			else:
				self.data[key] = data

		return self.data[key]

	def __setitem__(self, key, value):
		self.data[key] = value
		self.changed.append(key)

	def __delitem__(self, key):
		del self.data[key]
		filename = self.filename(key)
		if CacheDict.mc:
			CacheDict.mc.delete(filename.encode('utf-8'))
		os.unlink(filename)

	def __contains__(self, key):
		return (key in self.data)
		
	def keys(self):
		return self.data.keys()
		
	def mark(self, key):
		self.changed.append(key)
		
	def free(self, key):
		if key in self.changed:
			self.save()
		self.data[key] = None
	
	def save(self):
		keys = set(self.changed)
		for key in keys:
			if key in self.data and self.data[key] != None:
				filename = self.filename(key)
				if CacheDict.mc:
					CacheDict.mc.delete(filename.encode('utf-8'))
				pickle.dump(self.data[key], open(filename, 'wb'), pickle.HIGHEST_PROTOCOL)
				print "pickling", filename
		self.changed = []
		
	def __del__(self):
		self.save()
				
	def __getstate__(self):
		emptydict = {}
		for key in self.data.keys():
			emptydict[key] = None
		return {'path': self.path, 'data':emptydict, 'changed':[], 'prefix':self.prefix, 'suffix':self.suffix}

	def cacheto(self, memcache):
		CacheDict.mc = memcache
		
	def filename(self, key):
		return self.path + '/' + self.prefix + key + self.suffix







class Project(object):
	''' Project session with workdir '''
	def __init__(self, workdir):
		self.workdir = workdir
		self.filename = workdir + '/session.pkl'
		self.views = CacheDict(self.workdir, prefix='view_')
		self.ressources = CacheDict(self.workdir, prefix='res_')

	def load(self, inputfile, *kv, **ka):
		""" Imports data with a specific context (file format, import target ...) """
		raise NotImplementedError
		
	def list_views(self):
		""" Returns a list of all available views """
		return self.views.keys()

	def get_view(self, name):
		""" returns a specific view """
		if name in self.views:
			return self.views[name]
		else:
			raise NotImplementedError

	def set_view(self, name, view):
		self.views[name] = view

	def list_res(self):
		""" Returns a list of all available views """
		return self.ressources.keys()

	def get_res(self, name):
		""" returns a specific view """
		if name in self.ressources:
			return self.ressources[name]
		else:
			raise NotImplementedError

	def set_res(self, name, view):
		self.ressources[name] = view






























if config.memcache and memcache:
	mc = memcache.Client(config.memcache, debug=0)
	Ressource.memcache = mc
	CacheDict.mc = mc
else:
	print "ERROR: Could not setup memcache. Module not found. You might want to install it for better performance."




