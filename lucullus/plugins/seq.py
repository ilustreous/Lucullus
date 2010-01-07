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
import urllib2
from StringIO import StringIO
import fnmatch

from lucullus.resource import BaseView, ResourceQueryError
from Bio import SeqIO, Seq, SeqRecord



class SequenceResource(BaseView):
	def prepare(self):
		self.sequences = []
		self.keys = []
		self.cols = 0
		self.rows = 0
		self.source = None
		self.format = 'fasta'
		self.fontsize = 12
		self.len = 0

	
	def setup(self, **options):
		self.fontsize = int(options.get('fontsize', self.fontsize))
		self.source = options.get('source', self.source)
		self.format = options.get('format', self.format)
		if 'source' in options:
			self.api_load(source=self.source, format=self.format)
		self.touch()

	
	def size(self):
		return (self.cols*self.fontsize, self.rows*self.fontsize)

	
	def getstate(self):
		s = super(SequenceResource, self).getstate()
		s['len'] = self.len
		s['fontsize'] = self.fontsize
		s['rows'] = self.rows
		s['columns'] = self.cols
		s['source'] = self.source
		s['format'] = self.format
		return s

	
	def api_load(self, source, format='fasta'):
		if source.startswith("http://"):
			try:
				data = urllib2.urlopen(source, None).read()
			except (urllib2.URLError, urllib2.HTTPError), e:
				raise ResourceQueryError('Faild do open URI: %s' % source)
			self.source = source
			self.format = format
		else:
			raise ResourceQueryError('Unsupported protocol or uri syntax: %s' % source)
		
		try:
			seq = SeqIO.parse(StringIO(data), self.format)
		except Exception, e:
			raise ResourceQueryError('Parser error %s: %s' % (e.__class__.__name__, str(e.args)))
		if not seq:
			raise ResourceQueryError('No sequences found.')
		for s in seq:
			self.sequences.append(str(s.seq))
			self.keys.append(s.id)
		self.cols = max([len(s) for s in self.sequences])
		self.rows = len(self.keys)
		self.len = self.rows
		self.touch()

	
	def api_position(self, **options):
		col = abs(int(options.get('column',0)))
		row = abs(int(options.get('row',0)))
		return {"x":self.fontsize * col, "y":self.fontsize * row}

	
	def api_search(self, **options):
		''' Search for a sequence name.
		    @param query Search string.
		    @param limit Number of matches to return
			@return matches List of matches {key:string, position:int}
			@return count Total number of seuquces
		    
		    Search string syntax:
		      '*' matches everything
		      '?' matches any single character
		      '[seq]' matches any character in seq
		      '[!seq]' matches any character not in seq
		'''
		q = options.get('query', 0)
		limit = max(1, int(options.get('limit', 25)))
		matches = []
		for i in xrange(len(self.keys)):
			key = self.keys[i]
			if fnmatch.fnmatch(key.lower(), q.lower()):
				matches.append({"name":key, "index":i+1})
				if len(matches) == limit:
					break
		if not matches and not q.endswith("*"):
			return self.api_search(query=q+'*', limit=limit)
		return {'matches':matches, 'count':len(self.keys)}

	
	def api_posinfo(self, **options):
		col = int(math.floor(float(options.get('x',0)) / self.fontsize))
		row = int(math.floor(float(options.get('y',0)) / self.fontsize))
		try:
			key = self.keys[row]
			seq = self.sequences[row]
			val = len(self.sequences[row]) >= col and self.sequences[row][col] or '-'
		except IndexError:
			key = "None"
			seq = ""
			val = '-'
		spos = min(col+1, len(seq)) - seq.count('-', 0, col+1)
		return {"key":key, "seqpos":spos, "value":val}

	
	def api_keys(self):
		return {"keys":self.keys}

	
	def render(self, rc):
		# Shortcuts
		c = rc.context
		area = rc.area
		
		# Configuration
		c.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		options = cairo.FontOptions()
		#fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		#fo.set_hint_style(cairo.HINT_STYLE_NONE)
		options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		c.set_font_options(options)
		c.set_font_size(self.fontsize - 1)
		lineheight = c.font_extents()[1]
		
		# Rows to consider
		row_first = int(math.floor( float(area.top) / self.fontsize))
		row_last  = int(math.ceil(	float(area.bottom) / self.fontsize))
		row_last  = min(row_last, self.rows)
		col_first = int(math.floor( float(area.left) / self.fontsize))
		col_last  = int(math.ceil(	float(area.right) / self.fontsize))
		#col_last  = min(col_last, self.cols)
		
		# Draw background
		rc.draw_stripes(self.fontsize*10, 'bio.amino-section1', 'bio.amino-section2')
		
		# Draw data
		for row in range(row_first, row_last):
			try:
				data = self.sequences[row][col_first:col_last].upper()
			except IndexError:
				data = ''
			# Fill with dashes
			data += '-' * (col_last - col_first - len(data))
			y = (row+1) * self.fontsize - lineheight
			cache = dict()
			for col in range(col_first, col_last):
				char = data[col - col_first]
				rc.set_color('bio.amino-%s' % char)
				if self.fontsize > 6:
					char_padding_left, char_padding_top, char_width, char_height = \
					cache.setdefault(char, c.text_extents(char)[0:4])
					x = self.fontsize * col + float(self.fontsize - char_width - char_padding_left)/2
					c.move_to(x, y)
					c.show_text(char)
				else:
					c.rectangle(self.fontsize * col, self.fontsize * row, self.fontsize, self.fontsize)
					c.fill()
		return self
















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
