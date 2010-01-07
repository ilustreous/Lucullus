from lucullus.resource import BaseView
import cairo
import math

class IndexView(BaseView):
    def prepare(self, **options):
        self.fontsize = 12 
        self.index = []
        self.fontcolor = 'black'

    def size(self):
        w = max([len(i) for i in self.index] + [0]) * self.fontsize
        h = len(self.index) * self.fontsize
        return (w,h)

    def getstate(self):
        s = super(IndexView, self).getstate()
        s['rows'] = len(self.index)
        return s

    def setup(self, **options):
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
        row_first = int(math.floor(float(rc.area.top) / self.fontsize))
        row_last  = int(math.ceil(float(rc.area.bottom) / self.fontsize))
        row_last  = min(row_last, len(self.index)-1)

        # Fill the background with #ffffff
        rc.clear(color='white')
        if self.fontsize > 6:
            rc.set_color(self.fontcolor)
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
        self.fontcolor = 'black'

    def setup(self, **options):
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

        first = rc.area.left - rc.area.left % self.fontsize
        last = rc.area.right + rc.area.right % self.fontsize
        rc.clear('white')

        fo = cairo.FontOptions()
        fo.set_hint_metrics(cairo.HINT_METRICS_ON)
        fo.set_hint_style(cairo.HINT_STYLE_NONE)
        fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        c.set_font_options(fo)
        c.set_font_size(self.fontsize)
        font_extends = c.font_extents()

        rc.set_color(self.fontcolor)
        if self.fontsize > 6:
            for mark in xrange(first - self.fontsize*self.digits, last + self.fontsize*self.digits, self.fontsize):
                if (mark % (self.fontsize * self.digits)) == 0:
                    name = str(mark / self.fontsize)
                    text_width, text_height = c.text_extents(name)[2:4]
                    c.move_to(mark - text_width/2, font_extends[3])
                    c.show_text(name)

        for mark in xrange(first, last, self.fontsize):
            if self.fontsize > 3 and (mark % (self.fontsize * self.marks)) == 0:
                c.rectangle(mark, font_extends[3]+4, 1, rc.area.height)
            if (mark % (self.fontsize * self.digits)) == 0:
                c.rectangle(mark, font_extends[3]+2, 2, rc.area.height)
            c.fill()

        return self
