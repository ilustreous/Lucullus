Lucullus.ui = new Object()

Lucullus.ui.formfield = function(name, label, node, def) {
    var div = $('<div></div>')
    div.append($('<label>').attr('for', name).text(label+':'))
    div.append($(node).attr('name', name).attr('value', def))
    return div
}


Lucullus.ui.Dialog = function(node, options) {
    var self = this
    this.node = node ? $(node) : $('<div></div>')
    this.node.css('padding','3px').width(500).height(300)
    options = typeof options == 'object' ? options : {}
    options.title = "Lucullus Sequence Viewer"
    options.width = 500
    options.height = 300
    options.resizeStop = function(e, ui) {self.on_resize(e, ui)}
    options.close = function(e, ui) {self.on_close(e, ui)}
    this.node.dialog(options)
}

Lucullus.ui.Dialog.prototype.settitle = function(value) {this.node.dialog('option', 'title', value)}
Lucullus.ui.Dialog.prototype.setwidth = function(value) {this.node.dialog('option', 'width', value)}
Lucullus.ui.Dialog.prototype.setheight = function(value) {this.node.dialog('option', 'height', value)}
Lucullus.ui.Dialog.prototype.setmodal = function(value) {this.node.dialog('option', 'modal', value)}
Lucullus.ui.Dialog.prototype.show = function() {this.node.dialog('open', true)}
Lucullus.ui.Dialog.prototype.hide = function() {this.node.dialog('close', true)}
Lucullus.ui.Dialog.prototype.on_close = function() {}
Lucullus.ui.Dialog.prototype.on_resize = function() {}



Lucullus.ui.Dialog.prototype.autosize = function() {
    this.setheight(this.node.outerHeight())
    this.setwidth(this.node.outerWidth())
}

Lucullus.ui.Upload = function(resource, callback) {
    var self = this
    this.resource = resource
    this.dialog = new Lucullus.ui.Dialog(null, {modal: true})
    this.dialog.settitle('Upload to '+resource.type+'('+resource.id+')')
    this.dialog.setmodal(true)
    this.nForm = $('<form />')
    this.nForm.append(Lucullus.ui.formfield('source','Source', '<input type"text" />', 'http://'))
    this.nForm.append($('<div />').append($('<input>').attr('type', 'submit').val('Submit')))
    this.dialog.node.append(this.nForm)

    this.nForm.submit(function(){
        resource.wait(function(){
            var upreq = resource.load({'source':self.nForm.find('input[name="source"]').val()})
            upreq.wait(function(){
                if(upreq.error) {
                    alert("Upload failed: "+upreq.result.detail)
                } else {
                    self.dialog.hide()
                    if(callback) callback(upreq)
                }
            })
        })
        return false
    })
}

Lucullus.ui.Newick = function(api) {
    var self = this
    this.api = api
    this.dialog = new Lucullus.ui.Dialog()
    this.dialog.settitle('Newick Viewer')
    this.dialog.on_resize = function(e, ui) {
        var x = self.dialog.node.innerWidth()
        x -= self.dialog.node.css('padding-left').replace('px','')
        x -= self.dialog.node.css('padding-right').replace('px','')
        var y = self.dialog.node.innerHeight()
        y -= self.dialog.node.css('padding-top').replace('px','')
        y -= self.dialog.node.css('padding-bottom').replace('px','')
        y -= self.dialog.node.css('pading-top').replace('px','')
        y -= self.dialog.node.css('pading-bottom').replace('px','')
        y -= self.dialog.node.css('border-top-width').replace('px','')
        y -= self.dialog.node.css('border-bottom-width').replace('px','')
        y -= self.dialog.node.css('margin-top').replace('px','')
        y -= self.dialog.node.css('margin-bottom').replace('px','')
        self.map.resize(Math.floor(x), Math.floor(y))
    }
    this.view = this.api.create('NewickResource', {fontsize:10})
    this.map = new Lucullus.ViewMap(this.dialog.node, this.view)
    this.ml = new Lucullus.MoveListenerFactory()
    this.ml.addMap(this.map,1,1)
    this.ml.addJoystick(this.map.node,1,1)
    this.upload = new Lucullus.ui.Upload(this.view, function(){
        self.dialog.on_resize()
    })
}