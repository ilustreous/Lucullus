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
        text: 'Load test file',
        handler: function(){
            var a = new Lucullus.gui.NewickApp({
                name: 'TestApp', source:'http://fab8:8080/test/test.phb'
            })
            self.addApp(a)
        },
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
        minTabWidth: 150,
        tabWidth: 200,
        enableTabScroll: true, //<-- displays a scroll for the tabs
        border: false,
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

Lucullus.gui.AppWindow.prototype.show = function() {
    if(this.gui.root.hidden) this.gui.root.show()
}

Lucullus.gui.AppWindow.prototype.do_load = function() {
    var self = this
    new Lucullus.gui.ImportWindow({onsubmit:function(type, name, url){
        if(type = 'Newick') {
            if(url && name) {
                var a = new Lucullus.gui.NewickApp({name: name, source:url})
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

    app.gui.root.on('activate', function(){
        if(app.gui.toolbar_items) {
            for(i=0; i < app.gui.toolbar_items.length; i++) {
                app.gui.toolbar_items[i].show()
            }
        }
        this.gui.toolbar.doLayout()
    }, this)

    app.gui.root.on('deactivate', function(){
        if(app.gui.toolbar_items) {
            for(i=0; i < app.gui.toolbar_items.length; i++) {
                app.gui.toolbar_items[i].hide()
            }
        }
        this.gui.toolbar.doLayout()
    }, this)

    app.gui.root.on('close', function(){
        if(app.gui.toolbar_items) {
            for(i=0; i < app.gui.toolbar_items.length; i++) {
                app.gui.toolbar_items[i].hide()
            }
        }
        this.gui.toolbar.doLayout()
        this.apps.remove[id]
    }, this)

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
                {boxLabel: 'Sequence Alignment', name: 'type',
                 inputValue: 'SeqApp', checked: true},
                {boxLabel: 'Newick Tree', name: 'type',
                 inputValue: 'NewickApp'},
            ]
        },{
            xtype: 'textfield',
            fieldLabel: 'Project Name',
            name: 'name',
        },{
            xtype: 'textfield',
            value: 'http://',
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
        items: this.gui.form,
        buttonAlign: 'center',
        buttons: [{text: 'Load'}, {text: 'Cancel'}]
    });

    this.gui.root.show()
    this.gui.root.buttons[0].on("click", this.onClick, this)
    this.gui.root.buttons[1].on("click", this.onAbort, this)

    /* This hack allows submitting the form with enter key. It works by adding
       an invisible submit button to the form and catch its click event.
    */
    var enter_hack = this.gui.form.getForm().el.createChild({
        tag: 'input',
        type: 'submit',
        style: { position: 'absolute', top: '-10000px', left: '-10000px' },
        tabIndex: -1 // Exclude this button from tab-focus
    });
    enter_hack.on("click", this.onClick, this);
}

Lucullus.gui.ImportWindow.prototype.onClick = function() {
    var data = this.gui.form.getForm().getValues()
    this.options.onsubmit(data.type, data.name, data.url)
    this.gui.root.destroy()
    return false
}

Lucullus.gui.ImportWindow.prototype.onAbort = function() {
    this.gui.root.destroy()
}

















Lucullus.gui.NewickApp = function(options) {
    this.options = {
      api: Lucullus.current,
      fontsize: 10,
      source: '/test/test.seq',
      name: 'Unnamed Tree'
    }
    jQuery.extend(this.options, options)
    var self = this
    this.api = this.options.api
    this.data = {}
    this.gui = {}

    this.gui.toolbar_items = [new Ext.Button({text: this.options.name})]

    this.gui.root = new Ext.Panel({
        title: self.options.name + " (Newick Tree)",
        iconCls: 'icon-document',
        closable: true,
        layout: 'border',
        border: false,
    })
    
    this.gui.root.on('activate', function(){
        self.sync_size()
    })
    this.gui.root.on('destroy', function(){
        for ( var i in this.gui.toolbar_items ) {
            if(this.gui.toolbar_items[i].destroy)
                this.gui.toolbar_items[i].destroy();
        }
    }, this)


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
        collapsible: false,
        border: false
    })
    this.gui.root.add(this.gui.map_panel);

    // Create data structures client and server side
    this.data.tree = this.api.create('NewickResource', {
        fontsize: this.options.fontsize
    })
    this.data.index = this.api.create('IndexView', {
        fontsize: this.options.fontsize
    })

    // Create a mouse-event hub to syncronize the different panels
    this.ml = new Lucullus.MoveListenerFactory()

    // Create ViewMaps as soon as the map and index panel doms are available
    this.gui.map_panel.on('render', function(){
        if(!self.gui.map_view) {
            self.gui.map_view = new Lucullus.ViewMap(
                          self.gui.map_panel.body.dom,
                          self.data.tree)
            // The whole map is a mouse control
            self.ml.addMap(self.gui.map_view,1,1)
            self.ml.addLinear(self.gui.map_view.node,1,1)
        }
    })

    this.gui.index_panel.on('render', function(){
        if(!self.gui.index_view) {
            self.gui.index_view = new Lucullus.ViewMap(
                          self.gui.index_panel.body.dom,
                          self.data.index)
            // The whole index map is a mouse control, but limited to the y axis
            self.ml.addMap(self.gui.index_view, 0, 1)
            self.ml.addJoystick(self.gui.index_view.node, 0, 1)
        }
    })

    // Resize the ViewMaps along wih the panel 
    this.gui.map_panel.on('resize', this.sync_size, this)
    this.gui.index_panel.on('resize', this.sync_size, this)
    this.gui.map_panel.on('enable', this.sync_size, this)
    this.gui.index_panel.on('enable', this.sync_size, this)

    // As soon as the initialisation finishes, configure the index map
    this.data.tree.wait(function(){
        var upreq = self.data.tree.load({'source':self.options.source})
        upreq.wait(function(){
            self.data.index.wait(function(){
                if(upreq.error) {
                    alert("Upload failed: " + upreq.result.detail)
                    self.close()
                    return
                }
                if(upreq.result.keys) {
                    self.gui.root.items.items[1].enable()
                    self.data.index.setup({
                        'keys': upreq.result.keys
                    }).wait(function(){
                        self.gui.root.items.items[0].enable()
                        self.sync_size()
                    })
                }
            })
        })
    })
}

Lucullus.gui.NewickApp.prototype.sync_size = function() {
    console.log(this)
    if(this.gui.map_view) {
        var h = this.gui.map_panel.body.getHeight(true)
        var w = this.gui.map_panel.getWidth(true)
        this.gui.map_view.resize(w, h)
    }
    if(this.gui.index_view) {
        var h = this.gui.index_panel.body.getHeight(true)
        var w = this.gui.index_panel.getWidth(true)
        this.gui.index_view.resize(w, h)
    }
}

Lucullus.gui.NewickApp.prototype.close = function() {
    this.gui.root.destroy()
}









