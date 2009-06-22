#!/usr/bin/env python
# encoding: utf-8
"""
plugin_seq.py

Created by Marcel Hellkamp on 2009-01-20.
Copyright (c) 2008 Marcel Hellkamp. All rights reserved.
"""

import cairo
import math
import random
import os
import sys

from lucullus import base
from lucullus.base import renderer
from lucullus.base import shapes
from Bio import SeqIO, Seq, SeqRecord



class SequenceResource(base.BaseResource):
	def prepare(self):
		self.data	= []
		self.len	= 0
		self.width	= 0
		self.source = None
		self.format = None

	def status(self):
		s = super(SequenceResource, self).status()
		s['len'] = self.len
		s['width'] = self.width
		return s

	def api_load(self, source, format='fasta'):
		self.source = source
		self.format = format
		text = self.session.get_resource(self.source)
		if not isinstance(text, base.TextResource):
			raise base.ResourceQueryError('Can not load resources other than TextResource')
	
		data = text.getIO()
		try:
		  data = SeqIO.parse(data, self.format)
		except Exception, e:
			raise base.ResourceQueryError('Parser error %s: %s' % (e.__class__.__name__, str(e.args)))
		if not data:
			raise base.ResourceQueryError('No sequences found.')

		self.data += [[seq.id, str(seq.seq)] for seq in data]
		self.len = len(self.data)
		self.width = max([len(seq[1]) for seq in self.data])
		self.touch()
		return {"len":self.len, 'width':self.width}

	def api_index(self, **options):
		return {"len":self.len, "index":list(self.getIndex())}

	def getIndex(self):
		for data in self.data:
			yield data[0]

	def getData(self):
		for data in self.data:
			yield data[1]

	def export(self):
		for (key, seq) in self.data:
			yield ">%s\n" % key
			yield seq
			yield "\n"


base.register_plugin("SequenceResource", SequenceResource)







class SequenceView(base.BaseView):
	def prepare(self):
		self.fieldsize = 12
		self.data = []
		self.cols = 0
		self.rows = 0
		self.source = None
		self.color = {}
		self.color['*'] = renderer.hexcolor('#000000FF')
		self.color['-'] = renderer.hexcolor('#999999FF')
		self.color['A'] = renderer.hexcolor('#008000FF')
		self.color['C'] = renderer.hexcolor('#A20000FF')
		self.color['E'] = renderer.hexcolor('#FF0000FF')
		self.color['D'] = renderer.hexcolor('#FF0000FF')
		self.color['G'] = renderer.hexcolor('#FF00FFFF')
		self.color['F'] = renderer.hexcolor('#008000FF')
		self.color['I'] = renderer.hexcolor('#008000FF')
		self.color['H'] = renderer.hexcolor('#0080FFFF')
		self.color['K'] = renderer.hexcolor('#0000D9FF')
		self.color['M'] = renderer.hexcolor('#008000FF')
		self.color['L'] = renderer.hexcolor('#008000FF')
		self.color['N'] = renderer.hexcolor('#8080C0FF')
		self.color['Q'] = renderer.hexcolor('#7171B9FF')
		self.color['P'] = renderer.hexcolor('#D9D900FF')
		self.color['S'] = renderer.hexcolor('#FF8000FF')
		self.color['R'] = renderer.hexcolor('#0000FFFF')
		self.color['T'] = renderer.hexcolor('#FF8000FF')
		self.color['W'] = renderer.hexcolor('#00FF00FF')
		self.color['V'] = renderer.hexcolor('#008000FF')
		self.color['Y'] = renderer.hexcolor('#008000FF')
		self.color['X'] = renderer.hexcolor('#000000FF')
		self.color['section2'] = renderer.hexcolor('#EEEEEEFF')
		self.color['section1'] = renderer.hexcolor('#FFFFFFFF')

	def size(self):
		return (self.cols*self.fieldsize, self.rows*self.fieldsize)
		
	def status(self):
		s = super(SequenceView, self).status()
		s['fieldsize'] = self.fieldsize
		s['rows'] = self.rows
		s['columns'] = self.cols
		return s

	def api_set(self, **options):
		self.fieldsize = int(options.get('fieldsize', self.fieldsize))
		for key in options:
			if key.startswith('color-'):
				try:
				  self.color[key[6:]] = base.renderer.hexcolor(options[key])
				except AttributeError:
					pass

	def api_load(self, source, **options):
		self.source = source
		seq = self.session.get_resource(self.source)
		if not isinstance(seq, SequenceResource):
			raise base.ResourceQueryError('Can not load resources other than SequenceResource')
		self.data = list(seq.getData())
		self.cols = max([len(d) for d in self.data])
		self.rows = len(self.data)
		self.touch()
		return {'columns':self.cols, 'rows':self.rows}

	def api_position(self, **options):
		col = abs(int(options.get('column',0)))
		row = abs(int(options.get('row',0)))
		return {"x":self.fieldsize * col, "y":self.fieldsize * row}

	def setfontoptions(self, context):
		context.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		options = cairo.FontOptions()
		#fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		#fo.set_hint_style(cairo.HINT_STYLE_NONE)
		options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		context.set_font_options(options)
		context.set_font_size(self.fieldsize - 1)
		return context.font_extents()
		
	def render(self, context, x, y, w, h):
		# Shortcuts
		cminx, cminy, cmaxx, cmaxy = x, y, x+w, y+h
		c = context
		fieldsize = self.fieldsize
		fontsize = self.fieldsize - 1
		cc = self.cols
		rc = self.rows
		color = self.color
		
		# Configuration
		self.setfontoptions(c)
		lineheight = context.font_extents()[1]

		# Rows to consider
		row_first = int(math.floor( float(cminy) / fieldsize))
		row_last  = int(math.ceil(  float(cmaxy) / fieldsize))
		row_last  = min(row_last, self.rows)
		col_first = int(math.floor( float(cminx) / fieldsize))
		col_last  = int(math.ceil(  float(cmaxx) / fieldsize))
		#col_last  = min(col_last, self.cols)
		
		# Draw background
		base.renderer.draw_stripes(c, cminx, cminy, w, h, (fieldsize*10), color["section1"], color["section2"])

		# Draw data
		for row in range(row_first, row_last):
			try:
				data = self.data[row][col_first:col_last].upper()
			except IndexError:
				data = ''
			# Fill with dashes
			data += '-' * (col_last - col_first - len(data))
			y = (row+1) * fieldsize - lineheight
			for col in range(col_first, col_last):
				char = data[col - col_first]
				(r,g,b,a) = self.color.get(char,(0,0,0,1))
				context.set_source_rgba(r,g,b,a)
				char_padding_left, char_padding_top, char_width, char_height = context.text_extents(char)[0:4]
				x = fieldsize * col + float(fieldsize - char_width - char_padding_left)/2
				context.move_to(x, y)
				context.show_text(char)
		return self

base.register_plugin("SequenceView", SequenceView)
















"""		
	def _parse_groups(self, line, offset = 0):
		'''Parses a string and searches blocks of the same char.
				returns a list of (char, start, len) triples'''
		start = offset		# Start of the current group
		size = 0			# Size of the current group
		current = line[0]	# Character of the current group
		groups = []
		for s in line:
			if s == current:
				size += 1
			else:
				groups.append((current, start, size))
				start = start + size
				size = 1
				current = s
		groups.append((current, start, size))
		return groups

	def _render_dna(self, data, context):
		((vx,vy),(vw,vh))	= self.view
		((ax,ay),(aw,ah))	= self.area
		fieldsize			= self.fieldsize
		c					= context

		# Data area to consider
		col_first = int(math.floor( float(vx-ax)	/ fieldsize))
		col_last  = int(math.ceil(	float(vx-ax+vw) / fieldsize))

		data = self._parse_groups(data)

		for (code, start, size) in data:
			if start > col_last:
				break
			if start+size > col_first:
				x = float(self.fieldsize * start)
				y = 0.0
				w = float(self.fieldsize * size)
				h = float(self.fieldsize)
				rx = float(self.fieldsize) / 2
				ry = float(self.fieldsize) / 2
				rrx = 0.5
				rry = 0.5
				border = 1.0
				(r,g,b,a) = color.get(code,(0,0,0,1))

				c.set_source_rgba(r,g,b,a)
				i = random.randint(0,3)
				if True or i == 1:
					c.new_path()
					c.arc(x+w-h/2,y+h/2,h/2-border,0,2*math.pi)
					c.set_source_rgba(r,g,b,a)
					c.fill()
					#pat = cairo.LinearGradient(x, y, x+h, y+h);
					#cairo_pattern_add_color_stop_rgba (pat, 1, 0, 0, 0, 1);
					#cairo_pattern_add_color_stop_rgba (pat, 0, 1, 1, 1, 1);


					shapes.path_tube(c,x,y,w,h,border)
					c.fill()
				elif i==2:
					shapes.path_arrow(c,x,y,w,h,rx,h-rx,0.0,border)
				else:
					c.rectangle(x+border,y+ry/2+border,w-border*2,h-ry-border*2)
				c.fill()
				

"""
