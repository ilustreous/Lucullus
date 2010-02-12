Lucullus.gui = new Object()

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