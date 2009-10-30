#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Marcel Hellkamp on 2008-08-20.
Copyright (c) 2008 Marcel Hellkamp. All rights reserved.
"""

import cPickle as pickle
import UserDict
from lucullus.base import config, color
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
import glob

class PluginError(Exception): pass
class PluginNotFoundError(PluginError):pass

class ResourceError(Exception): pass
class ResourceNotFound(ResourceError): pass
class ResourceUploadError(ResourceError): pass
class ResourceQueryError(ResourceError): pass
class ResourceQueryNoApiError(ResourceQueryError): pass
class ResourceQueryOptionsError(ResourceQueryError): pass


""" Geometry and cairo Helper
"""

class GeometryError(Exception): pass

class RenderContext(object):
    """
        Represents a single render area (AOI: Area of Interest) and provides
        georemtry and cairo helper methods. This is passed to plugins on a 
        BaseView.render() call.
    """
    def __init__(self, top=0, left=0, width=256, height=246, format='png'):
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.format = format.lower()
        self._surface = None
        self._context = None

    @property
    def bottom(self): return self.top + self.height
    @property
    def right(self): return self.left + self.width
    @property
    def x(self): return self.left
    @property
    def y(self): return self.top
    @property
    def x1(self): return self.left
    @property
    def y1(self): return self.top
    @property
    def x2(self): return self.right
    @property
    def y2(self): return self.bottom
    @property
    def offset(self): return (self.left, self.top)
    @property
    def area(self): return (self.left, self.top, self.right, self.bottom)

    @property
    def surface(self):
        """ A cairo surface """
        if not self._surface:
            if self.format in ('png'):
                self._surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                self.width, self.height)
            else:
                raise NotImplementedError("Format %s is not supported." %
                                          self.format)
        return self._surface

    @property
    def context(self):
        """ A cairo context translated to the AOI position """
        if not self._context:
            self._context = cairo.Context(self.surface)
            self._context.translate(-self.left, -self.top)
        return self._context

    def test_point(self, x, y):
        """ Test if a point is visible """
        return self.left <= x <= self.wight \
           and self.top <= y <= self.bottom
    
    def test_rectangle(self, left, top, right, bottom):
        """ Test if a rectangle is visible (full or partly) """
        return self.top < bottom and self.bottom > top \
           and self.left < right and self.right > left

    def intersect(self, left, top, right, bottom):
        """ Return the visible part of a rectangle """
        if self.test_area(left, top, right, bottom):
            return max(self.top, top), max(self.left, left), \
                   min(self.bottom, bottom), min(self.right, right)
        else:
            raise GeometryError("Rectangles do not intersect")

    def save(self, io):
        """ Renderes image to a byte stream """
        if self.format == 'png':
            self.surface.write_to_png(io)
        else:
            raise NotImplementedError("Format %s is not supported." %
                                      self.format)

    def clear(self, r=1.0, g=1.0, b=1.0, a=1.0):
        """ Clears the image (color fill) """
        self.set_color(r, g, b, a)
        self.context.paint()
        
    def set_color(self, r=1.0, g=1.0, b=1.0, a=1.0):
        """ Clears the image (color fill) """
        self.context.set_source_rgba(r, g, b, a)


class ResourceManager(object):
    """docstring for ResourceManager"""
    def __init__(self, savepath):
        super(ResourceManager, self).__init__()
        self.savepath = savepath
        self.plugins = dict()
        self.db = dict()

    def add_plugin(self, name, cls):
        if not isinstance(cls, type):
            cls = cls.__class__
        if not issubclass(cls, BaseResource):
            raise AttributeError('Resources must implement BaseResource.')
        if name not in self.plugins:
            self.plugins[name] = cls

    def create(self, name, **options):
        if name not in self.plugins:
            raise PluginNotFoundError('Plugin %s not available' % name)
        r = self.plugins[name]()    
        r.configure(**options)
        rid = id(r)
        while rid in self.db or os.path.exists(os.path.join(self.savepath, "%d.res" % rid)): 
            rid += 1
        self.db[rid] = r
        r.id = rid
        r.touch()
        return r

    def cleanup(self, timeout=60*60):
        for x in self.db.keys():
            try:
                if isinstance(self.db[x], BaseResource)and self.db[x].atime < time.time() - timeout:
                    self.purge(x)
            except KeyError:
                pass

    def purge(self, rid):
        r = self.db.get(rid, None)
        if r and isinstance(r, BaseResource):
            fname = os.path.join(self.savepath, "%d.res" % rid)
            with open(fname, 'wb') as f:
                r.touch()
                pickle.dump(r, f, -1)
            self.db[rid] = (r.__class__, r.atime, fname)

    def fetch(self, rid, *a):
        r = self.db.get(rid, os.path.join(self.savepath, "%d.res" % rid))
        if isinstance(r, BaseResource):
            return r
        elif os.path.exists(r):
            r = pickle.load(r)
            self.db[rid] = r
            r.id = rid
            r.touch()
            return r
        elif a: return a[0]            
        else: raise ResourceNotFound("Resource %d not found in %s" % (rid, self.savepath))






class BaseResource(object):
    """ An empty cache-, pick- and saveable data container bound to a session. """
    def __init__(self):
        self.mtime = time.time()
        self.atime = time.time()
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
    
    def __init__(self, *l, **d):
        super(BaseView, self).__init__(*l, **d)

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





class IndexView(BaseView):
    def prepare(self, **options):
        self.fontsize = 12 
        self.index = []
        self.color = {}
        self.color['fontcolor'] = color.get('css','black')

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
        self.touch()

    def render(self, rc):
        # Shortcuts
        c = rc.context

        # Configuration
        c.select_font_face("mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        options = cairo.FontOptions()
        #fo.set_hint_metrics(cairo.HINT_METRICS_ON)
        #fo.set_hint_style(cairo.HINT_STYLE_NONE)
        options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        c.set_font_options(options)
        c.set_font_size(self.fontsize - 1)
        real_lineheight = c.font_extents()[1]

        # Rows to consider
        row_first = int(math.floor(float(rc.top) / self.fontsize))
        row_last  = int(math.ceil(float(rc.bottom) / self.fontsize))
        row_last  = min(row_last, len(self.index)-1)

        # Fill the background with #ffffff
        rc.clear(*self.color.get('background',(1,1,1,1)))
        if self.fontsize <= 6: return self #No need to render text
        rc.set_color(*self.color.get('fontcolor',(0,0,0,1)))
        font_extends = c.font_extents()

        for row in range(row_first, row_last+1):
            name = self.index[row]
            y = self.fontsize * row + self.fontsize - font_extends[1]
            x = 0
            c.move_to(x, y)
            c.show_text(name)

        return self


class RulerView(BaseView):
    def prepare(self):
        self.marks      = 1
        self.digits     = 10
        self.fontsize   = 12
        self.color = {}
        self.color['fontcolor'] = color.get('css','white')

    def configure(self, **options):
        self.marks      = int(options.get('marks', self.marks))
        self.digits     = int(options.get('digits', self.digits))
        self.fontsize   = int(options.get('fontsize', self.fontsize))
        self.touch()

    def size(self):
        return (2**32, self.fontsize + 5)
        
    def offset(self):
        return (0,0)

    def render(self, rc):
        c = rc.context

        first = rc.left - rc.left % self.fontsize
        last = rc.right + rc.right % self.fontsize
        rc.clear(*color.get('css','white'))

        fo = cairo.FontOptions()
        fo.set_hint_metrics(cairo.HINT_METRICS_ON)
        fo.set_hint_style(cairo.HINT_STYLE_NONE)
        fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        c.set_font_options(fo)
        c.set_font_size(self.fontsize)
        font_extends = c.font_extents()

        rc.set_color(*color.get('css', 'black'))
        if self.fontsize > 6:
            for mark in xrange(first - self.fontsize*self.digits, last + self.fontsize*self.digits, self.fontsize):
                if (mark % (self.fontsize * self.digits)) == 0:
                    name = str(mark / self.fontsize)
                    text_width, text_height = c.text_extents(name)[2:4]
                    c.move_to(mark - text_width/2, font_extends[3])
                    c.show_text(name)

        for mark in xrange(first, last, self.fontsize):
            if (mark % (self.fontsize * self.marks)) == 0:
                c.rectangle(mark, font_extends[3]+4, 1, rc.height)
            if (mark % (self.fontsize * self.digits)) == 0:
                c.rectangle(mark, font_extends[3]+2, 2, rc.height)
            c.fill()

        return self


