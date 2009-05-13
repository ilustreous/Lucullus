from lucullus.lib import pyseq
from lucullus.lib.pyseq import renderer
from lucullus.lib.pyseq import shapes

from Bio import SeqIO, Seq, SeqRecord
import cairo, math, random, os, sys



class SequenceResource(pyseq.BaseResource):
	def prepare(self):
		self.data	= []
		self.len	= 0
		self.width	= 0
		self.source = None
		self.format = None

	def api_load(self, source, format='fasta'):
		self.source = source
		self.format = format
		text = self.session.get_resource(self.source)
		if not isinstance(text, pyseq.TextResource):
			raise pyseq.ResourceQueryError('Can not load resources other than TextResource')
	
		data = text.getIO()
		try:
		  data = SeqIO.parse(data, self.format)
		except Exception, e:
			raise pyseq.ResourceQueryError('Parser error %s: %s' % (e.__class__.__name__, str(e.args)))
		if not data:
			raise pyseq.ResourceQueryError('No sequences found.')

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


pyseq.register_plugin("SequenceResource", SequenceResource)







class SequenceView(pyseq.BaseView):
	def prepare(self):
		self.fieldsize = 12
		self.data = []
		self.cols = 0
		self.rows = 0
		self.source = None
		self.offset = 0
		self.limit = 1024
		self.color = {}
		self.color['*'] = pyseq.renderer.hexcolor('#000000FF')
		self.color['-'] = pyseq.renderer.hexcolor('#999999FF')
		self.color['A'] = pyseq.renderer.hexcolor('#008000FF')
		self.color['C'] = pyseq.renderer.hexcolor('#A20000FF')
		self.color['E'] = pyseq.renderer.hexcolor('#FF0000FF')
		self.color['D'] = pyseq.renderer.hexcolor('#FF0000FF')
		self.color['G'] = pyseq.renderer.hexcolor('#FF00FFFF')
		self.color['F'] = pyseq.renderer.hexcolor('#008000FF')
		self.color['I'] = pyseq.renderer.hexcolor('#008000FF')
		self.color['H'] = pyseq.renderer.hexcolor('#0080FFFF')
		self.color['K'] = pyseq.renderer.hexcolor('#0000D9FF')
		self.color['M'] = pyseq.renderer.hexcolor('#008000FF')
		self.color['L'] = pyseq.renderer.hexcolor('#008000FF')
		self.color['N'] = pyseq.renderer.hexcolor('#8080C0FF')
		self.color['Q'] = pyseq.renderer.hexcolor('#7171B9FF')
		self.color['P'] = pyseq.renderer.hexcolor('#D9D900FF')
		self.color['S'] = pyseq.renderer.hexcolor('#FF8000FF')
		self.color['R'] = pyseq.renderer.hexcolor('#0000FFFF')
		self.color['T'] = pyseq.renderer.hexcolor('#FF8000FF')
		self.color['W'] = pyseq.renderer.hexcolor('#00FF00FF')
		self.color['V'] = pyseq.renderer.hexcolor('#008000FF')
		self.color['Y'] = pyseq.renderer.hexcolor('#008000FF')
		self.color['X'] = pyseq.renderer.hexcolor('#000000FF')
		self.color['section2'] = pyseq.renderer.hexcolor('#EEEEEEFF')
		self.color['section1'] = pyseq.renderer.hexcolor('#FFFFFFFF')

	def api_load(self, source, offset=0, limit=1024, **options):
		self.source = source
		self.offset = abs(int(offset))
		self.limit = abs(int(limit))
		self.fieldsize = options.get('fieldsize', self.fieldsize)
		for key in options:
			if key.startswith('color-'):
				try:
				  self.color[key[6:]] = pyseq.renderer.hexcolor(options[key])
				except AttributeError:
					pass

		seq = self.session.get_resource(self.source)
		if not isinstance(seq, SequenceResource):
			raise pyseq.ResourceQueryError('Can not load resources other than SequenceResource')
		try:
			self.data = list(seq.getData())[self.offset:self.limit]
		except IndexError:
			raise pyseq.ResourceQueryError('Can not satisfy offset %d or limit %d' % (self.offset, self.limit))
		self.cols = max([len(d) for d in self.data])
		self.rows = len(self.data)
		self.touch()
		return {'columns':self.cols, 'rows':self.rows, 'width':self.cols*self.fieldsize,'height':self.rows*self.fieldsize}

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
		
	def draw(self, context, clipping):
		# Shortcuts
		cminx, cminy, cmaxx, cmaxy = clipping
		w,h = cmaxx-cminx, cmaxy-cminy
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
		pyseq.renderer.draw_stripes(c, cminx, cminy, w, h, (fieldsize*10), color["section1"], color["section2"])

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

pyseq.register_plugin("SequenceView", SequenceView)
















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
