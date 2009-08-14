import bottle
import sys
from os.path import abspath, join, dirname, basename
from lucullus import base
from lucullus.base import config
import lucullus.base
import cairo
import simplejson
import logging
import mimetypes
import os
import lucullus.plugins.seq
import time
import random

bottle.debug(True)

# create logger
log = logging.getLogger("lucullus")
log.setLevel(logging.DEBUG)
#create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
log.addHandler(ch)
log.debug("Starting server")
sessions = {}
resource_path = abspath(join(dirname(__file__), './data'))
bottle.TEMPLATE_PATH.insert(0,abspath(join(dirname(__file__), './views'))+'/%s.tpl')



"""
Masterplan:
Sessions verschwinden. Connect entfaellt. Es gibt nur noch Resourcen und Views.
Resourcen sind mutable Objekte die komplett gepickelt werden.
Views sind das gleiche, haben aber eine render() methode.

>>> /api/create type(resource), apikey, **args 
<<< {"id": #, "state": {...}, "api": [list-of-api-functions]}
Erschafft eine neue resource

/api/r123456
Wirft statistiken ueber die resource aus, kann jeder machen

/api/r123456/setup apikey
Konfiguriert eine Ressource

/api/r123456/... apikey **args
Ruft eine Methode der resource auf


Nur Views:
/api/r123456/render apikey x y w h f
Rendert ein Bild

"""

apikeys = ['test']
resources = bottle.db.resources


def jsonify(action):
	""" Action Decorator that formats output for JSON

	Given a function that will return content, this decorator will turn
	the result into JSON, with a content-type of 'application/json' and
	output it.
	"""
	def tojson(**kwargs):
		try:
			data = action(**kwargs)
		except Exception, e:
			data = {'error':str(e)}
		log.debug("Jsonify %s" % str(data))
		bottle.response.content_type = 'application/json'
		return simplejson.dumps(data)
	return tojson



@bottle.route('/api/create', method="POST")
@jsonify
def create():
	log.debug(repr(bottle.request.params))
	log.debug(repr(bottle.request.params['apikey']))
	apikey = bottle.request.params.get('apikey','')
	r_type = bottle.request.POST.get('type','txt')
	options = dict(bottle.request.params)
	del options['apikey']
	del options['type']
	
	if apikey not in apikeys:
		bottle.abort(401, 'You have to provide a valid api key')
	if r_type not in lucullus.base.plugins:
		bottle.abort(403, 'The requestet resource type is not available. Please coose from ths list: '+', '.join(lucullus.base.plugins.keys()))	   

	r = lucullus.base.plugins[r_type]()
	r.configure(**options)
	r.touch()
	resources[id(r)] = r
	api = [a[4:] for a in dir(r) if a.startswith('api_') and callable(getattr(r, a))]
	return {"id": str(id(r)), "state": r.state(), "api": api}


@bottle.route('/api/r:rid:[0-9]+:/setup', method='POST')
@jsonify
def configure(rid):
	""" Accesses the resource configuration and functions """
	apikey = bottle.request.params.get('apikey','')
	r = resources.get(int(rid),None)

	if not r:
		bottle.abort(404, 'Resource not found')
	if apikey not in apikeys:
		bottle.abort(401, 'You have to provide a valid api key')

	options = dict(bottle.request.params)
	del options['apikey']

	try:
		r.configure(**options)
		r.touch()
		return {"id": rid, "state": r.state()}
	except base.ResourceError, e:
		return {'id': rid, 'error': repr(e)}


@bottle.route('/api/r:rid:[0-9]+:/:query:[a-z_]+:', method='POST')
@jsonify
def query(rid, query):
	""" Accesses the resource configuration and functions """
	apikey = bottle.request.params.get('apikey','')
	r = resources.get(int(rid),None)

	if not r:
		bottle.abort(404, 'Resource not found')
	if apikey not in apikeys:
		bottle.abort(401, 'You have to provide a valid api key')

	options = dict(bottle.request.params)
	del options['apikey']

	if not r:
		bottle.abort(404, 'Resource not found')
	try:
		answer = r.query(query, **options)
		answer['id'] = rid
		answer['state'] = r.state()
		return answer
	except base.ResourceError, e:
		return {'id': rid, 'error': repr(e)}


@bottle.route('/api/r:rid:[0-9]+:/help', method='GET')
@bottle.route('/api/r:rid:[0-9]+:/help/:query:[a-z_]+:', method='GET')
@jsonify
def help(rid, query=None):
	r = resources.get(int(rid),None)
	if query:
		api = [(a[4:], getattr(r, a).__doc__) for a in [query] if a.startswith('api_') and callable(getattr(r, a))]
	else:
		api = [(a[4:], getattr(r, a).__doc__) for a in dir(r) if a.startswith('api_') and callable(getattr(r, a))]
	return {'api':api}

@bottle.route('/api/r:rid:[0-9]+:')
@jsonify
def info(rid):
	r = resources.get(int(rid),None)
	if not r:
		bottle.abort(404, 'Resource not found')
	return {"id": rid, "state": r.state()}


@bottle.route('/api/r:rid:[0-9]+:/x:x:[0-9]+:y:y:[0-9]+:w:w:[0-9]+:h:h:[0-9]+:\.:f:(png):')
def render(rid, x, y, w, h, f):
	import rfc822
	r = resources.get(int(rid),None)
	if not r:
		bottle.abort(404, 'Resource not found')

	if not isinstance(r, base.BaseView):
		raise bottle.abort(404, "This resource has no visuals")
		
	mode = 'RGB24'

	try:
		x,y,w,h = map(int, (x,y,w,h))
	except:
		bottle.abort(500, "Cannot parse input parameters. Use numeric values for x,y,z,w and h")

	if w < 16 or h < 16 or w > 1024 or h > 1024:
		bottle.abort(500, "Image size to big or to small")
	if f not in ('png'):
		bottle.abort(500, "Image format not supported.")
	if mode not in ('ARGB32', 'RGB24'):
		bottle.abort(500, "Image mode not supported")

	# Send cached file to client
	filename = '/tmp/lucullus/image_%s.mtime%d.x%d.y%d.w%d.h%d.%s.%s' % (rid,int(r.mtime),x,y,w,h,mode,f)

	if not os.path.exists(filename):
		try:
			try: os.makedirs(dirname(filename))
			except OSError: pass
			io = open(filename, "wb")
		except (IOError,OSError):
			log.error("Could not create cache image file %s", filename)
			raise

		if "ARGB32" == mode:
			surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
		else:
			surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)

		context = cairo.Context(surface)
		context.translate(-x, -y)
		try:
			r.render(context, x, y, w, h)
		except Exception, e:
			log.exception("Bad render call")
			raise

		if format == 'png':
			surface.write_to_png(io)
		else:
			surface.write_to_png(io)
		io.close()
		
	bottle.response.content_type = "image/%s" % f
	bottle.response.header['X-Copyright'] = "Max Planck Institut (MPIBPC Goettingen) Marcel Hellkamp"
	bottle.response.header['Expires'] = rfc822.formatdate(time.time() + 60*60*24)
	bottle.send_file(filename=basename(filename), root=dirname(filename))


@bottle.route('/')
def index():
	return bottle.template('seqgui')

@bottle.route('/:filename:(js|css|test)/.+:')
def static(filename):
	bottle.send_file(filename=filename, root=resource_path + '/static_files')

def serve():
	bottle.run(server=bottle.PasteServer, host='0.0.0.0', port=8080)
	return 0
	
if __name__ == '__main__':
	sys.exit(serve())