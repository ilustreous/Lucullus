class GeometryError(Exception): pass

class Area(object):
    def __init__(self, top=0, left=0, width=256, height=246):
        self.top = top
        self.left = left
        self.width = width
        self.height = height

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def right(self):
        return self.left + self.width

    @property
    def x(self):
        return self.left

    @property
    def y(self):
        return self.top

    @property
    def x1(self):
        return self.left

    @property
    def y1(self):
        return self.top

    @property
    def x2(self):
        return self.right

    @property
    def y2(self):
        return self.bottom

    @property
    def offset(self):
        return (self.left, self.top)

    @property
    def area(self):
        return (self.left, self.top, self.right, self.bottom)

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
