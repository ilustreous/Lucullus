import bottle
from os.path import abspath, join, dirname, basename
from lucullus import base
from lucullus.base import Session, config
import lucullus.base
import cairo
import simplejson
import logging
import mimetypes
import os
import lucullus.plugins.seq
import time

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

def jserror(msg, **data):
    data['error'] = msg
    return data



def jsonify(action):
    """ Action Decorator that formats output for JSON

    Given a function that will return content, this decorator will turn
    the result into JSON, with a content-type of 'application/json' and
    output it.
    """
    def tojson(**kwargs):
        data = action(**kwargs)
        log.debug("Jsonify %s" % str(data))
        bottle.response.content_type = 'application/json'
        return simplejson.dumps(data)
    return tojson



def with_session(action):
    """ Action Decorator that requies a valid session and stores it in request.session
    """
    def getsession(**kwargs):
        if "sid" in kwargs:
            s = kwargs['sid']
            del kwargs['sid']
        else:
            s = bottle.request.POST.get("sid", None)
        if s:
            s = sessions.get(s, None)
        if s:
            s.touch(False)
            bottle.request.session = s
            return action(**kwargs)
        else:
            log.debug("Session %s not found" % s)
            bottle.abort(401, 'Valid session requied')
    return getsession



def with_resource(action):
    def getresource(**kwargs):
        if not hasattr(bottle.request, 'session'):
            raise itty.Forbidden('Valid session requied')
        if "rid" in kwargs:
            r = kwargs['rid']
            del kwargs['rid']
        else:
            r = bottle.request.POST.get("rid", None)
        if r:
            r = bottle.request.session.get_resource(r, None)
        if r:
            bottle.request.resource = r
            r.touch(True)
            return action(**kwargs)
        else:
            bottle.abort(401, 'Valid resource requied for this action')
    return getresource



@bottle.route('/api/connect', method='POST')
@jsonify
def connect():
    """ Creates a new session and returns a session id and a list of available plugins."""
    sess = Session(config.savepath)
    sessions[sess.id] = sess
    return {'session': sess.id, 'plugins':sess.plugins.keys()}


@bottle.route('/api/:sid:[a-f0-9]{32}:/create', method='POST')
@jsonify
@with_session
def upload():
    filename = bottle.request.POST.get("name", None)
    filetype = bottle.request.POST.get("type", None)
    session = bottle.request.session

    if not filetype or filetype not in session.plugins:
        return jserror('Resource type not available.', plugins=session.plugins.keys())

    resource = session.new_resource(filetype, filename)
    mets = [a[4:] for a in dir(resource) if a.startswith('api_') and callable(getattr(resource, a))]
    log.debug("Created resource %s for session %s", resource.id, bottle.request.session.id)

    return {'session': session.id, 'resource': resource.id, 'type':type(resource).__name__, 'apis':mets, 'status':resource.status()}



@bottle.route('/api/:sid:[a-f0-9]{32}:/:rid/:query', method='POST')
@jsonify
@with_session
@with_resource
def query(query):
    """ Accesses the resource configuration and functions """
    try:
        params = dict(bottle.request.POST)
        params.update(dict(bottle.request.GET))
        result = bottle.request.session.query_resource(bottle.request.resource.id, query, params)
    except base.ResourceError, e:
        return jserror(e.message)
    return {"session":bottle.request.session.id, "resource":bottle.request.resource.id, "result":result, "status":bottle.request.resource.status()}



@bottle.route('/api/:sid:[a-f0-9]{32}:/:rid/x:x:[0-9]+:y:y:[0-9]+:w:w:[0-9]+:h:h:[0-9]+:\.:f:(png):')
@with_session
@with_resource
def render(x, y, w, h, f):
    import rfc822

    if not isinstance(bottle.request.resource, base.BaseView):
        raise itty.AppError("This resource has no visuals")
        
    mode = 'RGB24'

    try:
        x,y,w,h = map(int, (x,y,w,h))
    except:
        raise itty.AppError("Cannot parse input parameters. Use numeric values for x,y,z,w and h")

    if w < 16 or h < 16 or w > 1024 or h > 1024:
        raise itty.AppError("Image size to big or to small")
    if f not in ('png'):
        raise itty.AppError("Image format not supported.")
    if mode not in ('ARGB32', 'RGB24'):
        raise itty.AppError("Image mode not supported")

    # Send cached file to client
    filename = bottle.request.session.workpath + '/image_%s.mtime%d.x%d.y%d.w%d.h%d.%s.%s' % (bottle.request.resource.id,int(bottle.request.resource.mtime),x,y,w,h,mode,f)

    if not os.path.exists(filename):
        try:
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
            bottle.request.resource.render(context, x, y, w, h)
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
    return '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <script src="./js/jquery.js" type="text/javascript"></script>
        <script src="./js/jquery.query.js" type="text/javascript"></script>
        <script src="./js/lucullus.js"   type="text/javascript"></script>
        <script src="./js/lucullus.seqgui.js"   type="text/javascript"></script>
        <title>Lucullus</title>
        <style type="text/css">
            html {background-color:#fff}
            #mySeqMap {background-color:#eee}
        </style>
    </head>
    <body>
        <div id="debug"></div>
        <div id="seqgui">
            <form class='upload' style="background: lightgrey;
                                        border: 5px solid grey;
                                        position: absolute; top:50%; left:50%;
                                        height:100px; width:400px; padding:14px;
                                        margin:-65px -215px;
                                        -moz-border-radius: 10px 10px;
                                        overflow:hidden">
                <div style="font-weight: bold; border-bottom: 1px solid grey; margin-bottom:5px">Upload a fasta File</div>
                <label for="upUrl">URL:</label> <input type="text" name="upUrl" style="width: 50%" /> <input type="submit" value="Upload"/><br />
                <label for="format">Format:</label>
                <select name="format">
                    <option value="fasta">Fasta</option>
                </select>
                <select name="pack">
                    <option value="none">Not compressed</option>
                    <option value="gz">gzip</option>
                    <option value="rar">rar</option>
                    <option value="zip">zip</option>
                </select>
                <div style="color:red" class="status"></div>
            </form>
            <table class="guitable" style="height:500px; width: 90%; margin: auto; border: 1px solid grey; border-spacing:0px; border-collapse:collapse">
                <tr class="control" style="height:20px">
                    <td class="logo" style="width: 100px"></td>
                    <td class="ruler"></td>
                </tr>
                <tr class="compare" style="height:14px">
                    <td class="index"></td>
                    <td class="map"></td>
                </tr>
                <tr class="main">
                    <td class="index"></td>
                    <td class="map"></td>
                </tr>
                <tr class="status" style="height:20px">
                    <td colspan='2' class="text" style="border: 1px solid grey">Please activate JavaScript.</td>
                </tr>
            </table>
      </div>
        <script type="text/javascript">
          /*<![CDATA[*/
        var autoload = jQuery.query.get('upUrl')
        var server = document.location.protocol + '//' + document.location.host + document.location.pathname + 'api'
        var api
        var gui

        /* api calls are blocking. Never call them in main thread */
        $(document).ready(function() {
            api = new Lucullus.api(server, "nokey")
            gui = new SeqGui(api, '#seqgui')
            api.connect().wait(function() {
                if(autoload)
                    gui.upload(autoload, 'fasta')
            })
        })

        /*]]>*/</script>
    </body>
    </html>
    '''

# To serve static files, simply setup a standard @get method. You should
# capture the filename/path and get the content-type. If your media root is
# different than where your ``itty.py`` lives, manually setup your root
# directory as well. Finally, use the ``static_file`` handler to serve up the
# file.
@bottle.route('/:filename:(js|css|test)/.+:')
def static(filename):
    bottle.send_file(filename=filename, root=resource_path + '/static_files')


import sys, traceback
@bottle.error(500)
def fuck(exception):
    log.error(str(exception))
    log.debug(traceback.format_exc())
    return "Internal server error"


def serve():
    bottle.run(server=bottle.PasteServer, host='0.0.0.0', port=8080)
    return 0
    
if __name__ == '__main__':
    print bottle.ROUTES_SIMPLE, bottle.ROUTES_REGEXP
    for x in bottle.ROUTES_REGEXP["POST"]:
        print x[0].pattern
    sys.exit(serve())