Lucullus.gui = new Object()

Lucullus.gui.AppWindow = function(options) {
    /* This creates/opens a window holding multiple workspaces  */
    this.gui = {}
    this.apps = []

    this.gui.root = new Ext.Window({
        title: 'Lucullus Workspace',
        closable: true,
        hidden: true,
        width: 600,
        height: 350,
        //border:false,
        plain: true,
        layout: 'fit',
    });

    /* Tab area */
    this.gui.tabpanel = new Ext.TabPanel({
        resizeTabs: true, // turn on tab resizing
        minTabWidth: 115,
        tabWidth: 135,
        enableTabScroll: true, //<-- displays a scroll for the tabs
        border: false
    });

    this.gui.root.add(this.gui.tabpanel)
    this.gui.tabpanel.add({
        title: 'Settings',
        closable: false,
        iconCls: 'icon-config',
        html: 'foo',
    })
    this.gui.tabpanel.setActiveTab(0)
}

Lucullus.gui.AppWindow.prototype.show = function() {
    if(this.gui.root.hidden) this.gui.root.show()
}

Lucullus.gui.AppWindow.prototype.addApp = function(app) {
    this.gui.tabpanel.add(app.gui.root)
    this.gui.tabpanel.activate(app.gui.root)
    this.apps.push(app)
}





Lucullus.gui.NewickApp = function(options) {
    this.options = {
      api: Lucullus.current,
      fontsize: 10
    }
    jQuery.extend(this.options, options)

    this.api = this.options.api
    this.data = {}
    this.gui = {}

    this.data.tree = this.api.create('NewickResource', {fontsize: this.options.fontsize})

    this.gui.root = new Ext.Panel({
        title: 'Newick App',
        iconCls: 'icon-document',
        closable: true,
        layout: 'border',
        border: false,
        tbar: new Ext.Toolbar({border: false})
    })

    /* Toolbar area */

    this.gui.toolbar = this.gui.root.getTopToolbar()

    this.gui.tb_file = new Ext.Button({
        text: 'New',
        icon: '/img/icons/16x16/actions/document-new.png',
        menu: new Ext.menu.Menu()
    });

    this.gui.tb_file.menu.add({
        text: 'Open file',
        handler: this.load, scope: this,
        icon: '/img/icons/16x16/actions/document-open.png'
    });

    this.gui.tb_file.menu.add({
        text: 'Export',
        handler: this.export, scope: this,
        disabled: true,
        icon: '/img/icons/16x16/actions/document-save.png'
    });

    this.gui.toolbar.add(this.gui.tb_file)

    this.gui.root.add(new Ext.Panel({
        title: 'Sequence Index',
        border: false,
        region: 'west',
        split: true,
        disabled: true,
        width: 200,
        collapsible: true,
        margins:'0 0 0 0',
        cmargins:'0 0 0 0'
    }));

    this.gui.root.add(new Ext.Panel({
        title: 'Phylogenetic Tree Data',
        region: 'center',
        split: true,
        disabled: true,
        width: 400,
        collapsible: false,
        margins:'0 0 0 0',
        cmargins:'0 0 0 0'
    }));
}

Lucullus.gui.NewickApp.prototype.load = function() {
  this.gui.root.items.items[0].enable()
  this.gui.root.items.items[1].enable()
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
