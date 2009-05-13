from lucullus.lib import pyseq
from lucullus.lib.pyseq import renderer
from lucullus.lib.pyseq import shapes

from Bio import SeqIO, Seq, SeqRecord

import sys
import re



def next(s,search):
	''' Helper to find the first occurance of multible search terms in a string.
		Use a list or a multiline string to search for multible words. Use a string to search for multible chars. 
	    Returns the lowest index of all matches or -1 on error (no match)
	'''
	n = [x for x in [s.find(x) for x in search] if x >= 0]
	if n:
		return min(n)
	else:
		return -1






class Tree(object):
	""" Represents a Tree, a subtree or a leaf. Use add(), remove(), swap() and insert() to manipulate the tree. Use root.reset() to clear cached meta data"""

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
		""" Insert this node into another tree, replacing the given node and adding the removed node as child. """
		if self.parent:
			self.parent.remove(self)

		if p.parent:
			p.parent.add(self)
			p.parent.remove(p)
		self.add(p)

	def reset(self):
		""" Resets metadata up and down the tree. Only touches meta information that is affected by the current node """
		for p in self.path():
			self._leafs = []
			self._allchilds = []
		self._path = []
		for c in self.allchilds():
			c._path = []

	def render(self, order=0):
		print '	'*order, self.label
		for c in self.childs:
			c.render(order+1)






class WeightedTree(Tree):
	def __init__(self, parent = None):
		Tree.__init__(self, parent)
		self.weight = 0.0

	def maxdepth(self):
		return max([l.position()[0] for l in self.tree.leafs()])






class LayoutTree(WeightedTree):
	def __init__(self, parent = None):
		Tree.__init__(self, parent)
		self._height = 0
	
	def height(self):
		if not self._height:
			if self.isleaf():
				self._height = 1.0
			else:
				self._height = sum(c.height() for c in self.childs)
		return self._height






class NewickTree(WeightedTree):
	def parse(self, io, s=''):
		'''Parses a tree from a newick file and returns the rest'''
		while True:
			while io and len(s) < 128:
				n = io.read(128)
				if n:
					s += ''.join(n.split())
				else:
					break
			if s[0] == "(":								# Start of new subtree
				s = s[1:]
				sub = self.__class__(self)				#  Create new subtree
				s = sub.parse(io, s)				#  continue with new subtree
			elif s[0] == ',':							# A comma seperates childs. 
				s = s[1:]
				if self.isempty():						#  last node was empty -> ',,' or '(,'
					return s							#   Close it and continue with parent
				sub = self.__class__(self)					# Start a new subtree
				s = sub.parse(io, s)
			else:										# expect a label label or a :dist
				if s[0] == ')':							# '()x:y' is the same as 'x:y'
					s = s[1:]
					if self.isempty():
						self.parent.childs.remove(self)
						return s
				x = next(s,',)')						# Labels end with , (we are a left child) or ')' (we are a last child)
				if x < 0:
					label = s
					s = ''
				else:
					label = s[:x]
					s = s[x:]
				if label:								# Label found
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
	tree_layout.tokens = []
	tree_layout.lc     = 0.0

	def go_down(node, xpos):
		if node.isleaf():
			''' a---b '''
			ax = xpos
			ay = tree_layout.lc
			bx = xpos + node.weight
			by = tree_layout.lc
			tree_layout.tokens.append(['line', ax, ay, bx, by])
			tree_layout.tokens.append(['label', bx, by, node.label])
			tree_layout.lc += 1
			return ay
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
			tree_layout.tokens.append(['line', ax, ay, bx, by])
			if not node.isroot():
				cx = xpos
				cy = (ay + by) / 2
				dx = ax
				dy = cy
				tree_layout.tokens.append(['line', cx, cy, dx, dy])
				return cy

	go_down(tree, 0.0)
	tokens = tree_layout.tokens
	tree_layout.tokens = []
	return tokens

def tree_center_layout(tree):
	# TODO not thread save...
	""" Returns three lists of nodes and lines prepared for a renderer:
	node  = (x, y, width, text, isleaf) ordered by y --> A-------B Text
	line  = Vertical line used to connect childs to parent node (x, y, height) ordered by x
	"""
	tree_center_layout.nodes = []
	tree_center_layout.lines  = []
	tree_center_layout.lc     = 0.5

	def go_down(node, xpos):
		if node.isleaf():
			''' a---b text'''
			tree_center_layout.nodes.append((xpos, tree_center_layout.lc, node.weight, node.label, True))
			tree_center_layout.lc += 1
			return tree_center_layout.lc - 1
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
			tree_center_layout.lines.append((ax, ay, by-ay))
			if not node.isroot():
				cx = xpos
				cy = (ay + by) / 2
				dx = ax
				dy = cy
				tree_center_layout.nodes.append((cx, cy, node.weight, node.label, False))
				return cy

	go_down(tree, 0.0)
	out = (tree_center_layout.nodes, tree_center_layout.lines)
	out[0].sort(lambda a,b: cmp(a[1], b[1])) # Order by y inplace
	out[1].sort() # Order by x inplace
	
	tree_center_layout.nodes = []
	tree_center_layout.leafs = []
	tree_center_layout.lines  = []
	tree_center_layout.lc     = 0.0
	return out

















class PhbProject(pyseq.Project):
	def __init__(self, workdir):
		super(self.__class__, self).__init__(workdir)
		self.ressources['phb'] = ''

	def load(self, io, format):
		self.ressources['phb'] = io.read()
		tree = NewickTree(None)
		tree.parse(StringIO.StringIO(self.ressources['phb']))
		self.ressources['label'] = [node.label for node in tree.leafs()]
		
		self.views['tree'] = PhbView(tree=tree, fontsize=12, scale = 1.0)
		self.views['index'] = pyseq.renderer.IndexRenderer([node.label for node in tree.leafs()])
		self.views['ruler'] = pyseq.renderer.RulerRenderer(self.views['tree'].size[1])

pyseq.add_project('phb', PhbProject)




import cairo, math, random, os, sys, StringIO

class PhbView(pyseq.BaseView):
	def prepare(self):
		self.fontsize = self.options.get('fontsize',12)
		tree = self.options.get('tree',NewickTree(None))
		scale = self.options.get('scale',1.0)
		self.nodes, self.vlines = tree_center_layout(tree)
		minstep = 9999999999.0
		for node in self.nodes:
			if minstep > node[2] > 0:
				minstep = node[2]
		self.scalex = 1.0 / minstep * scale
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
		self.size = (width, height)
		self.biglabel = biglabel
		

	def setfontoptions(self, context):
		context.select_font_face("mono",cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		options = cairo.FontOptions()
		#fo.set_hint_metrics(cairo.HINT_METRICS_ON)
		#fo.set_hint_style(cairo.HINT_STYLE_NONE)
		options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		context.set_font_options(options)
		context.set_font_size(self.fontsize)
		return context.font_extents()
		

	def draw(self, context, clipping):
		# Shortcuts
		nodes = self.nodes
		vlines = self.vlines
		cminx, cminy, cmaxx, cmaxy = clipping
		c = context
		sx, sy = self.scalex, self.scaley
		
		# Make sure clipping is not hiding any text nodes or hlines
		print cminx, cminy, cmaxx, cmaxy
		cminy -= self.biglabel
		cmaxy += self.biglabel
		cminx -= 1.0
		cmaxx += 1.0
		print cminx, cminy, cmaxx, cmaxy
				
		self.setfontoptions(c)
		c.set_source_rgba(1.0,1.0,1.0,1.0)
		c.paint()

		c.set_source_rgba(0.0,0.0,0.0,1.0)
		c.set_line_width(1.0)

		for (x,y,w,text,isleaf) in self.nodes:
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
			