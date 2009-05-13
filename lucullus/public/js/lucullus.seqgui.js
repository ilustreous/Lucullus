/**
 * Used for UserInteraction
 * @constructor
 */
Lucullus.SeqGui = function(element, api) {
	this.api   = api
	this.node  = $(element)
	this.map   = null
	this.index = null
	this.ml = new Lucullus.MoveListenerFactory()

	var self   = this

	self.api.addHook("connectStart", function(msg, d) {
		self.node.html("Connecting to "+self.api.server+"...")
	})

	self.api.addHook("connectSuccess", function(msg, d) {
		self.node.html("Connecting to to "+self.api.server+" with session key "+d.output.session+". Creating project...")
		self.api.create('sequences')
	})

	self.api.addHook("createSuccess", function(msg, d) {
		self.node.html('\
		<div style="color: green">Your Lucullus project is currently empty. Please provide an URL to a fasta file.</div>\
		<form>\
		  URL: <input type="text" name="upUrl" />\
		  Format:<select>\
		    <option value="fasta">Fasta</option>\
		  </select> <input type="submit" value="Upload"/>\
		</form>')
		$('form',self.node).bind('submit', function(event) {
			event.preventDefault()
		    event.stopPropagation()
			var file = $('input:first',event.target).val()
			var format = $('select:first',event.target).val()
			if(confirm("Do you want to import the following file (format:"+format+")? "+file)) {
				self.api.import_data(file, format)
			}
		});
	})
	
	self.api.addHook("importStart", function(msg, d) {
		self.node.html("Importing "+d.input.uri+"...")
	})
	
	self.api.addHook("importSuccess", function(msg, d) {
		if(self.map) {
			self.ml.removeMap(self.map)
			self.map = null
		}
		self.node.html('\
		<table style="border-spacing:0px; border-collapse: collapse; margin: 0px auto" cellspacing="0" cellpadding="0">\
			<tr>\
				<td style="background: transparent url(logo.png) no-repeat top left;"></td>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
			</tr>\
			<tr>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
			</tr>\
			<tr>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
			</tr>\
		</table>')

		var rulernode = $('td',self.node)[1]
		var indexnode = $('td',self.node)[4]
		var mapnode = $('td',self.node)[5]
		$($('tr',self.node)[1]).hide() // TODO: This is ugly

		self.api.call('getsize',{'view':'default'}, function(data) {
			var x = Number(data.x)
			var y = Number(data.y)
			var w = Number(data.width)
			var h = Number(data.height)
			
			self.map = new Lucullus.PixelMap(mapnode, function(numberx, numbery, sizex, sizey) {
				return self.api.server + '/image?view=alignment&session='+self.api.session+'&x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey	
			})
			
			self.map.set_clipping(x,y,x+w,y+h)
			self.ml.addMap(self.map,1,1)
			self.ml.addLinear(mapnode,1,1)

			self.index = new Lucullus.PixelMap(indexnode, function(numberx, numbery, sizex, sizey) {
				return self.api.server + '/image?view=index&session='+self.api.session+'&x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey	
			})
			self.index.set_clipping(x,y,x+200,y+h)
			self.ml.addMap(self.index,0,1)
			self.ml.addLinear(indexnode,0,1)

			self.ruler = new Lucullus.PixelMap(rulernode, function(numberx, numbery, sizex, sizey) {
				return self.api.server + '/image?view=ruler&session='+self.api.session+'&x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey	
			})
			self.ruler.set_clipping(0,0,w,20)
			self.ml.addMap(self.ruler,1,0)
			self.ml.addJoystick(rulernode,1,0)


			self.map.set_size(700,500)
			self.index.set_size(150,500)
			self.ruler.set_size(700,25)
			return true
		})
	})

	self.api.addHook("connectError", function(msg, d) {
		self.node.html("Connection failed... Please try again later.")
	})

	self.api.addHook("createError", function(msg, d) {
		self.node.html("Failed to create a new project. Please try again later.")
	})

	self.api.addHook("importError", function(msg, d) {
		self.node.html("Failed to import data: "+ d.output.error)
	})
}


Lucullus.PhbGui = function(element, api) {
	this.api   = api
	this.node  = $(element)
	this.map   = null
	this.index = null
	this.ml = new Lucullus.MoveListenerFactory()

	var self   = this

	self.api.addHook("connectStart", function(msg, d) {
		self.node.html("Connecting to "+self.api.server+"...")
	})

	self.api.addHook("connectSuccess", function(msg, d) {
		self.node.html("Connecting to to "+self.api.server+" with session key "+d.output.session+". Creating project...")
		self.api.create('phb')
	})

	self.api.addHook("createSuccess", function(msg, d) {
		self.node.html('\
		<div style="color: green">Your Lucullus project is currently empty. Please provide an URL to a fasta file.</div>\
		<form>\
		  URL: <input type="text" name="upUrl" /> <input type="submit" value="Upload"/>\
		</form>')
		$('form',self.node).bind('submit', function(event) {
			event.preventDefault()
		    event.stopPropagation()
			var file = $('input:first',event.target).val()
			var format = 'phb'
			if(confirm("Do you want to import the following file (format:"+format+")? "+file)) {
				self.api.import_data(file, format)
			}
		});
	})
	
	self.api.addHook("importStart", function(msg, d) {
		self.node.html("Importing "+d.input.uri+"...")
	})
	
	self.api.addHook("importSuccess", function(msg, d) {
		if(self.map) {
			self.ml.removeMap(self.map)
			self.map = null
		}
		self.node.html('\
		<table style="border-spacing:0px; border-collapse: collapse; margin: 0px auto" cellspacing="0" cellpadding="0">\
			<tr>\
				<td style="background: transparent url(logo.png) no-repeat top left;"></td>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
			</tr>\
			<tr>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
			</tr>\
			<tr>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
				<td style="border: 1px solid grey;"><div>Loading...</div></td>\
			</tr>\
		</table>')

		var rulernode = $('td',self.node)[1]
		var indexnode = $('td',self.node)[4]
		var mapnode = $('td',self.node)[5]
		$($('tr',self.node)[1]).hide() // TODO: This is ugly

		self.api.call('getsize',{'view':'tree'}, function(data) {
			var x = Number(data.x)
			var y = Number(data.y)
			var w = Number(data.width)
			var h = Number(data.height)
			
			self.map = new Lucullus.PixelMap(mapnode, function(numberx, numbery, sizex, sizey) {
				return self.api.server + '/image?view=tree&session='+self.api.session+'&x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey	
			})
			
			self.map.set_clipping(x,y,x+w,y+h)
			self.ml.addMap(self.map,1,1)
			self.ml.addLinear(mapnode,1,1)

			self.index = new Lucullus.PixelMap(indexnode, function(numberx, numbery, sizex, sizey) {
				return self.api.server + '/image?view=index&session='+self.api.session+'&x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey	
			})
			self.index.set_clipping(x,y,x+200,y+h)
			self.ml.addMap(self.index,0,1)
			self.ml.addLinear(indexnode,0,1)

			self.ruler = new Lucullus.PixelMap(rulernode, function(numberx, numbery, sizex, sizey) {
				return self.api.server + '/image?view=ruler&session='+self.api.session+'&x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey	
			})
			self.ruler.set_clipping(0,0,w,20)
			self.ml.addMap(self.ruler,1,0)
			self.ml.addJoystick(rulernode,1,0)


			self.map.set_size(700,500)
			self.index.set_size(150,500)
			self.ruler.set_size(700,25)
			return true
		})
	})

	self.api.addHook("connectError", function(msg, d) {
		self.node.html("Connection failed... Please try again later.")
	})

	self.api.addHook("createError", function(msg, d) {
		self.node.html("Failed to create a new project. Please try again later.")
	})

	self.api.addHook("importError", function(msg, d) {
		self.node.html("Failed to import data: "+ d.output.error)
	})
}
