Lucullus.gui = new Object()

Lucullus.gui.AppWindow = function(options) {
    /* This creates/opens a window holding multiple workspaces  */
    this.gui = {}
    this.apps = []
    var self = this

    this.gui.root = new Ext.Window({
        title: 'Lucullus Workspace',
        closable: true,
        maximizable: true,
        hidden: true,
        width: 600,
        height: 350,
        //border:false,
        plain: true,
        layout: 'fit',
        tbar: new Ext.Toolbar({border: false})
    });

    this.gui.toolbar = this.gui.root.getTopToolbar()

    this.gui.tb_file = new Ext.Button({
        text: 'New',
        icon: '/img/icons/16x16/actions/document-new.png',
        menu: new Ext.menu.Menu()
    });

    this.gui.tb_file.menu.add({
        text: 'Open URL...',
        handler: this.do_load, scope: this,
        icon: '/img/icons/16x16/categories/applications-internet.png'
    });

    this.gui.tb_file.menu.add({
        text: 'Open file...',
        handler: this.do_load, scope: this,
        disabled: true,
        icon: '/img/icons/16x16/actions/document-open.png'
    });

    this.gui.tb_file.menu.add({
        text: 'Export',
        handler: this.do_export, scope: this,
        disabled: true,
        icon: '/img/icons/16x16/actions/document-save.png'
    });

    this.gui.toolbar.add(this.gui.tb_file)
    this.gui.toolbar.add('-')

    /* Tab area */
    this.gui.tabpanel = new Ext.TabPanel({
        resizeTabs: true, // turn on tab resizing
        minTabWidth: 115,
        tabWidth: 135,
        enableTabScroll: true, //<-- displays a scroll for the tabs
        border: false,
        listeners: {
            beforetabchange: function(tabPanel, tab){self.on_beforetabchange(tab)},
            tabchange: function(tabPanel, tab){self.on_tabchange(tab)}
        }
    });
    this.gui.root.add(this.gui.tabpanel)

    //this.gui.tabpanel.add({
    //    title: 'Settings',
    //    closable: false,
    //    iconCls: 'icon-config',
    //    html: 'foo',
    //})
    //this.gui.tabpanel.setActiveTab(0)
}

Lucullus.gui.AppWindow.prototype.on_beforetabchange = function() {
    if(this.gui.tabpanel.getActiveTab()) {
        var app = this.apps[this.gui.tabpanel.getActiveTab().getId()]
        if(app.gui.toolbar_items) {
            for(i=0; i < app.gui.toolbar_items.length; i++) {
                app.gui.toolbar_items[i].hide()
            }
        }
    }
}

Lucullus.gui.AppWindow.prototype.on_tabchange = function() {
    if(this.gui.tabpanel.getActiveTab()) {
        var app = this.apps[this.gui.tabpanel.getActiveTab().getId()]
        if(app.gui.toolbar_items) {
            for(i=0; i < app.gui.toolbar_items.length; i++) {
                app.gui.toolbar_items[i].show()
            }
        }
        this.gui.toolbar.doLayout()
    }
}

Lucullus.gui.AppWindow.prototype.show = function() {
    if(this.gui.root.hidden) this.gui.root.show()
}

Lucullus.gui.AppWindow.prototype.do_load = function() {
    var self = this
    new Lucullus.gui.ImportWindow({onsubmit:function(type, name, url){
        if(type = 'Newick') {
            if(url && name) {
                var a = new Lucullus.gui.NewickApp({source:url})
                a.gui.root.setTitle("Newick: " + name)
                self.addApp(a)
            }
        }
    }});
}

Lucullus.gui.AppWindow.prototype.addApp = function(app) {
    var id = app.gui.root.getId()
    this.apps[id] = app // TODO: Was passiert bei doppelt eingefuegten apps?
    this.gui.tabpanel.add(app.gui.root)
    if(app.gui.toolbar_items) {
        for(i=0; i < app.gui.toolbar_items.length; i++) {
            this.gui.toolbar.add(app.gui.toolbar_items[i])
        }
    }
    var self = this
    this.gui.tabpanel.activate(app.gui.root)
}












Lucullus.gui.ImportWindow = function(options) {
    this.options = {onsubmit: alert}
    jQuery.extend(this.options, options)
    var self = this
    this.gui = {}
    
    this.gui.form = new Ext.FormPanel({
        labelWidth: 100,
        baseCls: 'x-plain',
        defaults: {
            anchor: '95%',
        },
        items: [{
            xtype: 'radiogroup',
            fieldLabel: 'Type',
            items: [
                {boxLabel: 'Sequence Alignment', name: 'type', inputValue: 'SeqApp', checked: true},
                {boxLabel: 'Newick Tree', name: 'type', inputValue: 'NewickApp'},
            ]
        },{
            xtype: 'textfield',
            fieldLabel: 'Project Name',
            name: 'name',
        },{
            xtype: 'textfield',
            emptyText: 'http://',
            fieldLabel: 'Data File',
            name: 'url',
        }],
    });

    this.gui.root = new Ext.Window({
        title: 'Data Import Form',
        modal: true,
        width: 500,
        minWidth: 300,
        layout: 'fit',
        plain: true,
        buttonAlign: 'center',
        items: this.gui.form,
        buttons: [{text: 'Load'},{text: 'Cancel'}]
    });

    this.gui.root.show()
    this.gui.root.buttons[0].on("click", this.onClick, this)
    this.gui.root.buttons[1].on("click", this.onAbort, this)
}

Lucullus.gui.ImportWindow.prototype.onClick = function() {
    var data = this.gui.form.getForm().getValues()
    this.options.onsubmit(data.type, data.name, data.url)
    this.gui.root.destroy()
}

Lucullus.gui.ImportWindow.prototype.onAbort = function() {
    this.gui.root.destroy()
}

















Lucullus.gui.NewickApp = function(options) {
    this.options = {
      api: Lucullus.current,
      fontsize: 10,
      source: '/test/test.seq'
    }
    jQuery.extend(this.options, options)
    var self = this
    this.api = this.options.api
    this.data = {}
    this.gui = {}

    this.gui.toolbar_items = [new Ext.Button({text: 'Button'})]

    this.gui.root = new Ext.Panel({
        title: 'Newick App',
        iconCls: 'icon-document',
        closable: true,
        layout: 'border',
        border: false,
    })
    
    this.gui.root.on('activate', function(){
        self.refresh()
    })

    /* Toolbar area */

    this.gui.index_panel = new Ext.Panel({
        title: 'Sequence Index',
        border: false,
        region: 'west',
        split: true,
        disabled: true,
        width: 200,
        collapsible: true,
        margins:'0 0 0 0',
        cmargins:'0 0 0 0'
    })
    this.gui.root.add(this.gui.index_panel);

    this.gui.map_panel = new Ext.Panel({
        title: 'Phylogenetic Tree Data',
        region: 'center',
        split: true,
        disabled: true,
        collapsible: false
    })
    this.gui.root.add(this.gui.map_panel);

    this.data.tree = this.api.create('NewickResource', {fontsize: this.options.fontsize})
    this.gui.map_panel.on('render', function(){
        if(!self.gui.map) {
            self.gui.map_view = new Lucullus.ViewMap(self.gui.map_panel.body.dom, self.data.tree)
            self.ml.addMap(self.gui.map_view,1,1)
            self.ml.addJoystick(self.gui.map_view.node,1,1)
            self.refresh()
        }
    })
    this.gui.map_panel.on('resize', function(){
        self.refresh()
    })
    
    this.data.tree.wait(function(){
        var upreq = self.data.tree.load({'source':self.options.source})
        upreq.wait(function(){
            if(upreq.error) {
                alert("Upload failed: "+upreq.result.detail)
            }
            self.load()
            self.refresh()
        })
    })
    this.ml = new Lucullus.MoveListenerFactory()
}

Lucullus.gui.NewickApp.prototype.refresh = function() {
    var h = this.gui.map_panel.body.getHeight(true)
    var w = this.gui.map_panel.getWidth(true)
    this.gui.map_view.resize(w, h)
}

Lucullus.gui.NewickApp.prototype.load = function() {
    this.gui.root.items.items[0].enable()
    this.gui.root.items.items[1].enable()
}









