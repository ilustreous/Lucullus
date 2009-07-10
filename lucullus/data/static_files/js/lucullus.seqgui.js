/**
 * Used for UserInteraction
 * @constructor
 */

function SeqGui(api, root) {
	var self = this
	this.api = api
	this.root = root
	this.ml = new Lucullus.MoveListenerFactory()
	this.ml = new Lucullus.MoveListenerFactory()

	this.sequence = null
	this.compare = null
		
	this.sequence_view = null
	this.compare_view = null

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
	var txt = this.api.create('TextResource','tr')
	var seq = this.api.create('SequenceResource','seq')
	var view = this.api.create('SequenceView','sev')
	var iview = this.api.create("IndexView",'iv')
	var rview = this.api.create("RulerView",'rv')

	// The following code blocks have do be called (and completed) in order.
	// To do this, we /could/ use nested wait() blocks. But thats ugly.
	
	// Upload the textfile
	var upload_txt = function(c) {
		if(txt.error) { self.status('Creation of text Buffer failed'); return }
		if(seq.error) { self.status('Creation of sequence Buffer failed'); return }
		if(view.error) { self.status('Creation of image Buffer failed'); return }
		if(iview.error) { self.status('Creation of index Buffer failed'); return }
		if(rview.error) { self.status('Creation of index Buffer failed'); return }
		txt.load({'uri':file})
		txt.wait(parse_seq)
	}

	// Parse the textfile
	var parse_seq = function(c) {
		if(txt.error) {
			self.status('Upload failed: '+txt.error.message);
			$('form.upload', this.root).css('border-color','red')
			$('form.upload .status', this.root).html(txt.error.message)
			return
		}
		$('form.upload', this.root).css('border-color','green')
		self.status('Upload complete. Filesize: '+txt.size+' bytes')
		seq.load({'source':txt.id})
		seq.wait(load_into_views)
	}

	// Load sequences into views
	var load_into_views = function(c) {
		if(seq.error) { self.status('Parser error: '+seq.error.message); return }
		self.status('Parsing complete. Number of sequences: '+seq.len)
		self.sequence = seq
		view.load({'source':seq.id})
		view.set({'fieldsize': 14})
		iview.load({'source':seq.id})
		iview.set({'lineheight': 14})
		iview.load({'source':seq.id})
		rview.set({'step': 14})
		view.wait(create_seqmap)
		iview.wait(create_indexmap)
		Lucullus.wait([view,rview], create_rulermap)
	}

	// Draw sequence map and configure index view
	var create_seqmap = function(c) {
		if(view.error) { self.status('View error: '+view.error.message); return }
		self.status('Rendering complete. Number of sequences: '+seq.len)
		var node = $('tr.main td.map:first', this.root)
		$('tr.main', this.root).show()
		$('form.upload', this.root).hide()
		var map = new Lucullus.ViewMap(node, view)
		self.ml.addMap(map,1,1)
		self.ml.addLinear(node,1,1)
	}

	// Draw index view
	var create_indexmap = function(c) {
		if(iview.error) { self.status('View error: '+iview.error.message); return }
		var node = $('tr.main td.index:first', this.root)
		$('tr.main', this.root).show()
		var map2 = new Lucullus.ViewMap(node, iview)
		self.ml.addMap(map2,0,1)
		self.ml.addLinear(node,0,1)
	}

	// Draw ruler view
	var create_rulermap = function(c) {
		if(rview.error) { self.status('View error: '+rview.error.message); return }
		var node = $('tr.control td.ruler:first', this.root)
		$('tr.control', this.root).show()
		var map3 = new Lucullus.ViewMap(node, rview)
		self.ml.addMap(map3,1,0)
		self.ml.addJoystick(node,1,0)
	}

	// Wait for resource creation and start it all!
	Lucullus.wait([txt,seq,view,iview, rview], upload_txt)
}
	
	
