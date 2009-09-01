/**
 * Used for UserInteraction
 * @constructor
 */

/*
SeqGui
  SeqHelp
  SeqUpload
  SeqData
    SeqDataTable
    SeqSlider
    SeqSearch
    SeqInfo[]


*/

function SeqGui(api) {
    if(typeof SeqGui.id == 'undefined') SeqGui.id = 0
    this.id = SeqGui.id++
    var self = this
    this.api = api

    this.nDialog = $('<div></div>').dialog({
        height:400, minHeight: 200,
        width:700, minWidth: 400,
        title: "Lucullus Sequence Viewer",
        resizeStop: function(e, ui) { self.on_resize() }
    }).css('padding','3px').addClass('seqgui').css('overflow','hidden')

    this.nTabs = $('<div class="tabs"/>')
    this.nTabs.append($('<a>Upload</a>').click(function(){
        self.eUpload.show()
    }))
    this.nTabs.append($('<a>Help</a>').click(function(){
        self.eHelp.show()
    }))
    this.nTabs.find('a').addClass('tab').attr('href','#')
    /*this.nTabs.find('a').click(function(e) {
        var n = $(this).prevAll().length
        self.nDialog.find('div.tabcontent').hide()
        self.nDialog.find('a.tab').removeClass('tab_selected')
        $(this).addClass('tab_selected')
        self.nTabs.find('siv.tabcontent:visible').hide()
        self.nDialog.find('div.tabcontent:eq('+n+')').show()
        return true
    })*/

    this.nData = $('<div />')

    this.nDialog.append(this.nTabs)
    this.nDialog.append(this.nData)

    this.eData = new SeqDataTable(this.api, this.nData)
    this.eHelp = new SeqHelp()
    this.eUpload = new SeqUpload(function(file, type, compression) {
        self.upload(file, type, compression)
    })
    this.eUpload.show()
}


SeqGui.prototype.upload = function(file, type, compression) {
    var self = this
    this.eData.upload(file, type, compression).wait(function(c) {
        if(c.error) {
            self.eUpload.status(c.error.message)
        } else {
            self.nDialog.dialog('option', 'title', 'Lucullus ('+file+')')
            self.eUpload.hide()
            self.on_resize()
        }
    })
}

SeqGui.prototype.on_resize = function(w, h) {
    var x = this.nDialog.innerWidth()
    x -= this.nDialog.css('padding-left').replace('px','')
    x -= this.nDialog.css('padding-right').replace('px','')
    var y = this.nDialog.innerHeight()
    y -= this.nTabs.find('ul:first').outerHeight(true)
    y -= this.nDialog.css('padding-top').replace('px','')
    y -= this.nDialog.css('padding-bottom').replace('px','')
    y -= this.nDialog.css('pading-top').replace('px','')
    y -= this.nDialog.css('pading-bottom').replace('px','')
    y -= this.nDialog.css('border-top-width').replace('px','')
    y -= this.nDialog.css('border-bottom-width').replace('px','')
    y -= this.nDialog.css('margin-top').replace('px','')
    y -= this.nDialog.css('margin-bottom').replace('px','')
    this.eData.resize(Math.floor(x), Math.floor(y)-100)
}

function SeqHelp(root) {
    this.nRoot = $('<div />').attr('title','Help').dialog({autoOpen: false})
    this.nRoot.html('Help meee')
}

SeqHelp.prototype.show = function() {this.nRoot.dialog('open', true)}
SeqHelp.prototype.hide = function() {this.nRoot.dialog('close', true)}


function SeqUpload(on_upload) {
    var self = this
    this.nRoot = $('<div />').attr('title','Fiel Upload').dialog({autoOpen: false, modal: true, width: 500, show: 'slide'})
    this.do_upload = on_upload
    
    this.nForm = $('<form />')
    this.nStatus = $('<div>').css('color','red')
    this.nForm.append($('<label for="upUrl" />').text('File').css('display','block'))
    this.nForm.append($('<input type="text" name="upUrl" />'))
    this.nForm.append($('<select />').attr('name','format')
        .append($('<option />').val('fasta').text('Fasta')))
    this.nForm.append($('<select />').attr('name','packed')
        .append($('<option />').val('raw').text(''))
        .append($('<option />').val('zip').text('.zip'))
        .append($('<option />').val('gzip').text('.gzip'))
        .append($('<option />').val('bzip2').text('.bzip2')))
    this.nForm.append($('<input type="submit" name="submit" />').val('Upload'))
    this.nForm.append(this.nStatus)
    this.nRoot.empty().append(this.nForm)

    this.nForm.submit(function(e) {
        var url = self.nForm.find('input[name="upUrl"]').val()
		var format = self.nForm.find('select[name="format"]').val()
		var packed = self.nForm.find('select[name="packed"]').val()
		self.do_upload(url, format, packed)
		return false
    })
}

SeqUpload.prototype.show = function() {this.nRoot.dialog('open', true)}
SeqUpload.prototype.hide = function() {this.nRoot.dialog('close', true)}


SeqUpload.prototype.status = function(msg) {
    this.nStatus.text(msg)
}


function SeqSlider(data_table, root) {
    var self = this
    this.dt = data_table
    this.node = $('<div />').css('height','100px')
    this.node.slider({
		min:0, max:100,
		stop: function(e, ui) {
			self.dt.slide_to(self.dt.get_columns() * ui.value / 100, null)
		},
		slide: function(e, ui) {
			self.status("Slide to: " + Math.ceil(self.dt.get_columns() * ui.value / 100) + "/" + self.dt.get_columns())
		},
		orientation: "vertical"
	})
}



function SeqDataTable(api, root) {
	var self = this
	// Settings
	this.api = api
	this.ml = new Lucullus.MoveListenerFactory()

	// Layout
	this.lZoom = 12	// zoom level
	this.lIndexWidth = 100 // width of index column
	this.lRulerHeight = 20 // height if ruler rw
	this.lSliderWidth = 12
	this.lSliderHeight = 12
	
	// Settings
	this.sShowCompare = false

	// HTML Nodes
	this.nRoot = $(root)
    this.nRoot.empty()
	this.nTable = $('<table><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr><td></td><td></td><td></td></tr></table>')
	this.nTableTDs = this.nTable.find('td')
	this.nSeq = this.nTable.find('tr:eq(2) td:eq(1)')
	this.nIndex = this.nTable.find('tr:eq(2) td:eq(0)')
	this.nSeq2 = this.nTable.find('tr:eq(1) td:eq(1)')
	this.nIndex2 = this.nTable.find('tr:eq(1) td:eq(0)')
	this.nRuler = this.nTable.find('tr:eq(0) td:eq(1)')
	this.nRoot.append(this.nTable)

	this.nStatus = $('<div />')
	this.nRoot.append(this.nStatus)

	this.nSearch = $('<form />')
	this.nRoot.append(this.nSearch)

	// Show/Hide everyting
	this.nTable.find('tr:eq(1) td').hide()
	this.nStatus.show()

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

	this.nHSlider = $('<div />')
	this.nTable.find('tr:eq(3) td:eq(1)').append(this.nHSlider)
	this.nHSlider.slider()

	this.nVSlider = $('<div />')
	this.nTable.find('tr:eq(2) td:eq(2)').append(this.nVSlider)
	this.nVSlider.slider({orientation: "vertical"})

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
	/*this.eSlider = this.nSlider.css('height', '100px').slider({
		min:0, max:0,
		stop: function(e, ui) {
			self.slide_to(ui.value, null)
		},
		slide: function(e, ui) {
			self.status("Slide to: " + ui.value +"/"+self.eSeqMap.view.columns)
		},
		
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
	})*/


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
}


SeqDataTable.prototype.status = function(txt) {
	this.eStatus.text(txt)
}

SeqDataTable.prototype.resize = function(sw, sh) {
    // Firefox bug...
	this.nTable.css('border-collapse','separate').css('border-collapse','collapse')
	// Wether the table element resizes
	var ch = this.lZoom
	if(!this.sShowCompare) ch = 0
	if(this.eSeqMap) {
    	this.eRulerMap.resize(sw-this.lIndexWidth-this.lSliderWidth-4, this.lRulerHeight)
    	this.eSeqMap.resize(sw-this.lIndexWidth-this.lSliderWidth-4, sh-ch-this.lRulerHeight-this.lSliderHeight-5)
    	this.eIndexMap.resize(this.lIndexWidth, sh-ch-this.lRulerHeight-this.lSliderHeight-5)
    	this.eSeq2Map.resize(sw-this.lIndexWidth-this.lSliderWidth-4, ch)
    	this.eIndex2Map.resize(this.lIndexWidth, ch)
    	this.nVSlider.height(sh-ch-this.lRulerHeight-this.lSliderHeight-1-5)
    	this.nHSlider.width(sw-this.lIndexWidth-this.lSliderWidth-1-4)
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

SeqDataTable.prototype.upload = function(file, format, compression){
	this.status('Starting Upload. File: '+file+' Format: '+format)
    var trigger = new Lucullus.Trigger() 
	var self = this
	// Request resources
	self.eSeqMap.view.wait(function(){
		self.eSeqMap.view.setup({'source':file, 'format':format})
		self.eSeqMap.view.wait( function(c) {
		    trigger.finish(c) // Do this before recover()ing from errors, so the callbacks can display the error message.
			if(c.error) {
				self.status('Upload failed: '+self.eSeqMap.view.error.message)
				self.eSeqMap.view.recover()
				return
			}
			self.eSeqMap.refresh()
			//self.eSlider.slider('option', 'max', self.eSeqMap.view.columns)
			self.eRulerMap.set_clipping(0,0,self.eSeqMap.get_datasize()[0], self.lRulerHeight)
			self.status('Parsing complete. Number of sequences: '+self.eSeqMap.view.len)
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
	return trigger
}
	
SeqDataTable.prototype.jump_to = function(name) {
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

SeqDataTable.prototype.slide_to = function(pos) {
	// new_position = (data_size - window_size) * (jump_to_column / num_columns)
	var target = (this.eSeqMap.get_datasize()[0] - this.eSeqMap.get_size()[0]) * pos / this.eSeqMap.view.columns
	this.ml.scroll_to(Math.floor(-target), null)
}

SeqDataTable.prototype.position_info = function(x,y) {
	var self = this
	self.eSeqMap.view.posinfo({'x':x, 'y':y}).wait(function(c) {
		if(c.result.key) {
			self.status("Sequence: "+c.result.key+" (Position: "+c.result.seqpos+", Value: "+c.result.value+")")
		} else {
			self.status("Sequence: None - Position: None")
		}
	})
}

SeqDataTable.prototype.get_columns = function() {
    if(self.eSeqMap && self.eSeqMal.view)
	    return self.eSeqMap.view.columns
	else
	    return 0
}
