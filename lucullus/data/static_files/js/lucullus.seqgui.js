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
        height: 400, minHeight: 200,
        width: 700, minWidth: 400,
        title: "Lucullus Sequence Viewer",
        resizeStop: function(e, ui) { self.on_resize() },
        close: function() {self.on_close()}
    }).css('padding','3px').addClass('seqgui').css('overflow','hidden')

    this.nTabs = $('<div class="tabs"/>')
    this.nTabs.append($('<a>Load</a>').click(function(){
        self.eUpload.show()
    }))
    this.nTabs.append($('<a>Search</a>').click(function(){
        self.eSearch.show()
    }))
    this.nTabs.append($('<a>Settings</a>').click(function(){
        self.eSettings.show()
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
    this.eHelp = new SeqHelpDialog()
    this.eSettings = new SeqSettingsDialog(this.eData)
    this.eUpload = new SeqUploadDialog(function(file, type, compression) {
        self.upload(file, type, compression)
    })
    this.eSearch = new SeqSearchDialog(function(name, offset) {return self.eData.jump_to(name, offset)})
    this.eUpload.show()
}

/* Uploads a file and returns a trigger */
SeqGui.prototype.upload = function(file, type, compression) {
    var self = this
    var t = this.eData.upload(file, type, compression)
    t.wait(function(c) {
        if(c.error) {
            self.eUpload.status(c.error.message)
        } else {
            self.nDialog.dialog('option', 'title', 'Lucullus ('+file+')')
            self.eUpload.hide()
            self.on_resize()
        }
    })
    return t
}

SeqGui.prototype.focus = function(name) {
    this.eData.jump_to(q)
}

SeqGui.prototype.on_close = function() {
    this.eData.on_close()
}

SeqGui.prototype.on_resize = function(w, h) {
    var x = this.nDialog.innerWidth()
    x -= this.nDialog.css('padding-left').replace('px','')
    x -= this.nDialog.css('padding-right').replace('px','')
    var y = this.nDialog.innerHeight()
    y -= this.nTabs.outerHeight(true)
    y -= this.nDialog.css('padding-top').replace('px','')
    y -= this.nDialog.css('padding-bottom').replace('px','')
    y -= this.nDialog.css('pading-top').replace('px','')
    y -= this.nDialog.css('pading-bottom').replace('px','')
    y -= this.nDialog.css('border-top-width').replace('px','')
    y -= this.nDialog.css('border-bottom-width').replace('px','')
    y -= this.nDialog.css('margin-top').replace('px','')
    y -= this.nDialog.css('margin-bottom').replace('px','')
    this.eData.resize(Math.floor(x), Math.floor(y))
}

SeqGui.prototype.zoom = function(value) {
    return this.eData.zoom(value)
}










function SeqHelpDialog() {
    this.nRoot = $('<div />').attr('title','Help').dialog({
        autoOpen: false, buttons: {
            Ok: function() {
                $(this).dialog('close');
            }
        }
    })
    this.nRoot.html('Help meee')
}

SeqHelpDialog.prototype.show = function() {this.nRoot.dialog('open', true)}
SeqHelpDialog.prototype.hide = function() {this.nRoot.dialog('close', true)}










function SeqSettingsDialog(eData) {
    this.eData = eData
    var self = this
    this.nRoot = $('<div />').attr('title','Settings').dialog({
        autoOpen: false, buttons: {
            Ok: function() {
                $(this).dialog('close');
            }
        }
    })
    this.nZoomSlider = $('<div />')
    this.nRoot.append($('<h2>Zoom: <span class="zoomlevel">12</span></h2>'))
    this.nRoot.append(this.nZoomSlider)
    this.nZoomSlider.slider({
        min:1, max:24,
        stop: function(e, ui) {
            self.eData.zoom(Math.ceil(ui.value))
        },
        slide: function(e, ui) {
            self.nRoot.find('span.zoomlevel').html(Math.ceil(ui.value))
        }})
    this.nIndexCheckbox = $('<input type="checkbox" value="yes" />')
    this.nRoot.append($('<h2>View:</h2>'))
    this.nRoot.append(this.nIndexCheckbox)
    this.nIndexCheckbox.attr('checked', this.eData.lIndexWidth ? true : false)
    this.nIndexCheckbox.change(function(e) {
        if(this.checked) {
            self.eData.lIndexWidth = 100
            self.eData.refresh()
        } else {
            self.eData.lIndexWidth = 0            
            self.eData.refresh()
        }
    })
}

SeqSettingsDialog.prototype.show = function() {
    this.nRoot.dialog('open', true)
    this.nZoomSlider.slider('value', this.eData.lZoom)
    this.nRoot.find('h2 span').html(this.eData.lZoom)
}
SeqSettingsDialog.prototype.hide = function() {this.nRoot.dialog('close', true)}










function SeqUploadDialog(on_upload) {
    var self = this
    this.stdtext = 'You can upload fasta files up to 30MB in size with any number of sequences.'
    this.do_upload = on_upload

    this.nRoot = $('<div />').attr('title','Fiel Upload').addClass('seqgui').empty()
    this.nForm = $('<form />')
    this.nRoot.append($('<p />').addClass('status').text(this.stdtext))
    this.nStatus = $('<div>').css('color','red')
    this.nForm.append($('<label for="upUrl" />').text('File'))
    this.nForm.append($('<input type="text" name="upUrl" />').addClass('text').val(jQuery.query.get('upUrl')))
    this.nForm.append($('<label for="format" />').text('Format'))
    this.nForm.append($('<select />').attr('name','format')
        .append($('<option />').val('fasta').text('fasta')))
    this.nForm.append($('<label for="packed" />').text('Compression'))
    this.nForm.append($('<select />').attr('name','packed')
        .append($('<option />').val('raw').text('none'))
        .append($('<option />').val('gzip').text('gzip'))
        .append($('<option />').val('bzip2').text('bzip2')))
    this.nForm.append(this.nStatus)
    this.nRoot.append(this.nForm)
    
    this.nForm.submit(function(e) {
        var url = self.nForm.find('input[name="upUrl"]').val()
        var format = self.nForm.find('select[name="format"]').val()
        var packed = self.nForm.find('select[name="packed"]').val()
        self.do_upload(url, format, packed)
        self.nRoot.find('.status').text('Uploading '+url+' ('+format+'). This may take a while...')
        self.nForm.hide('slow')
        return false
    })

    this.nRoot.dialog({
        autoOpen: false,
        modal: true,
        width: 500,
        close: function(e, ui) {
            self.nRoot.find('.status').text(self.stdtext)
            self.nForm.show()
        },
        buttons: {
        Abort: function() {
            $(this).dialog('close');
        }, 
        Upload: function() {
            self.nForm.submit();
        }
    }})
}

SeqUploadDialog.prototype.show = function() {this.nRoot.dialog('open', true)}
SeqUploadDialog.prototype.hide = function() {this.nRoot.dialog('close', true)}


SeqUploadDialog.prototype.status = function(msg) {
    this.nStatus.text(msg)
}










function SeqSearchDialog(on_search) {
    var self = this
    this.search = on_search

    this.nRoot = $('<div />' ).attr('title','Sequence Search').addClass('seqgui')
    this.nStatus = $('<div />').text("Enter your search query")
    this.nForm = $('<form />')
    this.nForm.append($('<label for="q" />').text('Name'))
    this.nForm.append($('<input type="text" name="q" />').addClass('text'))
    this.nForm.append(this.nStatus)
    this.nRoot.empty().append(this.nForm)
    // This is used to determine the visibility of the 'Next' button
    this.offset = 0
    this.lastsearch = ''

    this.nForm.submit(function(e) {
        var q = self.nForm.find('input[name="q"]').val()
        if(q == self.lastsearch) {
            self.offset = 0
            self.lastsearch = q
        }
        if(q) {
            var t = self.search(q, self.offset)
            t.wait(function(c) {
                if(c.result.matches) {
                    if(c.result.matches.length > 0) {
                        if(self.offset >= c.result.matches.length - 1) {
                            self.offset = c.result.matches.length - 1
                            self.nRoot.parent().find("button:contains(Next)").hide()
                        } else {
                            self.nRoot.parent().find("button:contains(Next)").show()
                        }
                        
                        self.nStatus.html("Search completed. Jumped to "+(self.offset+1)+" out of "+c.result.matches.length+" results: <b>"+c.result.matches[0].name+'</b>')
                    } else {
                        self.nRoot.parent().find("button:contains(Next)").hide()
                        self.nStatus.text("Search string not found.")
                    }
                }
            })
        } else {
            self.nStatus.text("Please enter a seqrch query first")
        }
        return false
    })

    this.nRoot.dialog({
        autoOpen: false,
        zIndex: 4000,
        close: function() {
            self.offset = 0
            self.nRoot.parent().find("button:contains(Next)").hide()
        },
        buttons:{
            Next: function() {
                var offset = self.nForm.find('input[name="offset"]').val() || '0'
                self.offset += 1
                self.nForm.submit();
            },
            Search: function() {
                self.offset = 0
                self.nForm.submit();
            },
            Abort: function() {
                $(this).dialog('close');
            }, 
        }
    })
    self.nRoot.parent().find("button:contains(Next)").hide()
}

SeqSearchDialog.prototype.show = function() {this.nRoot.dialog('open', true).dialog( 'moveToTop' )}
SeqSearchDialog.prototype.hide = function() {this.nRoot.dialog('close', true)}










function SeqDataTable(api, root) {
    var self = this
    // Settings
    this.api = api
    this.ml = new Lucullus.MoveListenerFactory()

    // Layout
    this.lZoom = 12 // zoom level
    this.lIndexWidth = 100 // width of index column
    this.lRulerHeight = 20 // height if ruler rw
    this.lSliderWidth = 16
    this.lSliderHeight = 16
    this.lTableWidth = 0
    this.lTableHeight = 0
    
    // Settings
    this.sShowCompare = false

    // HTML Nodes
    this.nRoot = $(root)
    this.nRoot.empty()

    this.nStatus = $('<div />')
    this.nRoot.append(this.nStatus)

    this.nTable = $('<table><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr><td></td><td></td><td></td></tr></table>')
    this.nTableTDs = this.nTable.find('td')
    this.nSeq = this.nTable.find('tr:eq(2) td:eq(1)')
    this.nIndex = this.nTable.find('tr:eq(2) td:eq(0)')
    this.nSeq2 = this.nTable.find('tr:eq(1) td:eq(1)')
    this.nIndex2 = this.nTable.find('tr:eq(1) td:eq(0)')
    this.nRuler = this.nTable.find('tr:eq(0) td:eq(1)')
    this.nRoot.append(this.nTable.hide())

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
    this.nSeq.css('border','1px solid lightgrey')
    this.nSeq2.css('border','1px solid lightgrey')
    this.nIndex.css('border','1px solid lightgrey')
    this.nIndex2.css('border','1px solid lightgrey')
    this.nRuler.css('border','1px solid lightgrey')
    
    
    // GUI elements (init, prepare and setup)
    this.eStatus = this.nStatus
    this.status('Initilalizing...')

    this.nHSlider = $('<div />')
    this.nTable.find('tr:eq(3) td:eq(1)').append(this.nHSlider)
    this.nHSlider.slider({
        min:0, max:0,
        stop: function(e, ui) {
            self.slide_to(Math.max(1,ui.value), null)
        },
        slide: function(e, ui) {
            self.status("Jump to sequence position: " + Math.max(1,ui.value) +"/"+self.eSeqMap.view.columns)
        }})

    this.nVSlider = $('<div />')
    this.nTable.find('tr:eq(2) td:eq(2)').append(this.nVSlider)
    this.nVSlider.slider({
        orientation: "vertical", 
        min:0, max:0,
        stop: function(e, ui) {
            self.slide_to(null, Math.max(1,self.eSeqMap.view.rows - ui.value))
        },
        slide: function(e, ui) {
            var p = Math.max(1,self.eSeqMap.view.rows - ui.value)
            self.status("Jump to sequence number: " + p +"/"+self.eSeqMap.view.rows + ' (' + self.names[p-1] +')')
        }})

    this.eSeqMap = new Lucullus.ViewMap(this.nSeq,
        this.api.create('Sequence', {'fontsize': this.lZoom}))
    this.eIndexMap = new Lucullus.ViewMap(this.nIndex,
        this.api.create('Index', {'fontsize': this.lZoom}))
    this.eSeq2Map = new Lucullus.ViewMap(this.nSeq2,
        this.api.create('Sequence', {'fontsize': this.lZoom}))
    this.eIndex2Map = new Lucullus.ViewMap(this.nIndex2,
        this.api.create('Index', {'fontsize': this.lZoom}))
    this.eRulerMap = new Lucullus.ViewMap(this.nRuler,
        this.api.create('Ruler', {'fontsize':Math.floor(this.lZoom*0.8)}))

    this.eSeqMap.cMove = function() { 
        self.update_slider()
    }

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

SeqDataTable.prototype.zoom = function(value) {
    this.lZoom = value
    var size = this.eSeqMap.get_datasize()
    var pos = this.eSeqMap.get_position()

    var self = this
    this.eRulerMap.view.query('setup', {'fontsize':this.lZoom}).wait(function(){
        self.eRulerMap.refresh()
    })
    this.eSeqMap.view.query('setup', {'fontsize':this.lZoom}).wait(function(){
        self.eSeqMap.refresh()
        var nsize = self.eSeqMap.get_datasize()
        var foo = [Math.floor(pos[0]*nsize[0]/size[0]), Math.floor(pos[1]*nsize[1]/size[1])]
        self.ml.move_to(-foo[0], -foo[1])
    })
    this.eSeq2Map.view.query('setup', {'fontsize':this.lZoom}).wait(function(){
        self.eSeq2Map.refresh()
    })
    this.eIndexMap.view.query('setup', {'fontsize':this.lZoom}).wait(function(){
        self.eIndexMap.refresh()
    })
    this.eIndex2Map.view.query('setup', {'fontsize':this.lZoom}).wait(function(){
        self.eIndex2Map.refresh()
    })

}

SeqDataTable.prototype.on_close = function() {
    this.eRulerMap.view.close()
    this.eSeqMap.view.close()
    this.eSeq2Map.view.close()
    this.eIndexMap.view.close()
    this.eIndex2Map.view.close()
}

SeqDataTable.prototype.update_slider = function() {
    if(this.eSeqMap && this.eSeqMap.get_datasize()[0] && this.eSeqMap.get_datasize()[1]) {
        var x = this.eSeqMap.view.columns * (this.eSeqMap.get_position()[0] / (this.eSeqMap.get_datasize()[0] - this.eSeqMap.get_size()[0]))
        var y = this.eSeqMap.view.rows * (this.eSeqMap.get_position()[1] / (this.eSeqMap.get_datasize()[1] - this.eSeqMap.get_size()[1]))
        this.nHSlider.slider('value', x)
        this.nVSlider.slider('value', this.eSeqMap.view.rows - y)
    }
}

SeqDataTable.prototype.refresh = function() {
    this.resize(this.lTableWidth, this.lTableHeight)
}

SeqDataTable.prototype.resize = function(sw, sh) {
    // Firefox bug...
    this.nTable.css('border-collapse','separate').css('border-collapse','collapse')
    this.lTableWidth = sw
    this.lTableHeight = sh
    // Wether the table element resizes
    var ch = this.lZoom
    if(!this.sShowCompare) ch = 0
    sw -= 4 // Borders
    sh -= 5 // Borders
    sh -= this.nStatus.outerHeight(true)

    if(this.eSeqMap) {
        this.eRulerMap.resize(sw-this.lIndexWidth-this.lSliderWidth, this.lRulerHeight)
        this.eSeqMap.resize(sw-this.lIndexWidth-this.lSliderWidth, sh-ch-this.lRulerHeight-this.lSliderHeight)
        this.eIndexMap.resize(this.lIndexWidth, sh-ch-this.lRulerHeight-this.lSliderHeight)
        this.eSeq2Map.resize(sw-this.lIndexWidth-this.lSliderWidth, ch)
        this.eIndex2Map.resize(this.lIndexWidth, ch)
        this.nVSlider.height(sh-ch-this.lRulerHeight-this.lSliderHeight-2)
        this.nHSlider.width(sw-this.lIndexWidth-this.lSliderWidth-2)
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
    var trigger = new Lucullus.util.Trigger() 
    var self = this
    self.nTable.hide()
    // Request resources
    self.eSeqMap.view.wait(function(){
        self.eSeqMap.view.query('setup', {'source':file, 'format':format})
        self.eSeqMap.view.wait( function(c) {
            trigger.finish(c) // Do this before recover()ing from errors, so the callbacks can display the error message.
            if(c.error) {
                self.status('Upload failed: '+c.error.error)
                c.finish(c.error)
                self.eSeqMap.view.recover()
                return
            }
            self.nTable.show()
            self.eSeqMap.refresh()
            self.nHSlider.slider('option', 'max', self.eSeqMap.view.columns)
            self.nVSlider.slider('option', 'max', self.eSeqMap.view.rows)
            self.update_slider()
            self.eRulerMap.set_clipping(0,0,self.eSeqMap.get_datasize()[0], self.lRulerHeight)
            self.status('Parsing complete. Number of sequences: '+self.eSeqMap.view.len)
            self.eSeqMap.view.keys().wait(function(c){
                if(c.error) {
                    self.status('Failed to build an index: '+self.eSeqMap.view.error.message)
                }
                self.names = c.result.keys
                self.eIndexMap.view.query('setup', {'keys':self.names})
                self.eIndexMap.view.wait(function(){
                    self.eIndexMap.refresh()
                })
            })
        })
    })
    return trigger
}

SeqDataTable.prototype.jump_to = function(name, offset) {
    var self = this
    var trigger = self.eSeqMap.view.search({'query':name, 'limit':100})
    var offset = parseInt(offset) || 0
    trigger.wait(function(c){
        if(c.result && c.result.matches && c.result.matches.length > offset) {
            var index = c.result.matches[offset].index
            var height_per_index = self.eIndexMap.get_datasize()[1] / c.result.count
            var target = (index) * height_per_index
            target -= self.eIndexMap.get_size()[1] / 2
            self.ml.scroll_to(null, Math.floor(-target))
        }
    })
    return trigger
}

SeqDataTable.prototype.slide_to = function(x, y) {
    // new_position = (data_size - window_size) * (jump_to_column / num_columns)
    if(x) x = -Math.floor((this.eSeqMap.get_datasize()[0] - this.eSeqMap.get_size()[0]) * x / this.eSeqMap.view.columns)
    if(y) y = -Math.floor((this.eSeqMap.get_datasize()[1] - this.eSeqMap.get_size()[1]) * y / this.eSeqMap.view.rows)
    this.ml.move_to(x, y)
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
    if(self.eSeqMap && self.eSeqMap.view)
        return self.eSeqMap.view.columns
    else
        return 0
}
