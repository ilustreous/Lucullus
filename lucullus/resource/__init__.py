import cPickle as pickle
import inspect
import time
import os.path

class ResourceError(Exception): pass
class ResourceNotFound(ResourceError): pass
class ResourceTypeNotFound(ResourceError): pass
class ResourceUploadError(ResourceError): pass
class ResourceQueryError(ResourceError): pass
class ResourceQueryNoApiError(ResourceQueryError): pass
class ResourceQueryOptionsError(ResourceQueryError): pass

class Pool(object):
    """docstring for ResourceManager"""
    def __init__(self, savepath):
        self.savepath = savepath
        self.plugins = dict()
        self.db = dict()

    def install(self, name, cls):
        ''' Install a plugin '''
        if not isinstance(cls, type):
            raise TypeError('Plugin must be a class.')
        if not issubclass(cls, BaseResource):
            raise TypeError('Plugin must implement BaseResource.')
        if name in self.plugins:
            raise TypeError('Plugin name no unique.')
        self.plugins[name] = cls

    def install_all(self, module):
        ''' Install all plugins from a module '''
        if not inspect.ismodule(module):
            module = __import__(module)
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if isinstance(cls, BaseResource):
                self.install(name, cls)

    def create(self, plugin, **options):
        ''' Create a new resource '''
        if plugin not in self.plugins:
            raise ResourceTypeNotFound('Plugin %s not available' % plugin)
        r = self.plugins[plugin](pool=self)
        r.configure(**options)
        rid = id(r)
        while rid in self.db or os.path.exists(os.path.join(self.savepath, "%d.res" % rid)): 
            rid += 1
        self.db[rid] = r
        r.id = rid
        r.touch()
        return r

    def cleanup(self, timeout=60*60):
        ''' Purge resources than timeout in seconds '''
        for x in self.db.keys():
            try:
                if isinstance(self.db[x], BaseResource) and self.db[x].atime < time.time() - timeout:
                    self.purge(x)
            except KeyError:
                pass

    def purge(self, rid):
        ''' Purge a resource '''
        r = self.db.get(rid, None)
        if r and isinstance(r, BaseResource):
            fname = os.path.join(self.savepath, "%d.res" % rid)
            with open(fname, 'wb') as f:
                r.touch()
                pickle.dump(r, f, -1)
            self.db[rid] = (r.__class__, r.atime, fname)

    def fetch(self, rid, *a):
        ''' Load a resource '''
        r = self.db.get(rid, None)
        if isinstance(r, BaseResource):
            return r
        path = os.path.join(self.savepath, "%d.res" % rid)
        if os.path.exists(path):
            r = pickle.load(path)
            self.db[rid] = r
            r.id = rid
            r.touch()
            return r
        if a:
            return a[0]            
        raise ResourceNotFound("Resource %d not found in %s" % (rid, self.savepath))






class BaseResource(object):
    """ An empty cache-, pick- and saveable data container bound to a session. """
    def __init__(self, pool):
        self.mtime = time.time()
        self.atime = time.time()
        self.resource_pool = pool
        self.prepare()
        self.api = [c[4:] for c in dir(self) if c.startswith('api_') and callable(getattr(self, c))]
        self.id = -1

    def state(self):
        """ Should return a dict with some infos about this resource """
        return {'mtime':self.mtime, 'atime':self.atime, 'api':self.api, 'id':self.id}

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
            raise ResourceQueryNoApiError("Resource %s does not implement %s()" % (self.__class__.__name__, name))
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
            raise ResourceQueryOptionsError('Missing arguments: %s' % ','.join(missing))
        unknown = provided - available
        if unknown and not twostar:
            raise ResourceQueryOptionsError('Unknown arguments: %s' % ','.join(unknown))
        self.touch(False)
        return c(**options)






class BaseView(BaseResource):
    def size(self):
        """ Should return the absolute size of the drawable area in pixel. """
        return (0,0)

    def offset(self):
        """ Should return the (x,y) offset of the drawable area in pixel. """
        return (0,0)

    def state(self):
        state = super(BaseView, self).state()
        w, h = self.size()
        ox, oy = self.offset()
        state.update({'width':w, 'height':h, 'offset':[ox, oy], 'size':[w, h]})
        return state

    def render(self, ra):
        """ Renders into a RenderArea cairo context. """
        pass
