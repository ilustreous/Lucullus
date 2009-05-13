/**
 * API Object
 * @class Server API (evend based asyc execution)
 * @constructor
 */

function Lucullus() {}

Lucullus.api = function (server, key) {
	/** Session id
	 * @type string */
	this.session	= ''
	/** API location (url) http://www.example.com/seqmap/api 
	 * @type string */
	this.server		= server
	/** API key 
	 * @type string */
	this.key		= key
	/** API version number 
	 * @type int */
	this.api		= 1	
	/** List of supported plugins 
	 * @type List */
	this.plugins  = []

	/** Log for errors and debug messages 
	 * @type Array */
	this.log		= []
	/** Debug mode
	 * @type bool */
	this.debug		= false
	/** List of known resources 
	 * @type Dict */
	this.resources  = {}
}


/**
 * Calls a API method of a Lucullus Server
 * @param {string} Name of the API method
 * @param {string} Data to provide
 * @param {function} Callback
 * @return Lucutus.call object
 */

Lucullus.api.prototype.call = function(action, input, callback) {
	var self = this
	var url = self.server + '/'
	
	if(self.session) {
		url = url + self.session + '/'
	}

	url = url + action
  return new Lucullus.call(self, url, input, callback)
}

/**
 * Connect to a Lucullus Server starting a new session
 * @param {function} Callback
 * @return Lucullus.call object
 */
Lucullus.api.prototype.connect = function(callback) {
	this.session = ''
	this.plugins = []

	return this.call( 'connect', 
		{'key':this.key}, 
		function(c) {
			if(c.result && c.result.session)
				c.api.session = c.result.session
			if(c.result && c.result.plugins)
				c.api.plugins = c.result.plugins
			if(callback)
			  callback(c)
		}
	);
}

/**
 * Creating a new Resource and returns a resource object equipped with
 * available api methods.
 * @param {string} type Type of the resource (one of api.plugins)
 * @param {function} Callback
 * @return Resource object
 */
Lucullus.api.prototype.create = function(type, callback) {
  var resource = new Lucullus.resource(this)
	var result = this.call( 'create', 
		{'type':type}, 
		function(c) {
			if(c.result && typeof c.result.resource !== 'undefined' && c.result.type) {
			  resource.id = c.result.resource
				resource.type = c.result.type
				resource.result = c.result
				if(c.result.methods) {
					jQuery.each(c.result.methods, function(i, name) {
						resource[name] = function(opt, callback2) {
							return resource.query(name, opt, callback2)
						}
					});
				}
				c.api.resources[resource.id] = resource
			}
			if(callback)
			  callback(c)
		}
	);
	return resource
}








Lucullus.resource = function(api) {
	this.api = api
	this.id	= null
	this.type = null
	this.result = null
	this.error = null
}

Lucullus.resource.prototype.query = function(action, parameter, callback) {
	var self = this
	var url = self.api.server + '/' + self.api.session + '/' + self.id + '/' + action
  var call = new Lucullus.call(self.api, url, parameter, 
		function(c) {
			if(c.result && typeof c.result.resource !== 'undefined' && c.result.resource == self.id && c.result.result) {
			  self.result = c.result.result
				// self.error = null
				// error recovery should be explicit (r.error=null)
			} else {
				self.error = c.error
				self.result = null
			}
			if(callback)
			  callback(c)
		}
	);
	return call
}







Lucullus.call = function(api, url, parameter, callback) {
	this.api = api
	this.url = url
	this.parameter = parameter
	this.callback = callback
	this.result = null
	this.error = null
	this.send()
}

Lucullus.call.prototype.send = function() {
	var self = this
	jQuery.ajax({
		url: self.url,
		data: self.parameter,
		dataType: "json",
		async: false,
		success: function(data){
			if(data && data.session) {
				self.result = data
			} else if(data && data.error) {
				self.error = data
				self.error['message'] = data.error
				delete self.error['error']
			} else if(data) {
				self.error = {'message':'Unexpected answer', 'answer':data}
			} else {
				self.error = {'error':'No answer'}
			}
		},
		complete: function() {
			if(self.callback) {
				self.callback(self)
			}
		}
	});
}











Lucullus.PixelMap = function (element, imageurl) {
	this.clipping = [-Number.MAX_VALUE, -Number.MAX_VALUE, Number.MAX_VALUE, Number.MAX_VALUE]			// minimum and maximum pixel to show
	this.tilesize = [256,256]			// Size of a tile in pixel
	this.tileurl  = null				// Function to generate tile url
	//this.tilecount = [0,0]			// Number of tiles to show (depends on node width and height)
	this.offset = [0,0]					// Current offset
	this.root = $(element)
	this.node = $('<div style="height:100%; width:100%; position:relative; overflow:hidden;"></div>')
	this.map =  null
	this.buffer = null
	this.root.empty()
	this.root.append(this.node)

	// Some caches for faster processing
	this.mapsize = [0,0,0,0]			// Size of viewable area and map container (minx, miny, maxx, maxy)
	this.mapoffset = [0,0]				// Position of map
	this.bufferoffset = [0,0]			// Position of buffer
	
	// callbacks and helper
	this.imageurl = imageurl
	
	this.refresh_speed = 500
	this.refresh_interval = null
	
	this._fill = function(nx, ny, cx, cy) {
		/* Fills the current map with images using (nx,ny) as number of top left tile and (cx,cy) as number of tiles to show */
		var tx = this.tilesize[0]
		var ty = this.tilesize[1]
		var images = []
		for(var y=0; y<cy; y++) {
			for(var x=0; x<cx; x++) {
				// Image URL
				var url = this.imageurl(x+nx, y+ny, tx, ty)
				// Offset within our map in pixel
				var ox = x * tx
				var oy = y * ty
				// Total offset of data area in pixel
				var tox = (x+nx) * tx
				var toy = (y+ny) * ty
				
				if(tox < this.clipping[2] && toy < this.clipping[3] && (tox + tx) > this.clipping[0] && (toy + ty) > this.clipping[1]) {
					images.push('<img src="'+url+'" style="position:absolute; width:'+tx+'px; height:'+ty+'px; left:'+ox+'px; top:'+oy+'px;" />')
				}
			}
		}
		this.map.html(images.join("\n"))
	}
	
	this._new_map = function() {
		if(!this.imageurl) return
		/* Adds a new map to the container node */
		// Height and width of visible area
		var w = this.node.width()
		var h = this.node.height()
		this.mapsize = [w,h,0,0]
		if(h == 0 || w == 0) return
		// Number of tiles that fit into that area (+1 for a spare tile in every direction)
		var overlap = 0 // Spare tiles in every direction (mor tiles, fewer refreshes)
		var tiles_x = Math.ceil(w / this.tilesize[0] ) + 1 + overlap*2
		var tiles_y = Math.ceil(h / this.tilesize[1] ) + 1 + overlap*2
		this.mapsize = [w,h, tiles_x*this.tilesize[0], tiles_y*this.tilesize[1]]
		// Index number of top left tile
		var nx = Math.floor(-this.offset[0] / this.tilesize[0])-overlap
		var ny = Math.floor(-this.offset[1] / this.tilesize[1])-overlap
		// Total offset of top left tile
		var ox = nx * this.tilesize[0] 
		var oy = ny * this.tilesize[1] 
		// Offset of top left tile relative to visible area
		var vox = ox+this.offset[0]
		var voy = oy+this.offset[1]

		if(this.buffer)
			this.buffer.remove()
		this.buffer = this.map
		this.bufferoffset = this.mapoffset
		this.map = $('<div style="position:absolute; left:'+vox+'px; top:'+voy+'px; width:'+(tiles_x * this.tilesize[0])+'px; height:'+(tiles_y * this.tilesize[1])+'px">Loading...</div>')
		this.mapoffset = [vox, voy]
		this._fill(nx, ny, tiles_x, tiles_y)
		this.node.append(this.map)
	}

	this.move = function(dx, dy) {
		/* Moves the map (and buffer) by (dx,dy) pixel and returns the actual movement */

		// Normalise movement (clipping) Don't try to understand this. It had 6 steps each before optimisation  
		dx = Math.min(- this.clipping[0], Math.max(this.mapsize[0] - this.clipping[2], this.offset[0] + dx)) - this.offset[0]
		dy = Math.min(- this.clipping[1], Math.max(this.mapsize[1] - this.clipping[3], this.offset[1] + dy)) - this.offset[1]

		if(dx == 0 && dy == 0) {
			return [0,0]
		}

		// Update offset
		this.offset[0] += dx
		this.offset[1] += dy

		// move map (and buffer, if available)
		this.mapoffset[0] += dx
		this.mapoffset[1] += dy
		this.map.css({'left': this.mapoffset[0] + 'px', 'top': this.mapoffset[1] + 'px'})

		if(this.buffer) {
			this.bufferoffset[0] += dx
			this.bufferoffset[1] += dy
			this.buffer.css({'left': this.bufferoffset[0] + 'px', 'top': this.bufferoffset[1] + 'px'})
		}

		return [dx, dy].slice()
	}

	var obj = this
	this._refresh_tick = function() {

		/* Adds a new map whenever needed (call every second or so) */
	    if(obj.mapoffset[0] > 0
		|| obj.mapoffset[0] + obj.mapsize[2] < obj.mapsize[0]
		|| obj.mapoffset[1] > 0
		|| obj.mapoffset[1] + obj.mapsize[3] < obj.mapsize[1] )
			obj._new_map()
			
		obj.refresh_interval = setTimeout(obj._refresh_tick, obj.refresh_speed)
	    return
	}

	this.set_size = function(w,h) {
		/** Sets the size of the mapping area and invokes a refresh.*/
		this.node.width(w + 'px')
		this.node.height(h + 'px')
		this._new_map()
	}
	
	this.set_clipping = function(minx, miny, maxx, maxy) {
		this.clipping = [minx, miny, maxx, maxy]
		this._new_map()
	}

	this._new_map()
	this._refresh_tick()
}














/**
 * Listener for mouse movements
 * @constructor
 */
Lucullus.DragListener = function(element) {
	/** Tracks Drag&Drop starting from element without doing anything. */
	this.element = $(element)
	this.moving = false			// Currently moving ?

	this.start   = [0,0]
	this.last    = [0,0]
	this.current = [0,0]

	var obj = this
	
	this.on_start = function(event) {
		if(obj.moving)
			return
		obj.moving = true
		obj.start   = [event.pageX, event.pageY]
		obj.last    = [event.pageX, event.pageY]
		obj.current = [event.pageX, event.pageY]
		$(document).bind('mousemove', obj.on_move)
		$(document).bind('mouseup', obj.on_stop)
		event.preventDefault()
	    event.stopPropagation()
	}
	
	this.on_move = function(event) {
		obj.current = [event.pageX, event.pageY]
	}
	
	this.on_stop = function(event) {
		$(document).unbind('mousemove', obj.on_move)
		$(document).unbind('mouseup', obj.on_stop)
		obj.current = [event.pageX, event.pageY]
		obj.moving = false
	}
	
	this.getDistance = function() {
		/** Distance from start to current position */
		x = this.current[0] - this.start[0]
		y = this.current[1] - this.start[1]
		return [x,y]
	}

	this.getMovement = function(noreset) {
		/** Movement since last call.
		@para {boolean} Ignore this call when calculating the next? Default: false
		@return {int,int} */
		x = this.current[0] - this.last[0]
		y = this.current[1] - this.last[1]
		if(! noreset)
		  this.last = this.current
		return [x,y]
	}

	this.element.bind('mousedown', obj.on_start)
}














/**
 * Initiates an empty 
 * @class Factory and Hub to track multible <code>SeqDragListener</code> and update multible Objects with a <code>.move()</code> method.
 * @constructor
 */
Lucullus.MoveListenerFactory = function() {
	this.listener	= []	// registred listener. ListenerObject, mode(0dead, 1linear, 2distance), scalex, scaley
	this.maps 		= []	// egistred maps to move
	this.speed		= 50

	var obj = this	// Used for events

	this.addLinear = function(element, sx, sy) {
		var lis = new Lucullus.DragListener(element) 
		this.listener.push([lis, 1, sx, sy])
		return lis
	}

	this.addJoystick = function(element, sx, sy) {
		var lis = new Lucullus.DragListener(element) 
		this.listener.push([lis, 2, -sx, -sy])
		return lis
	}
	
	this.addMap = function(map, sx, sy) {
		this.maps.push([map, sx, sy])
	}
	
	this.removeMap = function(map) {
		obj.maps = jQuery.grep(obj.maps, function(m, i){
			return (m[0] != map)
		})
	}

	this.tick = function() {
		var x = 0
		var y = 0
		// Collect movements from every listener
		jQuery.each(obj.listener, function(i, l) {
			if(l[0].moving) {
				var lis = l[0]
				var mode = l[1]
				var scale = [l[2],l[3]]
				if(mode == 1) {
				  var dis = lis.getMovement()
				} else {
				  var dis = lis.getDistance()
				}
				x += dis[0] * scale[0]
				y += dis[1] * scale[1]
			}
		})
		obj.move(x,y)
		// Do it again and again and ...
	    obj.interval = setTimeout(obj.tick, obj.speed);
	}
	
	this.move = function(x, y) {
		// Move every connected map
		if(x || y) {
			jQuery.each(obj.maps, function(i, map) {
				map[0].move(x*map[1],y*map[2])
			})
		}
		
	}

    this.interval = setTimeout(obj.tick, obj.speed);
}












/**
 * Used for UserInteraction
 * @constructor
 */
Lucullus.BaseGui = function(element, api) {
	this.api   = api
	this.node  = $(element)
	this.map   = null
	this.ml = new Lucullus.MoveListenerFactory()

	var self   = this

	self.api.addHook("connectStart", function(msg, d) {
		self.node.html("Connecting to "+self.api.server+"...")
	})

	self.api.addHook("connectSuccess", function(msg, d) {
		self.node.html("Connecting to to "+self.api.server+" with session key "+d.output.session+". Creating project...")
		self.api.create('sequences')
	})

	self.api.addHook("importStart", function(msg, d) {
		self.node.html("Importing "+d.input.uri+"...")
	})
	
	self.api.addHook("importSuccess", function(msg, d) {
		if(self.map) {
			self.ml.removeMap(self.map)
			self.map = null
		}

		self.api.call('getsize',{'view':'default'}, function(data) {
			var x = Number(data.x)
			var y = Number(data.y)
			var w = Number(data.width)
			var h = Number(data.height)
			
			self.map = new Lucullus.PixelMap(self.node, function(numberx, numbery, sizex, sizey) {
				return self.api.server + '/image?view=alignment&session='+self.api.session+'&x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey	
			})
			
			self.map.set_clipping(x,y,x+w,y+h)
			self.ml.addMap(self.map,1,1)
			self.ml.addLinear(mapnode,1,1)
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


