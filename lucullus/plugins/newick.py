#!/usr/bin/env python
# encoding: utf-8
"""
newick.py

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

from lucullus.resource import BaseView
from Bio import SeqIO, Seq, SeqRecord

def next(s, search):
	''' Returns the index of the first occurance of multible search terms in
		a string or -1 on error (no match). Use a list or a multiline string
		to search for multible words. Use a string to search for multible
		chars. 
	'''
	return min([x for x in [s.find(x) for x in search] if x >= 0] or [-1])

class Tree(object):
	""" Represents a Tree, a subtree or a leaf. """

	def __init__(self, parent):
		'''Implements a tree'''
		self.label = ''
		self.parent = parent
		self.childs = []
		self._allchilds = []
		self._leafs = []
		self._path = []
		if self.parent:
			self.parent.childs.append(self)

	def left(self):
		""" First (left) child """
		return self.childs[0]
		
	def right(self):
		''' Last (right) child '''
		return self.childs[-1]

	def isroot(self):
		return (self.parent == None)

	def isleaf(self):
		return (not self.childs)

	def isempty(self):
		''' Empty nodes can have a parent, but no childs or label '''
		return not (self.childs or self.label)

	def path(self):
		if not self._path:
			if self.isroot():
				self._path = [self]
			else:
				self._path = self.parent.path() + [self]
		return self._path
	
	def allchilds(self):
		if not self._allchilds:
			for c in self.childs:
				self._allchilds += c.allchilds() + [c]
		return self._allchilds

	def leafs(self):
		'''Leafs, left first'''
		if not self._leafs:
			for c in self.childs:
				if c.isleaf():
					self._leafs += [c]
				else:
					self._leafs += c.leafs()
		return self._leafs

	def add(self, child):
		for c in child.allchilds():
			c._path = []
		for p in self.path():
			self._allchilds = []
			self._leafs = []
		self.childs.append(child)
		child.parent = self
		
	def remove(self, child):
		for c in child.allchilds():
			c._path = []
		for p in self.path():
			self._allchilds = []
			self._leafs = []
		self.childs.remove(child)
		child.parent = None
		
	def swap(self, p):
		"""Swap this node with a given node"""
		my_parent = self.parent
		his_parent = p.parent
		if my_parent:
			my_parent.remove(self)
		if his_parent:
			his_parent.remove(p)
		if my_parent:
			my_parent.add(p)
		if his_parent:
			his_parent.add(self)

	def insert(self, p):
		""" Insert this node into another tree, replacing the given node and
			adding the removed node as child. """
		if self.parent:
			self.parent.remove(self)

		if p.parent:
			p.parent.add(self)
			p.parent.remove(p)
		self.add(p)

	def reset(self):
		""" Resets metadata up and down the tree. Only touches meta
			information that is affected by the current node """
		for p in self.path():
			self._leafs = []
			self._allchilds = []
		self._path = []
		for c in self.allchilds():
			c._path = []

	def render(self, order=0):
		print ' '*order, self.label
		for c in self.childs:
			c.render(order+1)






class WeightedTree(Tree):
	def __init__(self, parent = None):
		Tree.__init__(self, parent)
		self.weight = 0.0

	def maxdepth(self):
		return max([l.position()[0] for l in self.tree.leafs()])






class NewickTree(WeightedTree):
	def parse(self, io, s=''):
		'''Parses a tree from a newick file and returns the rest '''
		while True:
			while io and len(s) < 128:
				n = io.read(128)
				if n:
					s += ''.join(n.split())
				else:
					break
			if s[0] == "(":					# Start of new subtree
				s = s[1:]
				sub = self.__class__(self)	#  Create new subtree
				s = sub.parse(io, s)		#  continue with new subtree
			elif s[0] == ',':				# A comma seperates childs. 
				s = s[1:]
				if self.isempty():			#  last node was empty -> ',,' or '(,'
					return s				#	Close it and continue with parent
				sub = self.__class__(self)	# Start a new subtree
				s = sub.parse(io, s)
			else:							# expect a label label or a :dist
				if s[0] == ')':				# '()x:y' is the same as 'x:y'
					s = s[1:]
					if self.isempty():
						self.parent.childs.remove(self)
						return s
				x = next(s,',)')			# Labels end with , (we are a left child) or ')' (we are a last child)
				if x < 0:
					label = s
					s = ''
				else:
					label = s[:x]
					s = s[x:]
				if label:					# Label found
					x = next(label,':')
					if x == 0:
						self.weight = abs(float(label[1:]))
					elif x > 0:
						self.label = label[:x]
						self.weight = abs(float(label[x+1:]))
					else:
						self.label = label
				return s
		self.reset()
		return s

	def export(self):
		label = self.label
		if not label:
			label = ''
		if self.weight:
			label += ':%f' % self.weight
		if self.isleaf():
			return label
		else:
			return '(' + ','.join([c.export() for c in self.childs]) + ')' + label






def tree_layout(tree):
	""" Returns three lists of nodes and lines prepared for a renderer:
	node  = (x, y, width, text, isleaf) ordered by y --> A-------B Text
	line  = Vertical line used to connect childs to parent node (x, y, height) ordered by x
	"""
	nodes = []
	lines = []
	lc	  = [0.5]

	def go_down(node, xpos):
		if node.isleaf():
			''' a---b text'''
			nodes.append((xpos, lc[0], node.weight, node.label, True))
			lc[0] = lc[0] + 1
			return lc[0] - 1
		else:
			''' a
				|
			c--(d)
				|
				b
			'''
			cpos = [go_down(c, xpos + node.weight) for c in node.childs]
			ax = xpos + node.weight
			ay = min(cpos)
			bx = ax
			by = max(cpos)
			lines.append((ax, ay, by-ay))
			if not node.isroot():
				cx = xpos
				cy = (ay + by) / 2
				dx = ax
				dy = cy
				nodes.append((cx, cy, node.weight, node.label, False))
				return cy

	go_down(tree, 0.0)
	out = (nodes, lines)
	out[0].sort(lambda a,b: cmp(a[1], b[1])) # Order by y inplace
	out[1].sort() # Order by x inplace
	return out











class NewickResource(BaseView):
	def prepare(self):
		self.tree	= None
		self.source = None
		self.format = 'newick'
		self.nodes	= 0
		self.fontsize = 12
		self.scale = 1.0
		self.scalex = None
		self.scaley = None
		self.vnodes = []
		self.vlines = []
		self.size = (0.0, 0.0)

	def configure(self, **options):
		self.fontsize = int(options.get('fontsize', self.fontsize))
		self.source = options.get('source', self.source)
		self.format = options.get('format', self.format)
		self.scale = float(self.options.get('scale', self.scale))
		if 'source' in options:
			self.api_load(source=self.source, format=self.format)
		self.touch()

	def api_load(self, source, format='newick'):
		if source.startswith("http://"):
			try:
				data = urllib2.urlopen(source, None)
			except (urllib2.URLError, urllib2.HTTPError), e:
				raise base.ResourceQueryError('Faild do open URI: %s' % source)
			self.source = source
			self.format = format
		else:
			raise base.ResourceQueryError('Unsupported protocol or uri syntax: %s' % source)

		self.tree = NewickTree(None)
		try:
			self.tree.parse(data)
		except Exception, e:
			raise base.ResourceQueryError('Parser error %s: %s' % (e.__class__.__name__, str(e.args)))
		if not self.tree.nodes():
			raise base.ResourceQueryError('No data found.')
		self.nodes = len(self.tree.nodes())
		self.api_layout('center')
		self.touch()
		return {"nodes":self.nodes}

	def api_layout(self, name='center'):
		if name == 'center':
			self.vnodes, self.vlines = tree_layout(self.tree)
		else:
			raise base.ResourceQueryError('Requested layout mode not implemented.')
		minstep = min([n[2] for n in self.vnodes if n[2] > 0]) # TODO excepton on empty tree
		self.scalex = 1.0 / minstep * self.scale
		self.scaley = self.fontsize * 1.25 # 1.25 = SPACING
		self.size = (0.0, 0.0)

		# Calculate image size using font_extends() data in a test surface
		test_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 16, 16) # 16 = small number
		test_context = cairo.Context(test_surface)
		self.setfontoptions(test_context)
		height = 0.0
		width = 0.0
		biglabel = 0.0
		for (x,y,w,label,isleaf) in self.nodes:
			if isleaf:
				lw = 0.0
				if label:
					lw = test_context.text_extents(label)[4]
				biglabel = max(lw, biglabel)
				width = max(width, self.scalex * (x + w) + 1.0 + lw)
				height += self.scaley
		self.vsize = (width, height)
		self.biglabel = biglabel

	def size(self):
		return self.vsize

	
	def state(self):
		s = super(NewickResource, self).state()
		s['nodes'] = self.nodes
		return s

	def setfontoptions(self, context):
		context.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		options = cairo.FontOptions()
		#fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		#fo.set_hint_style(cairo.HINT_STYLE_NONE)
		options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		context.set_font_options(options)
		context.set_font_size(self.fontsize)
		return context.font_extents()

	def draw(self, rc):
		# Shortcuts
		c = rc.context
		area = rc.area
		nodes = self.vnodes
		lines = self.vlines

		cminx, cminy, cmaxx, cmaxy = area.left, area.bottom, area.right, area.top
		sx, sy = self.scalex, self.scaley
		
		# Make sure clipping is not hiding any text nodes or hlines
		cminy -= self.biglabel
		cmaxy += self.biglabel
		cminx -= 1.0
		cmaxx += 1.0
				
		self.setfontoptions(c)
		rc.clear('white')
		rc.set_color('black')
		c.set_line_width(1.0)

		for (x,y,w,text,isleaf) in vnodes:
			# Nodes are sorted by y-position.
			y *= sy
			if y < cminy: continue
			if y > cmaxy: break
			x *= sx
			x2 = x + w*sx

			c.move_to(0.5 + round(x), 0.5 + round(y))
			c.line_to(0.5 + round(x2), 0.5 + round(y))
			c.stroke()
			if isleaf:
				context.set_font_size(self.fontsize)
				c.move_to(x2 + 1.0, y + self.fontsize/3) #TODO: Ugly
			else:
				lw = context.text_extents(text.strip())[4]
				context.set_font_size(self.fontsize * 0.85)
				#c.move_to(x2 + 1.0, y + self.fontsize/3) #TODO: Ugly
				c.move_to(x2 - lw, y - 1.0) #TODO: Ugly
			if text:
				c.show_text(text)
		
		for (x,y,h) in self.vlines:
			# hlines are sorted by x-position
			x *= sx
			if x < cminx: continue
			if x > cmaxx: break
			y *= sy
			y2 = y + h*sy
			c.move_to(0.5 + round(x), 0.5 + round(y))
			c.line_to(0.5 + round(x), 0.5 + round(y2))
			c.stroke()	






