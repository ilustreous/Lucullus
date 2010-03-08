Lucullus.gui = new Object()

Lucullus.gui.NewickTreeWindow = function(options) {
    this.options = {
      api: Lucullus.current,
      fontsize: 10
    }
    jQuery.extend(this.options, options)

    this.api = this.options.api
    this.data = {}
    this.gui = {}
    
    this.data.tree = this.api.create('NewickResource', {fontsize: this.options.fontsize})
    
    this.gui.toolbar = new Ext.Toolbar()
    this.gui.toolbar.add({
        text: 'New',
        icon: '/img/icons/16x16/actions/document-new.png',
        menu: { items: [
            {text: 'Open file',
            handler: this.load,
            scope: this,
            icon: '/img/icons/16x16/actions/document-open.png'},
            {text: 'Export',
            handler: this.export,
            scope: this,
            disabled: true,
            icon: '/img/icons/16x16/actions/document-save.png'},
        ]}
    })
    
    this.gui.tree = new Ext.Panel({
        title: 'Phylogenetic Tree Data',
        region: 'center',
        split: true,
        disabled: true,
        width: 400,
        collapsible: false,
        margins:'0 0 0 0',
        cmargins:'0 0 0 0'
    });

    this.gui.index = idx = new Ext.Panel({
        title: 'Sequence Index',
        region: 'west',
        split: true,
        disabled: true,
        width: 200,
        collapsible: true,
        margins:'0 0 0 0',
        cmargins:'0 0 0 0'
    });

    this.gui.win = new Ext.Window({
        title: 'Newick Tree Viewer',
        closable: true,
        hidden: true,
        width: 600,
        height: 350,
        //border:false,
        plain: true,
        layout: 'border',
        defaults: {
            split: true,
            bodyStyle: 'padding:0px'
        },
        tbar: this.gui.toolbar,
        items: [this.gui.index, this.gui.tree]
    });
}

Lucullus.gui.NewickTreeWindow.prototype.show = function() {
  var win = this.gui.win
  if(!win.hidden) return this
  this.gui.win.show()
}

Lucullus.gui.NewickTreeWindow.prototype.load = function() {
  alert(5)
  this.gui.win.hide()
}




Lucullus.gui.ImportWindow = function(options) {
    this.options = {}
    jQuery.extend(this.options, options)
    this.form = new Ext.form.FormPanel({
        labelWidth: 55,
        defaultType: 'textfield',
        items: [{
            fieldLabel: 'File URL',
            name: 'upFile',
            anchor:'100%'  // anchor width by percentage
        }]
    });

    this.win = new Ext.Window({
        title: 'File Import',
        width: 500,
        height: 300,
        minWidth: 300,
        minHeight: 200,
        layout: 'fit',
        plain: true,
        bodyStyle: 'padding:5px;',
        buttonAlign: 'center',
        items: this.form,
        buttons: [{text: 'Import'},{text: 'Cancel'}]
    });

    this.win.show()
    this.win.buttons[0].on("click", this.onClick, this)
}

Lucullus.gui.ImportWindow.prototype.onClick = function() {
    console.log(this.form.items.items[0].getValue())
}

Lucullus.gui.ImportWindow.prototype.onAbort = function() {
    this.win.destroy()
}
