import cairo
import math
from lucullus.render.geometry import Area
from lucullus.render.color import pick as colorpick

class Target(object):
    """
        Represents a single render area (AOI: Area of Interest) and provides
        georemtry and cairo helper methods. This is passed to plugins on a 
        BaseView.render() call.
    """
    def __init__(self, area, format='png'):
        assert isinstance(area, Area)
        self.area = area
        self.format = format.lower()
        self._surface = None
        self._context = None

    @property
    def surface(self):
        """ A cairo surface """
        if not self._surface:
            if self.format in ('png'):
                self._surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                self.area.width, self.area.height)
            else:
                raise NotImplementedError("Format %s is not supported." %
                                          self.format)
        return self._surface

    @property
    def context(self):
        """ A cairo context translated to the AOI position """
        if not self._context:
            self._context = cairo.Context(self.surface)
            self._context.translate(-self.area.left, -self.area.top)
        return self._context

    def save(self, io):
        """ Renderes image to a byte stream """
        if self.format == 'png':
            self.surface.write_to_png(io)
        else:
            raise NotImplementedError("Format %s is not supported." %
                                      self.format)

    def clear(self, color='white'):
        """ Clears the image (color fill) """
        self.set_color(color)
        self.context.paint()

    def set_color(self, color):
        """ Clears the image (color fill) """
        c = colorpick(color)
        if c:
            self.context.set_source_rgba(*c)

    def draw_stripes(self, width=100, c1='white', c2='gray'):
        '''Rendert einen gestreiften Hintergrund'''
        context = self.context
        area = self.area
        # Compute start color
        c = (c1, c2)
        ci = int(math.floor(float(area.left) / width))
        offset = - (area.left % width)
        while offset < area.width:
            self.set_color(c[ci%2])
            context.rectangle(area.left+offset, area.top, width, area.height)
            context.fill()
            offset += width
            ci += 1