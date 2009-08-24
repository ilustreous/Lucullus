/**
 * Used for UserInteraction
 * @constructor
 */

function SeqGui(api, root) {
	var self = this
	// Settings
	this.api = api
	this.ml = new Lucullus.MoveListenerFactory()

	// Layout
	this.lZoom = 12	// zoom level
	this.lIndexWidth = 100 // width of index column
	this.lRulerHeight = 20 // height if ruler rw
	
	// Settings
	this.sShowCompare = false

	// HTML Nodes
	this.nRoot = $(root)
	this.nTable = this.nRoot.find('table.guitable')
	this.nTableTDs = this.nTable.find('td')
	this.nSeq = this.nTable.find('tr.main td.map')
	this.nIndex = this.nTable.find('tr.main td.index')
	this.nSeq2 = this.nTable.find('tr.compare td.map')
	this.nIndex2 = this.nTable.find('tr.compare td.index')
	this.nRuler = this.nTable.find('tr.control td.ruler')
	this.nSlider = this.nRoot.find('div.slider')
	this.nStatus = this.nRoot.find('div.status') // May be more than one
	this.nUpload = this.nRoot.find('div.upload')
	this.nSearch = this.nRoot.find('form.search')

	// Show/Hide everyting
	this.nTable.show()
	this.nTable.find('*').show()
	this.nSeq2.hide()
	this.nIndex2.hide()
	this.nStatus.show()
	this.nSlider.show()
	this.nUpload.hide()

	// Clean up and null out everythng
	this.nTable.css('padding','').css('border-spacing','0px')	
	this.nTable.find('td').empty()
	this.nTable.find('tr,td')
		.css('width','')
		.css('height','')
		.css('padding','0')
		.css('margin','0')
		.css('border','1px solid grey')

	// GUI elements (init, prepare and setup)
	this.eStatus = this.nStatus
	this.status('Initilalizing...')

	this.eSeqMap = new Lucullus.ViewMap(this.nSeq,
		this.api.create('Sequence', {'fontsize': this.lZoom}))
	this.eIndexMap = new Lucullus.ViewMap(this.nIndex,
		this.api.create('Index', {'fontsize': this.lZoom}))
	this.eSeq2Map = new Lucullus.ViewMap(this.nSeq2,
		this.api.create('Sequence', {'fontsize': this.lZoom}))
	this.eIndex2Map = new Lucullus.ViewMap(this.nIndex2,
		this.api.create('Index', {'fontsize': this.lZoom}))
	this.eRulerMap = new Lucullus.ViewMap(this.nRuler,
		this.api.create('Ruler', {'fontsize':Math.floor(this.lZoom*0.8), 'step':this.lZoom}))
	this.eUpload = this.nUpload.dialog({ autoOpen: false, width: this.nUpload.width() })
	this.nUpload.find('form').bind('submit', function(e) {
		self.lock_upload_dialog()
		url    = self.nUpload.find('input[name="upUrl"]').val()
		format = self.nUpload.find('select[name="format"]').val()
		packed = self.nUpload.find('select[name="packed"]').val()
		self.upload(url, format, packed)
		return false
	})
	this.eSlider = this.nSlider.slider({
		min:0, max:0,
		stop: function(e, ui) {
			self.slide_to(ui.value, null)
		},
		slide: function(e, ui) {
			self.status("Slide to: " + ui.value +"/"+self.eSeqMap.view.columns)
		}
	})
	this.eSeqMap.cMove = function() { 
		if(self.eSeqMap && self.eSeqMap.get_datasize()[0]) {
			var pos = self.eSeqMap.view.columns * (self.eSeqMap.get_position()[0] / (self.eSeqMap.get_datasize()[0] - self.eSeqMap.get_size()[0]))
			self.eSlider.slider('value', pos)
		}	
	}
	this.nSearch.find('form').bind('submit', function(e) {
		self.jump_to(self.nSearch.find('input[name="q"]').val())
		return false
	})


	// Absolutize table size and recalculate column/row sizes
	this.resize(this.nTable.width(), this.nTable.height())


	this.status('Adding mouse gestures...')
	// Move and dblclick listener
	this.ml.addMap(this.eSeqMap,1,1)
	this.ml.addLinear(this.eSeqMap.node,1,1)
	this.ml.addMap(this.eSeq2Map,1,1)
	this.ml.addLinear(this.eSeq2Map.node,1,1)
	this.ml.addMap(this.eIndexMap,0,1)
	this.ml.addLinear(this.eIndexMap.node,1,1)
	this.ml.addMap(this.eIndex2Map,0,1)
	this.ml.addLinear(this.eIndex2Map.node,1,1)
	this.ml.addMap(this.eRulerMap,1,0)
	this.ml.addJoystick(this.eRulerMap.node,1,0)
	this.eSeqMap.node.dblclick(function(e) {
		var p = self.eSeqMap.get_position_by_absolute(e.pageX, e.pageY)
		self.position_info(p[0], p[1])
	})
	this.status('Waiting for file upload...')
	this.open_upload_dialog()

}


SeqGui.prototype.status = function(txt) {
	this.eStatus.text(txt)
}

SeqGui.prototype.resize = function(sw, sh) {
    // Firefox bug...
	this.nTable.css('border-collapse','separate').css('border-collapse','collapse')
	// Wether the table element resizes
	var ch = this.lZoom
	if(!this.sShowCompare) ch = 0
	if(this.eSeqMap) {
    	this.eRulerMap.resize(sw-this.lIndexWidth, this.lRulerHeight)
    	this.eSeqMap.resize(sw-this.lIndexWidth, sh-ch-this.lRulerHeight)
    	this.eIndexMap.resize(this.lIndexWidth, sh-ch-this.lRulerHeight)
    	this.eSeq2Map.resize(sw-this.lIndexWidth, ch)
    	this.eIndex2Map.resize(this.lIndexWidth, ch)
    }
	this.nTable.width(sw)
	this.nTable.height(sh)

	/*
	this.nTable.find('tr td:nth-child(1)').width(this.lIndexWidth) // index/logo width
	this.nTable.find('tr td:nth-child(2)').width(sw-this.lIndexWidth) // ruler/map width
	this.nTable.find('tr:nth-child(1) td').height(this.lRulerHeight) // ruler/logo height
	this.nTable.find('tr:nth-child(2) td').height(ch) // compare height
	this.nTable.find('tr:nth-child(3) td').height(sh-ch-this.lRulerHeight-ch) // main height
	*/
}

SeqGui.prototype.open_upload_dialog = function(txt) {
	// Shows the uplaod dialog
	this.nUpload.dialog('open')
	this.nUpload.find('form,input,select').attr("disabled","");
}

SeqGui.prototype.lock_upload_dialog = function(txt) {
	// Shows the uplaod dialog
	this.nUpload.find('form,input,select').attr("disabled","disabled");
}

SeqGui.prototype.close_upload_dialog = function(txt) {
	// Shows the uplaod dialog
	this.nUpload.dialog('close')
}

SeqGui.prototype.upload = function(file, format){
	this.status('Starting Upload. File: '+file+' Format: '+format)

	var self = this
	// Request resources
	self.eSeqMap.view.wait(function(){
		self.eSeqMap.view.setup({'source':file, 'format':format})
		self.eSeqMap.view.wait( function(c) {
			if(c.error) {
				self.status('Upload failed: '+self.eSeqMap.view.error.message)
				self.open_upload_dialog()
				self.eSeqMap.view.recover()
				return
			}
			self.eSeqMap.refresh()
			self.eSlider.slider('option', 'max', self.eSeqMap.view.columns)
			self.eRulerMap.set_clipping(0,0,self.eSeqMap.get_datasize()[0], self.lRulerHeight)
			self.status('Parsing complete. Number of sequences: '+self.eSeqMap.view.len)
			self.close_upload_dialog()
			self.eSeqMap.view.keys().wait(function(c){
				if(c.error) {
					self.status('Failed to build an index: '+self.eSeqMap.view.error.message)
				}
				self.names = c.result.keys
	   	    	self.eIndexMap.view.setup({'keys':self.names})
				self.eIndexMap.view.wait(function(){
					self.eIndexMap.refresh()
				})
	   		})
		})
	})
}
	
SeqGui.prototype.jump_to = function(name) {
	var self = this
	self.eSeqMap.view.search({'query':name, 'limit':1}).wait(function(c) {
		if(c.result.matches) {
			if(c.result.matches.length > 0) {
				var index = c.result.matches[0].index
				var height_per_index = self.index_map.get_datasize()[1] / c.result.count
				var target = (index) * height_per_index
				target -= self.index_map.get_size()[1] / 2
				self.status(target)
				self.ml.scroll_to(null, Math.floor(-target))
				jQuery('#seqjump').css('background-color','#eeffff')
			} else {
				jQuery('#seqjump').css('background-color','#ffeeee')
			}
		}
	})
}

SeqGui.prototype.slide_to = function(pos) {
	// new_position = (data_size - window_size) * (jump_to_column / num_columns)
	var target = (this.eSeqMap.get_datasize()[0] - this.eSeqMap.get_size()[0]) * pos / this.eSeqMap.view.columns
	this.ml.scroll_to(Math.floor(-target), null)
}

SeqGui.prototype.position_info = function(x,y) {
	var self = this
	self.eSeqMap.view.posinfo({'x':x, 'y':y}).wait(function(c) {
		if(c.result.key) {
			self.status("Sequence: "+c.result.key+" (Position: "+c.result.seqpos+", Value: "+c.result.value+")")
		} else {
			self.status("Sequence: None - Position: None")
		}
	})
}

SeqGui.prototype.rows_by_position = function(pos) {
	
}