#!/usr/bin/env python
# encoding: utf-8
"""
cimg.py

Created by Marcel Hellkamp on 2008-01-11.
Copyright (c) 2008 Marcel Hellkamp. All rights reserved.

Base classes for cairo renderer.
class CimgTarget (CimgTargetFile, ...)
  Desctiptor for render destinations (svg, png, GTK-surface,...)
class Cimg
  Base class for render engines

Exception Tree
  InvalidSourceException
  OutputFormatException
  OutOfRangeException
	SizeOfRangeException
	AreaOutOfRangeException
	ZoomOutOfRangeException

"""

import cairo, math, random, os, sys
import shapes


# Helper

def draw_stripes(context, x, y, w, h, weight, c1, c2):
	'''Rendert einen gestreiften Hintergrund'''
	# Compute start color
	if math.floor(float(x) / weight) % 2:
		(c1, c2) = (c2, c1) #swap
	# offset is the absolute x position of the first section
	offset = - (x % weight )
	while offset < w:
		(c1, c2) = (c2, c1) #swap
		context.set_source_rgba(c1[0], c1[1], c1[2], c1[3])
		context.rectangle(x+offset,y,weight,h)
		context.fill()
		offset += weight



# Exceptions
class InvalidSourceException(Exception): pass
class OutputFormatException(Exception): pass
class OutOfRangeException(Exception): pass
class SizeOfRangeException(OutOfRangeException): pass
class AreaOutOfRangeException(OutOfRangeException): pass
class ZoomOutOfRangeException(OutOfRangeException): pass
class ViewOutOfRangeException(OutOfRangeException): pass

class BaseRenderer:
	def __init__(self, source, **options):
		self.options = options
		self.source			= source			# Data source (any format)
		self.area			= ((0,0),(0,0))		# Position (x,y) and size (width,height) of the drawable area
		self.view			= ((0,0),(0,0))		# Position (x,y) and size (width,height) of the viewable area
		self._source()

	def area_position(self):
		'''Returns the position (x, y) of the data area'''
		return self.area[0]

	def area_size(self):
		'''Returns the size (width, height) of the data area'''
		return self.area[1]

	def area_width(self):
		'''Returns the width of the data area'''
		return self.area[1][0]

	def area_height(self):
		'''Returns the height of the data area'''
		return self.area[1][1]

	def area_boundary(self):
		'''Returns the boundary (min_x, min_y, max_x, max_y) of the data area'''
		return (self.area[0][0], self.area[0][1], self.area[0][0]+self.area[1][0], self.area[0][1]+self.area[1][1])





	def viewport(self, x, y, width=255, height=255, relative=False):
		'''Selects an area to render and computes self.view. There is no test of valid values.
			If ''relative'' is True, the position is considered relative to the data area'''
			
		x,y = int(x),int(y)
		if relative:
			x += self.area[0][0]
			y += self.area[0][1]
		w,h = abs(int(width)), abs(int(height))
		self.view  = ((x,y),(w,h))
		self._viewport()
		return self
		
	def view_position(self):
		'''Returns the position (x, y) of the data view'''
		return self.view[0]

	def view_size(self):
		'''Returns the size (width, height) of the data view'''
		return self.view[1]

	def view_x(self):
		'''Returns the x position of the data view'''
		return self.view[0][0]

	def view_y(self):
		'''Returns the y position of the data view'''
		return self.view[0][1]

	def view_width(self):
		'''Returns the width of the data view'''
		return self.view[1][0]

	def view_height(self):
		'''Returns the height of the data view'''
		return self.view[1][1]

	def view_boundary(self):
		'''Returns the boundary (min_x, min_y, max_x, max_y) of the data view'''
		return (self.view[0][0], self.view[0][1], self.view[0][0]+self.view[1][0], self.view[0][1]+self.view[1][1])

	def render(self, f, width, height):
		width = abs(int(width))
		height = abs(int(height))

		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
		context = cairo.Context(surface)
		context.scale(width / self.view_width(), height / self.view_height())
		context.translate(- self.view[0][0], - self.view[0][1])
		self._render(context)
		surface.write_to_png(f)


 	def _source(self):
		''' Validiates and prepares self.source and calculates values for self.area
			Override this with your implementation.
			You have access to self.source'''
		pass
		
	def _viewport(self):
		''' Validiates self.view and corrects them, if possible.
			Override this with your implementation.
			You have access to self.source, self.area and self.view (new)'''
		pass
		
	def _render(self):
		''' Validiates self.target and does the rendering thing.
			Override this with your implementation.
			You have access to self.source, self.zoomlevel, self.area and self.view (new)'''
		pass























# Not used anymore but helpful
def intcolor(i, reverse = False):
	"""Splits a 32 bit integer into 4x8bit and represents them as floats between 0.0 and 1.0
	   This can be used to split an 32bit color code into its RGBA values
	   From low to high: red, green, blue, alpha """
	r = float( i		 % 256) / 255
	g = float((i >> 8  ) % 256) / 255
	b = float((i >> 16 ) % 256) / 255
	a = float((i >> 24 )	  ) / 255
	if reverse:
		return (a,b,g,r)
	else:
		return (r,g,b,a)

def hexcolor(h):
	'''Converts an #rgb, #rgba, #rrggbb or #rrggbbaa hex code to a quatuple (red,green,blue,alpha) of floats between 0.0 and 1.0'''
	h = h.strip()
	h = h.lstrip('#')
	if len(h) == 3:
		h = h[0]*2 + h[1]*2 + h[2]*2 + 'ff'
	elif len(h) == 4:
		h = h[0]*2 + h[1]*2 + h[2]*2 + h[3]*2
	elif len(h) == 6:
		h = h + 'ff'
	elif len(h) == 8:
		pass
	else:
		raise AttributeError, "This is not a valid hex color code: %s" % h

	i = int(h,16)
	return intcolor(i, reverse=True)
	
color = {}
color['*'] = hexcolor('#000000FF')
color['-'] = hexcolor('#999999FF')
color['A'] = hexcolor('#008000FF')
color['C'] = hexcolor('#A20000FF')
color['E'] = hexcolor('#FF0000FF')
color['D'] = hexcolor('#FF0000FF')
color['G'] = hexcolor('#FF00FFFF')
color['F'] = hexcolor('#008000FF')
color['I'] = hexcolor('#008000FF')
color['H'] = hexcolor('#0080FFFF')
color['K'] = hexcolor('#0000D9FF')
color['M'] = hexcolor('#008000FF')
color['L'] = hexcolor('#008000FF')
color['N'] = hexcolor('#8080C0FF')
color['Q'] = hexcolor('#7171B9FF')
color['P'] = hexcolor('#D9D900FF')
color['S'] = hexcolor('#FF8000FF')
color['R'] = hexcolor('#0000FFFF')
color['T'] = hexcolor('#FF8000FF')
color['W'] = hexcolor('#00FF00FF')
color['V'] = hexcolor('#008000FF')
color['Y'] = hexcolor('#008000FF')
color['X'] = hexcolor('#000000FF')
color['section2'] = hexcolor('#EEEEEEFF')
color['section1'] = hexcolor('#FFFFFFFF')























class IndexRenderer(BaseRenderer):
	def _source(self):
		self.fieldsize	= self.options.get('fontsize',12) + 2
		self.cols		= 0
		self.rows		= 0
		self.fontsize	= None
		if self.source:
			self.cols = max( [len(i) for i in self.source] )
			self.rows  = len(self.source)
		self.area = ((0, 0), (self.cols*self.fieldsize, self.rows*self.fieldsize))

	def _viewport(self):
		((x,y),(w,h)) = self.view
		((rx,ry),(rw,rh)) = self.area

		if w not in range(128,1024) or h not in range(128,1024):
			raise ViewOutOfRangeException, 'Viewport to big or to small. It should be between 128 and 1024 pixles.'

		if x+w < rx or x > rx+rw or y+h < ry or y > ry+rh:
			raise ViewOutOfRangeException, 'Viewport does not overlap with drawable area.'

	def _render(self, context):
		# Shortcuts
		source				= self.source
		((vx,vy),(vw,vh))	= self.view
		((ax,ay),(aw,ah))	= self.area
		fieldsize			= self.fieldsize
		c					= context
		
		# Configuration
		ccodes = color		# using module variable

		# Rows to consider
		row_first = int(math.floor( float(vy-ay)	/ fieldsize))
		row_last  = int(math.ceil(	float(vy-ay+vh) / fieldsize))
		print row_first, row_last, vy, ay
		# Fill the background with #ffffff
		c.set_source_rgb(1, 1, 1)
		c.rectangle(vx, vy, vw, vh)
		c.fill()

		# Font settings
		c.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		fo = cairo.FontOptions()
		fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		fo.set_hint_style(cairo.HINT_STYLE_NONE)
		fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		c.set_font_options(fo)
		if not self.fontsize:
			fsize = sum(c.font_extents()[0:2])
			fsize = float(fieldsize) * 0.75 * (fieldsize / fsize)
			self.fontsize = fsize
		c.set_font_size(self.fontsize)
		c.set_source_rgb(0, 0, 0)
		font_extends = context.font_extents()

		cm = c.get_matrix()
		c.translate(0, row_first * fieldsize)
		for row in range(row_first, row_last+1):
			if row % 2:
				c.set_source_rgb(0.95, 0.95, 0.95)
				c.rectangle(0, 0, vw, self.fieldsize)
				c.fill()
				c.set_source_rgb(0, 0, 0)
			try:				name = source[row]
			except IndexError:	name = ''
			y = self.fieldsize - font_extends[1]
			x = 0 #self.fieldsize * (col_first+col) + float(self.fieldsize - char_width - char_padding_left)/2
			context.move_to(x, y)
			context.show_text(name)
			c.translate(0, fieldsize)
		c.set_matrix(cm)
		
		return self


















class RulerRenderer(BaseRenderer):
	def _source(self):
		self.fieldsize	= self.options.get('fontsize',12) + 2
		self.cols		= 0
		self.rows		= 2
		self.fontsize	= None
		if self.source:
			self.cols = int(self.source)
		self.area = ((0, 0), (self.cols*self.fieldsize, self.rows*self.fieldsize))

	def _viewport(self):
		((x,y),(w,h)) = self.view
		((rx,ry),(rw,rh)) = self.area

		if w not in range(128,1024) or h not in range(128,1024):
			raise ViewOutOfRangeException, 'Viewport to big or to small. It should be between 128 and 1024 pixles.'

		if x+w < rx or x > rx+rw or y+h < ry or y > ry+rh:
			raise ViewOutOfRangeException, 'Viewport does not overlap with drawable area.'

	def _render(self, context):
		# Shortcuts
		source				= self.source
		((vx,vy),(vw,vh))	= self.view
		((ax,ay),(aw,ah))	= self.area
		fieldsize			= self.fieldsize
		c					= context

		# Rows to consider
		row_first = int(math.floor( float(vy-ay)	/ fieldsize))
		row_last  = int(math.ceil(	float(vy-ay+vh) / fieldsize))
		col_first = int(math.floor( float(vx-ax)	/ fieldsize))
		col_last  = int(math.ceil(	float(vx-ax+vw) / fieldsize))

		# To prevent cutting numbers at the view border, we have to look bejond the borders
		col_last	+= 10 - col_last % 10 + 1
		col_first	-= col_first % 10 + 1

		# Draw background
		draw_stripes(c, vx, vy, vw, vh, (fieldsize*10), color["section1"], color["section2"])

		# Font settings
		c.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		fo = cairo.FontOptions()
		fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		fo.set_hint_style(cairo.HINT_STYLE_NONE)
		fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		c.set_font_options(fo)
		if not self.fontsize:
			fsize = sum(c.font_extents()[0:2])
			fsize = float(fieldsize) * 0.75 * (fieldsize / fsize)
			self.fontsize = fsize
		c.set_font_size(self.fontsize)
		c.set_source_rgb(0, 0, 0)
		font_extends = context.font_extents()
		
		for i in range(col_first,col_last):
			# Draw marks
			x = i * fieldsize + fieldsize/2
			if (i % 5) == 0:
				c.rectangle(x,20-5,1,ah)
			elif (i % 10) == 0:
				c.rectangle(x-1,20-5,3,ah)
			else:
				c.rectangle(x,20-2,1,ah)
			c.fill()

			# Draw Numbers			
			if (i % 10) == 0:
				name = str(i)
				text_width, text_height = c.text_extents(name)[2:4]
				x = i * fieldsize + fieldsize/2 - text_width/2
				y = 20 - font_extends[1] - 5
				c.move_to(x, y)
				c.show_text(name)
				

		return self













import unittest, random

class TestColorFunc(unittest.TestCase):
	def setUp(self):
		self.colors = []
		self.colors.append(('#0080ff',8454143, (0.0, 128.0/255, 1.0, 1.0)))
		self.colors.append(('#0080ffff',8454143, (0.0, 128.0/255, 1.0, 1.0)))
		self.colors.append(('#00f',65535, (0.0, 0.0, 1.0, 1.0)))
		self.colors.append(('#00ff',65535, (0.0, 0.0, 1.0, 1.0)))
		
	def testintcolor(self):
		for (h,i,c) in self.colors:
			self.assertEqual(intcolor(i, reverse=True), c, i)

	def testhexcolor(self):
		for (h,i,c) in self.colors:
			self.assertEqual(hexcolor(h), c, h)


class TestSequenceRenderer(unittest.TestCase):
	def setUp(self):
		self.r = SequenceRenderer(['AAABBBb','ABABAB','ABCDEFG'])


	def testsourceparser(self):
		r = self.r
		self.assertEqual(r.cols, 7, 'r.cols')
		self.assertEqual(r.rows, 3, 'r.rows')
		area = ((0, 0), (r.cols*r.fieldsize, r.rows*r.fieldsize))
		self.assertEqual(r.area, area, 'r.area')
		self.assertEqual(r.area_position(),area[0],'area_position')
		self.assertEqual(r.area_size(),area[1],'area_size')
		self.assertEqual(r.area_width(),area[1][0],'area_width')
		self.assertEqual(r.area_height(),area[1][1],'area_height')
		self.assertEqual(r.area_boundary(),(area[0][0], area[0][1], area[0][0]+area[1][0], area[0][1]+area[1][1]),'area_boundary')

	def testviewport(self):
		r = self.r
		self.assertRaises(ViewOutOfRangeException, r.viewport, 0, 0, 10, 10)
		self.assertRaises(ViewOutOfRangeException, r.viewport, 0, 0, 10000, 10000)
		self.assertRaises(ViewOutOfRangeException, r.viewport, 100000, 100000, 1000, 1000)
		self.assertRaises(ViewOutOfRangeException, r.viewport, -100000, -100000, 1000, 1000)
		r.viewport(0, 1, 200, 300)
		self.assertEqual(r.view_position(),(0,1),'view_position')
		self.assertEqual(r.view_size(),(200,300),'view_size')
		self.assertEqual(r.view_x(),0,'view_x')
		self.assertEqual(r.view_y(),1,'view_x')
		self.assertEqual(r.view_width(),200,'view_width')
		self.assertEqual(r.view_height(),300,'view_height')
		self.assertEqual(r.view_boundary(),(0,1,200,301),'view_boundary')

	def testgrouper(self):
		r = self.r
		self.assertEqual(r._parse_groups('AAABBBB'),[('A',0,3),('B',3,4)],'Grouper AAABBBB')
		self.assertEqual(r._parse_groups('ABABAB'),[('A',0,1),('B',1,1),('A',2,1),('B',3,1),('A',4,1),('B',5,1)],'Grouper ABABAB')


if __name__ == '__main__':
	unittest.main()
