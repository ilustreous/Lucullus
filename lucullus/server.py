import os, os.path
import time
import rfc822
import bottle
from bottle import route, HTTPError
import logging
import lucullus.render
import lucullus.render.geometry
import lucullus.resource
import lucullus.plugins.base
import lucullus.plugins.seq


log = logging.getLogger("lucullus")
log.debug("Starting server")
sessions = {}
basepath = os.path.abspath(os.path.dirname(__file__))
resource_path = os.path.join(basepath, 'data')
bottle.TEMPLATE_PATH.insert(0,os.path.join(basepath, 'views/'))
log.debug("Template Path: %s", bottle.TEMPLATE_PATH)

apikeys = ['test']
rdb = lucullus.resource.Pool(resource_path)
rdb.install('Sequence', lucullus.plugins.seq.SequenceResource)
rdb.install('Index', lucullus.plugins.base.IndexView)
rdb.install('Ruler', lucullus.plugins.base.RulerView)



@route('/api/create', method="POST")
def create():
    rdb.cleanup(60*60)
    apikey = bottle.request.POST.get('apikey','')
    r_type = bottle.request.POST.get('type','txt')
    options = dict(bottle.request.POST)
    del options['apikey']
    del options['type']
    if apikey not in apikeys:
        return HTTPError(401, 'You have to provide a valid api key')
    try:
        r = rdb.create(r_type, **options)
    except lucullus.resource.ResourceTypeNotFound:
        return HTTPError(403, 'The requestet resource type is not available. Please coose from ths list: '+', '.join(rdb.plugins.keys()))
    return {"id": r.id, "state": r.state(), "methods": r.api}


@route('/api/r:rid#[0-9]+#/setup', method='POST')
def configure(rid):
    """ Accesses the resource configuration and functions """
    if bottle.request.POST.get('apikey','') not in apikeys:
        return HTTPError(401, 'You have to provide a valid api key')
    r = rdb.fetch(int(rid),None)
    if not r:
        return HTTPError(404, 'Resource not found')
    options = dict(bottle.request.POST)
    del options['apikey']
    try:
        r.configure(**options)
        return {"id": r.id, "state": r.state()}
    except lucullus.resource.ResourceError, e:
        return {'id': r.id, 'error': repr(e)}


@route('/api/r:rid#[0-9]+#/:query#[a-z_]+#', method='POST')
def query(rid, query):
    """ Accesses the resource configuration and functions """
    if bottle.request.POST.get('apikey','') not in apikeys:
        return HTTPError(401, 'You have to provide a valid api key')

    r = rdb.fetch(int(rid),None)
    if not r:
        return HTTPError(404, 'Resource not found')

    options = dict(bottle.request.POST)
    del options['apikey']

    if not r:
        return HTTPError(404, 'Resource not found')
    try:
        answer = r.query(query, **options)
        answer['id'] = r.id
        answer['state'] = r.state()
        return answer
    except lucullus.resource.ResourceError, e:
        return {'id': rid, 'error': repr(e)}


@route('/api/r:rid#[0-9]+#/help', method='GET')
@route('/api/r:rid#[0-9]+#/help/:query#[a-z_]+#', method='GET')
def help(rid, query=None):
    r = rdb.fetch(int(rid),None)
    if query:
        api = [(c, getattr(r, "api_"+c).__doc__) for c in [query] if c in r.api]
    else:
        api = [(c, getattr(r, "api_"+c).__doc__) for c in r.api]
    return {'api':api}


@route('/api/r:rid#[0-9]+#')
def info(rid):
    r = rdb.fetch(int(rid),None)
    if not r:
        return HTTPError(404, 'Resource not found')
    return {"id": rid, "state": r.state()}


@route('/api/r:rid#[0-9]+#/:channel#[a-z]+#-:x#[0-9]+#-:y#[0-9]+#-:w#[0-9]+#-:h#[0-9]+#.:format#png#')
@bottle.validate(x=int, y=int, w=int, h=int)
def render(rid, channel, x, y, w, h, format):
    ts = time.time()
    r = rdb.fetch(int(rid), None)
    if not r:
        return HTTPError(404, 'Resource not found')
    if not isinstance(r, lucullus.resource.BaseView):
        return HTTPError(404, "This resource has no visuals")
    try:
        x,y,w,h = map(lambda x: x and int(x) or 0, (x,y,w,h))
    except:
        return HTTPError(500, "Cannot parse input parameters. Use numeric values for x,y,z,w and h")
    if w < 16 or h < 16 or w > 1024 or h > 1024:
        return HTTPError(500, "Image size to big or to small")
    if format not in ('png'):
        return HTTPError(500, "Image format not supported.")
    # Send cached file to client
    filename = '/tmp/lucullus/image_%s_%s_mtime%dx%dy%dw%dh%d.%s' % (rid,channel,int(r.mtime),x,y,w,h,format)
    ts2 = time.time()
    if not os.path.exists(filename):
        area = lucullus.render.geometry.Area(left=x, top=y, width=w, height=h)
        rc = lucullus.render.Target(area=area, format=format)
        try:
            try: os.makedirs(os.path.dirname(filename))
            except OSError: pass
            with open(filename, "wb") as io:
                r.render(rc)
                rc.save(io)
        except (IOError,OSError):
            log.exception("Could not create cache image file %s", filename)
            raise
        except Exception, e:
            log.exception("Rendering failed!")
            raise
    bottle.response.header['X-Copyright'] = "Max Planck Institut (MPIBPC Goettingen) Marcel Hellkamp"
    bottle.response.header['X-CPUTIME'] = "render: %f all: %f" % (time.time() - ts2, time.time() - ts)
    bottle.response.header['Expires'] = rfc822.formatdate(time.time() + 60*60*24)
    return bottle.static_file(filename=os.path.basename(filename), root=os.path.dirname(filename), mimetype="image/%s" % format)


@route('/')
def index():
    return bottle.template('seqgui')


@route('/:filename#(js|jquery|css|test)/.+#')
def static(filename):
    return bottle.static_file(filename=filename, root=resource_path + '/static_files')


@route('/clean')
def cleanup():
    rdb.cleanup(10)
    return "done"