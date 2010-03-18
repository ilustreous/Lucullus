import os, os.path
import time
import rfc822
import bottle
from bottle import HTTPResponse, HTTPError, route, validate
import logging
import lucullus.render
import lucullus.render.geometry
import lucullus.resource

log = logging.getLogger("lucullus")

cfg = dict()
cfg['path.base'] = os.path.abspath(os.path.dirname(__file__))
cfg['path.views'] = os.path.join(cfg['path.base'], 'views')
cfg['path.db'] = os.path.join('/tmp')
cfg['path.static'] = os.path.join(cfg['path.base'], 'static')
cfg['api.strip'] = ''
cfg['api.keys'] = ['test']
cfg['debug'] = False

bottle.TEMPLATE_PATH.insert(0, cfg['path.views'])

rdb = lucullus.resource.Pool(cfg['path.db'])

err = dict()
err['no key'] = 'You have to provide a valid api key'
err['unknown type'] = 'The requestet resource type is not available.'
err['no resource'] = 'The requested resource could not been found.'
err['setup error'] = 'Resource setup failed'
err['query error'] = 'Resource query failed'

bottle.app.push()

def config(**config):
    for key in config:
        if '_' in key:
            config[key.replace('_','.')] = config[key]
            del config[key]
    cfg.update(config)
    if 'path.db' in config:
        rdb.savepath = cfg['path.db']
        if not os.path.exists(rdb.savepath):
            os.makedirs(rdb.savepath)
        log.debug("Ressource path: %s", rdb.savepath)
    if 'api.strip' in config:
        wsgi.rootpath = cfg['api.strip']
    if 'path.views' in config:
        bottle.TEMPLATE_PATH.insert(0, cfg['path.views'])
        log.debug("Template path: %s", bottle.TEMPLATE_PATH)

def load_plugin(path):
    rdb.install_module(path)

def start(*a, **k):
    log.info("Starting server: %s", repr((a, k)))
    bottle.run(app=wsgi, *a, **k)

def apierr(code, **args):
    args['error'] = code
    if 'detail' not in args:
        args['detail'] = err.get(code, 'Undocmented error')
    log.warning("API error: %s" % repr(args))
    raise bottle.HTTPResponse(args)


def needs_apikey(func):
    def wrapper(*a, **ka):
        key = bottle.request.POST.get('apikey', None)
        if key not in cfg['api.keys']:
            apierr('no key')
        del bottle.request.POST['apikey']
        return func(*a, **ka)
    return wrapper


def needs_ressource(func):
    def wrapper(*a, **ka):
        r = rdb.fetch(int(ka['rid']), None)
        if not r:
            return apierr('no resource', id=rid)
        del ka['rid']
        ka['ressource'] = r
        return func(*a, **ka)
    return wrapper


@route('/api/create', method="POST")
@needs_apikey
def create():
    rdb.cleanup(60*60)
    options = dict(bottle.request.POST)
    r_type = options.get('type', 'txt')
    if 'type' in options:
        del options['type']
    try:
        r = rdb.create(r_type)
        if options:
	        r.setup(**options)
    except lucullus.resource.ResourceTypeNotFound:
        apierr('unknown type', types=rdb.plugins.keys())
    except lucullus.resource.ResourceSetupError, e:
        apierr('setup error', id=rid, detail=e.args[0])
    return {"id": r.id, "state": r.getstate(), "methods": r.getapi()}


@route('/api/r:rid#[0-9]+#/setup', method='POST')
@needs_apikey
@needs_ressource
def setup(ressource):
    """ Accesses the resource configuration and functions """
    options = dict(bottle.request.POST)
    try:
        ressource.setup(**options)
        return {"id": ressource.id, "state": ressource.getstate()}
    except lucullus.resource.ResourceSetupError, e:
        return apierr('setup error', id=ressource.id, detail=e.args[0])


@route('/api/r:rid#[0-9]+#/:query#[a-z_]+#', method='POST')
@needs_apikey
@needs_ressource
def query(ressource, query):
    """ Accesses the resource configuration and functions """
    options = dict(bottle.request.POST)
    response = dict(id=ressource.id)
    response['request'] = query
    response['options'] = options
    try:
        response['result'] = ressource.query(query, **options)
        response['state'] = ressource.getstate()
        return response
    except lucullus.resource.ResourceQueryError, e:
        response['detail'] = e.args[0]
        return apierr('query error', **response)


@route('/api/r:rid#[0-9]+#/help', method='GET')
@route('/api/r:rid#[0-9]+#/help/:query#[a-z_]+#', method='GET')
@needs_apikey
@needs_ressource
def help(ressource, query=None):
    api = ressource.getapi()
    if query:
        if query in api:
            doc = getattr(ressource, "api_%s"%s).__doc__ or 'Undocumented'
            return dict(id=ressource.id, query=query, help=doc)
        else:
            return apierr('query error', id=ressource.id, detail='Undefined')
    return {'id': ressource.id, 'api':api.keys}


@route('/api/r:rid#[0-9]+#')
@needs_ressource
def info(rid):
    r = rdb.fetch(int(rid),None)
    if not r:
        return HTTPError(404, 'Resource not found')
    return {"id": rid, "state": r.state()}


@route('/api/r:rid#[0-9]+#/:channel#[a-z]+#-:x#[0-9]+#-:y#[0-9]+#-:w#[0-9]+#-:h#[0-9]+#.:format#png#')
@validate(x=int, y=int, w=int, h=int)
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
    if not os.path.exists(filename) or cfg['debug']:
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
    bottle.response.headers['X-Copyright'] = "Max Planck Institut (MPIBPC Goettingen) Marcel Hellkamp"
    bottle.response.headers['X-CPUTIME'] = "render: %f all: %f" % (time.time() - ts2, time.time() - ts)
    bottle.response.headers['Expires'] = rfc822.formatdate(time.time() + 60*60*24)
    return bottle.static_file(filename=os.path.basename(filename), root=os.path.dirname(filename), mimetype="image/%s" % format)


@route('/')
def index():
    return bottle.template('seqgui')


@route('/:filename#(img|js|jquery|css|test)/.+#')
def static(filename):
    return bottle.static_file(filename=filename, root=cfg['path.static'])


@route('/clean')
def cleanup():
    rdb.cleanup(10)
    return "done"

wsgi = bottle.app.pop()