import logging
import random
import hashlib
import os, os.path
import urllib2
import time
import inspect
import cairo

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
from pylons import config as app_config

from lucullus.lib.base import BaseController, template
from lucullus.lib import pyseq
from lucullus.lib.pyseq import config
import lucullus.lib.pyseq.plugin_seq
#import lucullus.lib.pyseq.plugin_phb

g = app_config['pylons.app_globals']
log = logging.getLogger(__name__)

		
"""
Server API
==========
- Sessions sind Arbeitsumgebungen eines Benutzers und halten Infos zu belegten Ressourcen und deren Abhaengigkeiten
- Resourcen halten Daten und koennen sie manipulieren
- Views sind besondere resourcen, die Bilder rendern koennen.

Die urls sind 

http://server.tld/api_path/[action]
http://server.tld/api_path/[session]/[action]
http://server.tld/api_path/[session]/[resource]/[action]

"""

def global_session_get(sid):
	""" Returns session and resource instances, if available """
	session = g.sessions.get(sid,None)
	session.touch(False)
	return session

def global_session_set(session):
	""" Returns session ans resource instances, if available """
	g.sessions[session.id] = session

def jserror(msg, **data):
	data['error'] = msg
	return data






class ApiController(BaseController):

	def __before__(self, *k, **o):
		self.session = None
		self.resource = None
		self.sid = o.get('sid', request.params.get("sid", None))
		self.rid = o.get('rid', request.params.get("rid", None))
		
		if self.sid != None:
			self.session = g.sessions.get(self.sid,None)
			if self.session:
				self.session.touch(False)
				if self.rid != None:
					self.resource = self.session.get_resource(self.rid)

	@jsonify
	def connect(self):
		""" Creates a new session and returns a session id"""
		try:
			s = pyseq.Session(config.savepath)
			global_session_set(s)
			return {'session': s.id, 'plugins':pyseq.plugins.keys()}
		except IOError:
			return jserror('Server error. Please try again later')



	@jsonify
	def create(self):
		""" Creates a new (empty) resource. """
		format = request.params.get("type", None)
		name = request.params.get("name", None)
		
		if not format or format not in pyseq.plugins:
			return jserror('Resource type not available.', plugins=pyseq.plugins.keys())

		if not self.session:
			return jserror('Session expired or invalid. Create a new session first.')

		try:
			cls = pyseq.plugins[format]
			resource = self.session.new_resource(cls, name)
			mets = [a[4:] for a in dir(resource) if a.startswith('api_') and callable(getattr(resource, a))]
			log.debug("Created resource %s for session %s", resource.id, self.session.id)
		except Exception, e:
			return jserror('Unhandled Exception %s' % e.__class__.__name__, detail=e.args)

		return {'session': self.session.id, 'resource': resource.id, 'type':type(resource).__name__, 'apis':mets, 'status':resource.status()}



	@jsonify
	def query(self, query):
		""" Accesses the resource configuration and functions """
		if not self.session:
			return jserror('Session expired or invalid. Create a new session first.')

		if not self.resource:
			return jserror('Unknown resource "%s" for session "%s"' % (self.rid, self.sid))

		options = dict(request.params)

		try:
			c = self.resource.getApiMethod(query)
		except (AttributeError), e:
			return jserror('Resource does not implement %s()' % query)
		
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
			return jserror('Missing arguments: %s' % ','.join(missing))
		unknown = provided - available
		if unknown and not twostar:
			return jserror('Unknown arguments: %s' % ','.join(unknown))
		
		try:
			result = c(**options)
			return {"session":self.session.id, "resource":self.resource.id, "result":result, "status":self.resource.status()}
		except pyseq.ResourceQueryError, e:
			return jserror('%s' % e.args[0])
		except Exception, e:
			return jserror('Query failed badly: %s' % e.args)



	def export(self):
		if not self.resource:
			if not self.session:
				return abort(404, 'Session expired or invalid. Create a new session first.')
			else:
				return abort(404, 'Unknown resource %s for session %s' % (rid, sid))

		options = dict(request.params)
		return self.resource.export(**options)



	def render(self, sid, rid):
		import rfc822

		if not self.resource:
			if not self.session:
				return abort(404, 'Session expired or invalid. Create a new session first.')
			else:
				return abort(404, 'Unknown resource %s for session %s' % (rid, sid))

		if not isinstance(self.resource, pyseq.BaseView):
			return abort(500, "This resource has no visuals")
		
		x = request.params.get("x",0)
		y = request.params.get("y",0)
		w = request.params.get("w",256)
		h = request.params.get("h",256)
		f = request.params.get("f",'png')
		mode = request.params.get("mode",'RGB24')

		try:
			x,y,w,h = map(int, (x,y,w,h))
		except:
			return abort(500, "Cannot parse input parameters. Use numeric values for x,y,z,w and h")

		if w < 16 or h < 16 or w > 1024 or h > 1024:
			return abort(500, "Image size to big or to small")

		if f not in ('png'):
			abort(500, "Image format not supported.")
			
		if mode not in ('ARGB32', 'RGB24'):
			return abort(500, "Image mode not supported")

		# Send cached file to client
		filename = self.session.workpath + '/image_%s.mtime%d.x%d.y%d.w%d.h%d.%s.%s' % (self.resource.id,int(self.resource.mtime),x,y,w,h,mode,f)

		if not os.path.exists(filename) or config.debug:
			# Image not cached. Render new one
			try:
				io = open(filename, "wb")
			except (IOError,OSError):
				log.error("Could not create cache image file %s", filename)
				return abort(500, "Server file system error. Please try again later")

			if "ARGB32" == mode:
				surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
			else:
				surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)

			context = cairo.Context(surface)
			context.translate(-x, -y)
			try:
				self.resource.render(context, x, y, w, h)
			except Exception, e:
				log.exception("Bad render call")
				return abort(500, "Rendering failed.")

			if format == 'png':
				surface.write_to_png(io)
			else:
				surface.write_to_png(io)
			io.close()
		
		response.headers['Content-Type'] = "image/%s" % f
		response.headers['X-Copyright'] = "Max Planck Institut (MPIBPC Goettingen) Marcel Hellkamp"
		response.headers['Expires'] = rfc822.formatdate(time.time() + 60*60*24)
		return open(filename)









