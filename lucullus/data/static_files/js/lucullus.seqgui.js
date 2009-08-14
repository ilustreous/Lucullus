/**
 * Used for UserInteraction
 * @constructor
 */

function SeqGui(api, root) {
	var self = this
	this.api = api
	this.root = root
	this.ml = new Lucullus.MoveListenerFactory()

	this.sequence = null
		
	$('tr', this.root).hide()
	$('tr td', this.root).css('padding','0px')
	$('tr.status', this.root).show()
		
	this.status('Preparing...')
		
	$('form.upload:first', this.root).bind('submit', function(event) {
		event.preventDefault()
		event.stopPropagation()
		var file = $('input:first',event.target).val()
		var format = $('select:first',event.target).val()
		self.upload(file, format)
	})
	
	this.status('Waiting for sequence upload...')
}
	
SeqGui.prototype.status = function(txt) {
	$('tr.status td.text:first', this.root).html(txt)
}

SeqGui.prototype.upload = function(file, format){
	this.status('Starting Upload. File: '+file+' Format: '+format)
	var self = this
	// Request resources
	self.sequence = this.api.create('Sequence', {'source':file, 'format':format, 'fontsize': 12})

	// Upload the textfile
	var uploaded = function(c) {
		if(self.sequence.error) {
		    self.status('Creation of sequence resource failed');
		    $('form.upload', self.root).css('border-color','red')
		    $('form.upload .status', self.root).html(self.sequence.error.message)
		    return
		}
		self.status('Parsing complete. Number of sequences: '+self.sequence.len)
		var node = $('tr.main td.map:first', self.root)
		$('tr.main', self.root).show()
		$('form.upload', self.root).hide()
		self.sequence_map = new Lucullus.ViewMap(node, self.sequence)
		self.ml.addMap(self.sequence_map,1,1)
		self.ml.addLinear(node,1,1)

		self.index = this.api.create("Index", {'fontsize':12})
    	self.ruler = this.api.create("Ruler", {'fontsize':12, 'steps':10})
		self.index.wait( function(){
    		self.sequence.keys().wait(function(c){
				self.names = c.result.keys
    	    	self.index.setup({'keys':self.names})
    	    	self.index.wait(show_index)
				jQuery('#seqjump').change(function(e) {
					self.jump_to(e.target.value)
				})
    		})
		})
		self.ruler.wait(show_ruler)
	}

	// Draw index view
	var show_index = function(c) {
		if(self.index.error) { self.status('Index error: '+self.index.error.message); return }
		var node = $('tr.main td.index:first', self.root)
		$('tr.main', self.root).show()
		self.index_map = new Lucullus.ViewMap(node, self.index)
		self.ml.addMap(self.index_map,0,1)
		self.ml.addLinear(node,0,1)
		self.index_map.set_clipping(0,0,self.sequence.width,self.sequence.height)
	}
	
	// Draw ruler view
	var show_ruler = function(c) {
		if(self.ruler.error) { self.status('Ruler error: '+self.ruler.error.message); return }
		var node = $('tr.control td.ruler:first', self.root)
		$('tr.control', self.root).show()
		self.ruler_map = new Lucullus.ViewMap(node, self.ruler)
		self.ml.addMap(self.ruler_map,1,0)
		self.ml.addJoystick(node,1,0)
		self.ruler_map.set_clipping(0,0,self.sequence.width,self.sequence.height)
	}
	
	self.sequence.wait(uploaded)
}
	
SeqGui.prototype.jump_to = function(name) {
	var self = this
	self.sequence.search({'query':name, 'limit':1}).wait(function(c) {
		if(c.result.matches) {
			if(c.result.matches.length > 0) {
				var index = c.result.matches[0].index
				var height_per_index = self.index_map.get_datasize()[1] / c.result.count
				var focus = (index) * height_per_index
				var movement = focus - self.index_map.get_center()[1]
				self.ml.scroll(0, Math.floor(-movement))
				jQuery('#seqjump').css('background-color','#eeffff')
			} else {
				jQuery('#seqjump').css('background-color','#ffeeee')
			}
		}
	})
}
