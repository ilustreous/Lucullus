import logging
import random
import hashlib
import os, os.path
import urllib2
import time
import inspect

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
from pylons import config as app_config

from lucullus.lib.base import BaseController, template
from lucullus.lib import pyseq
from lucullus.lib.pyseq import config
import lucullus.lib.pyseq.plugin_seq
import lucullus.lib.pyseq.plugin_phb

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
	""" Returns session ans resource instances, if available """
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
	def create(self, sid):
		""" Creates a new (empty) resource. """
		
		if not sid:
			return jserror('Session key missing.')

		session = global_session_get(sid)
		if not session:
			return jserror('Session expired or invalid. Create a new session first.')

		format = request.params.get("type", None)
		if not format or format not in pyseq.plugins:
			return jserror('Resource type not available.', plugins=pyseq.plugins.keys())

		try:
			cls = pyseq.plugins[format]
			resource = session.new_resource(cls)
			mets = [a[4:] for a in dir(resource) if a.startswith('api_') and callable(getattr(resource, a))]
		except Exception, e:
			return jserror('Unhandled Exception %s' % e.__class__.__name__, detail=e.args)

		return {'session': session.id, 'resource': resource.id, 'type':type(resource).__name__, 'apis':mets, 'status':resource.status()}



	@jsonify
	def query(self, sid, rid, query):
		""" Accesses the resource configuration and functions """
		if not sid:
			return jserror('Session key missing.')

		session = global_session_get(sid)
		if not session:
			return jserror('Session expired or invalid. Create a new session first.')

		if not rid:
			return jserror('Key missing: resource')

		resource = session.get_resource(rid)
		if not resource:
			return jserror('Unknown resource %s for session %s' % (rid, sid))

		action = query
		if not action:
			return jserror('Key missing: action')

		options = dict(request.params)

		try:
			c = getattr(resource, "api_" + action)
		except (AttributeError), e:
			return jserror('Resource does not implement %s()' % action)
		
		# Parameter testing
		provided = set(options.keys())
		available, onestar, twostar, defaults = inspect.getargspec(c)
		available.remove('self')
		print inspect.getargspec(c)
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
		print requied, missing, unknown
		
		try:
			result = c(**options)
			return {"session":session.id, "resource":resource.id, "result":result, "status":resource.status()}
		except pyseq.ResourceQueryError, e:
			return jserror('%s' % e.args[0])
		except Exception, e:
			return jserror('Query failed badly: %s' % e.args)



	def export(self, sid, rid):
		if not sid:
			return abort(404, 'Session key missing.')

		session = global_session_get(sid)
		if not session:
			return abort(404, 'Session expired or invalid. Create a new session first.')

		if not rid:
			return abort(404, 'Key missing: resource')

		resource = session.get_resource(rid)
		if not resource:
			return abort(404, 'Unknown resource %s for session %s' % (rid, sid))

		options = dict(request.params)
		return resource.export(**options)



	def render(self, sid, rid):
		import StringIO
		import rfc822

		if not sid:
			return abort(404, 'Session key missing.')

		session = global_session_get(sid)
		if not session:
			return abort(404, 'Session expired or invalid. Create a new session first.')

		if not rid:
			return abort(404, 'Key missing: resource')

		resource = session.get_resource(rid)
		if not resource:
			return abort(404, 'Unknown resource %s for session %s' % (rid, sid))

		if not isinstance(resource, pyseq.BaseView):
			return abort(500, "This resource has no visuals")
		
		x = request.params.get("x",0)
		y = request.params.get("y",0)
		z = request.params.get("z",0)
		w = request.params.get("w",256)
		h = request.params.get("h",256)
		f = request.params.get("f",'png')

		try:
			x,y,z,w,h = map(int, (x,y,z,w,h))
		except:
			return abort(500, "Cannot parse input parameters. Use numeric values for x,y,z,w and h")

		formats = ('png','jpg')
		if f not in formats:
			return abort(500, "Unknown image format. Use one of: %s" % ', '.join(formats))

		if x < 0 or y < 0:
			return abort(500, "Negative position.")

		if w < 16 or h < 16 or w > 1024 or h > 1024:
			return abort(500, "Image size to big or to small")

		response.headers['Content-Type'] = "image/%s" % f
		response.headers['X-Copyright'] = "Marcel Hellkamp"			
		response.headers['Expires'] = rfc822.formatdate(time.time() + 60*60*24)

		try:
			filename = session.workpath + '/image_%d.mtime%d.x%d.y%d.z%d.w%d.h%d.%s' % (resource.id,int(resource.mtime),x,y,z,w,h,f)
			try:
				if config.debug:
					os.unlink(filename)
				return open(filename)
			except (IOError, OSError):
				f = open(filename, "wb")
				resource.select(x, y, w+z, h+z)
				resource.render(f, w, h)
				f.close()
				return open(filename)
		except (IOError,OSError):
			return abort(500, "Server file system error. Please try again later")

