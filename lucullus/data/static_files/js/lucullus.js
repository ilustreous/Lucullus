/**
 * API Object
 * @class Server API (evend based asyc execution)
 * @constructor
 */

function Lucullus() {}

Lucullus.api = function (server, key) {
	/** API location (url) http://www.example.com/seqmap/api 
	 * @type string */
	this.server		= server
	/** API key 
	 * @type string */
	this.key		= key
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
 * Creates a new Resource and returns a resource object equipped with
 * available api methods.
 * @param {string} type Type of the resource (one of api.plugins)
 * @param {function} Callback
 * @return Lucullus.Resource object
 */
Lucullus.api.prototype.create = function(type, options) {
	var r = new Lucullus.Resource(this, type, options)
	r.wait(function(c) {
		if(! c.resource.error) {
			c.api.resources[c.resource.id] = c.resource
		}
	})
	return r
}


/**
 * Calls a API method of a Lucullus Server
 * @param {string} Name of the API method
 * @param {string} Data to provide
 * @param {function} Callback
 * @return Lucutus.call object with $this attached to $call.api
 */

Lucullus.api.prototype.query = function(action, options) {
	var self = this
	var url = self.server + '/'
	
	if(self.session) {
		url = url + self.session + '/'
	}

	url = url + action
 	var c = new Lucullus.Call()
	c.api = this
	c.run(url, options)
	self.log.push(c)
	return c
}



/**
 * Waits for one or many callbacks or resources to complete
 * @param {object} calls List of call or resource objects
 * @param {function} Callback
 */
Lucullus.wait = function (o, callback) {
	var count = o.length
	while(o.length) {
		var c = o.shift()
		c.wait(function(ca) {
			count = count - 1
			if(!count) {
				callback(ca)
			}
		})
	}
}




















/**
 * Handles a single ajax request.
 * @param {Lucullus.Api} api Api object to use
 * @param {strng} url URL to call (null to delay request. See Call.run())
 * @param {object} parameter Dict of POST parameters
 * @param {function} callback Function to call when finished (using the call object as parameter)
 * @return Call object (self)
 */
Lucullus.Call = function(url, parameter, callback, notnow) {
	this.url = null
	this.parameter = null
	this.callbacks = []

	this.started = false
	this.done = false

	this.result = null
	this.error = null

	this.run(url, parameter, callback, notnow)
}

/**
 * Starts the request 
 * @param {strng} url URL to call (optional, overwrites initial url)
 * @param {object} parameter Dict of POST parameters  (optional, overwrites initial parameter)
 * @param {function} callback Function to call when finished (using the call object as parameter)
 * @return Call object (self)
 */

Lucullus.Call.prototype.run = function(url, parameter, callback, notnow) {
	if(this.started || this.done)
		return this
	if(typeof url === 'string')
		this.url = url
	if(typeof parameter === 'object')
		this.parameter = parameter
	if(typeof callback === 'function')
		this.wait(callback)

	if(this.url && ! notnow) {
		this.started = true
		var self = this
		jQuery.ajax({
			url: self.url,
			data: self.parameter,
			dataType: "json",
			type: 'post',
			success: function(data){
				if(data && !data.error) {
					self.result = data
				} else if(data && data.error) {
					self.fail(data.error, data)
				} else if(data) {
					self.fail('Unexpected answer', {'answer':data})
				} else {
					self.fail('No answer')
				}
			},
			complete: function() {
				self.done = true
				self.wait()
			}
		});
	}
	return this
}

Lucullus.Call.prototype.fail = function(message, data) {
	if(this.done)
		return
	if(typeof data !== 'object')
		data = {'data':data}
	this.error = data
	this.error['message'] = message
	this.done = true
	this.wait()
}

/**
 * Runs a callback as soon as the call is finished.
 * Callbacks are executed in-order. 
 * @param {function} callback Function to call (using the call object as parameter)
 * @return Call object (self)
 */
Lucullus.Call.prototype.wait = function(callback) {
	if(callback && typeof callback === 'function')
	  this.callbacks.push(callback)
	if(this.done) {
		while(this.callbacks.length) {
			var c = this.callbacks.shift()
			c(this)
		}
	}
}













/*
  new Resource() tries to create a new resource
  r.query() returns call objects bount to that resource
  
*/




/**
 * Creates a server resource of a specific type.
 * @param {Lucullus.Api} api Session to use
 * @param {string} type Name of the resource classto create
 * @param {string} name Optional identifying name of the to-be-creates resource (overwriting existing)
 */
Lucullus.Resource = function(api, type, options) {
	this.api = api
	this.id	= name
	this.type = type
	this.error = null
	this.queue = []
	this.current = null
	var self = this
	
	// Request resource on server
	if(!options) var options = {}
	options['type'] = type
	options['apikey'] = self.api.key
    var call = this.api.query( 'create', options)
	self.current = call
	call.resource = self

	// Configure self and bind a functin for every 'apis' name
	call.wait(function(c) {
		if(c.result) {
			if(typeof c.result.id === 'string' || typeof c.result.id === 'number') {
				c.resource.id = c.result.id
				if(typeof c.result.state === 'object')
					c.resource.update(c.result.state)
				if(typeof c.result.api === 'object') {
					jQuery.each(c.result.api, function(i, name) {
						if(typeof c.resource[name] === 'undefined') {
							c.resource[name] = function(opt) {
								return self.query(name, opt)
							}
						}
					});
				}
			} else {
				c.resource.error = c.result
				c.resource.error['message'] = "No resource ID! Initialisation failed?"
			}
		} else {
			c.resource.error = c.error
		}
	})
}

/**
 * Used to update attributes without overwriting default attributes or functions.
 * @param {object} dict Dictionary of new (or changed) attributes
 * @return Resource object (self)
 */
Lucullus.Resource.prototype.update = function(dict) {
	var self = this
	jQuery.each(dict, function(key, val) {
		// Protect important attributes
		if(-1 != jQuery.inArray(key, ['api','id','type','error','queue','current']))
		  return
		// Protect functions
		if(typeof self[key] == 'function')
		  return
		// Set attribute
		self[key] = val
	});
	return self
}

/**
 * Waits for all current calls to finish
 * Callbacks are executed in-order.
 * @param {function} callback Function to call (using the call object as parameter)
 * @return Call object (self)
 */
Lucullus.Resource.prototype.wait = function(callback) {
	
	if(typeof callback == 'function') {
		this.current.wait(callback)
	}
}

/**
 * Waits for all current calls to finish
 * Callbacks are executed in-order.
 * @param {function} callback Function to call (using the call object as parameter)
 * @return Call object (self)
 */
Lucullus.Resource.prototype.onerror = function(callback) {
	if(typeof callback == 'function') {
		this.current.wait(function(c) {
			if(c.error)
				callback(c)
		})
	}
}



/**
 * Runs a server resource setup call and updates local attributes.
 * Does nothing if this.error is true. Delete this.error to recover from errors.
 * @param {object} parameter Dict of call parameters
 * @param {function} Callback
 * @return Call object with $this attached to $call.resource ad $this.api attached to $call.api
 */
Lucullus.Resource.prototype.setup = function(options, callback) {
	var self = this
	var url = this.api.server + '/r' + this.id + '/setup'
	if(!options) var options = {}
	options['apikey'] = self.api.key
	var call = new Lucullus.Call(url, options, callback, true)
	call.resource = this
	call.wait(function(c) {
		if(c.result) {
			if(typeof c.result.id !== 'undefined' && c.result.id == c.resource.id) {
				if(typeof c.result.state === 'object')
					c.resource.update(c.result.state)
			} else {
				c.resource.error = c.result
				c.resource.error['message'] = "Resource ID mismatch!"
			}
		} else {
			c.resource.error = c.error
		}
	})

	/* Calls are limited to one call per resource at a time, so we use the wait() queue of the last call to start the current call */
	this.queue.push(call)
	var old = self.current
	self.current = call

	old.wait(function() {
		var next = self.queue.shift()
		if(next) {
			next.run()
		}
	})

	return call
}






/**
 * Runs a server resource api call and updates local attributes.
 * Does nothing if this.error is true. Delete this.error to recover from errors.
 * @param {string} action Action to call
 * @param {object} parameter Dict of call parameters
 * @param {function} Callback
 * @return Call object with $this attached to $call.resource ad $this.api attached to $call.api
 */
Lucullus.Resource.prototype.query = function(action, options, callback) {
	var self = this
	var url = this.api.server + '/r' + this.id + '/' + action
	if(!options) var options = {}
	options['apikey'] = self.api.key
	var call = new Lucullus.Call(url, options, callback, true)
	call.api = this.api
	call.resource = this
	call.wait(function(c) {
		if(c.result) {
			if(typeof c.result.id !== 'undefined' && c.result.id == c.resource.id) {
				if(typeof c.result.state === 'object')
					c.resource.update(c.result.state)
			} else {
				c.resource.error = c.result
				c.resource.error['message'] = "Resource ID mismatch!"
			}
		} else {
			c.resource.error = c.error
		}
	})

	/* Calls are limited to one call per resource at a time, so we use the wait() queue of the last call to start the current call */
	this.queue.push(call)
	var old = self.current
	self.current = call

	old.wait(function() {
		var next = self.queue.shift()
		if(next) {
			next.run()
		}
	})

	return call
}















Lucullus.ViewMap = function (element, view) {
	/* Shows a view in an element using a movable tile map */
	this.view = view
	this.node = $('<div></div>')
	this.node.css('overflow','hidden')
	this.node.css('position','relative')
	this.node.css('width','100%')
	this.node.css('height','100%')
	$(element).empty()
	$(element).append(this.node)

	/* Default values */
	this.clipping = [0,0,0,0]			// minimum and maximum pixel to show
	this.manclipp = [-Number.MAX_VALUE, -Number.MAX_VALUE, Number.MAX_VALUE, Number.MAX_VALUE]			// minimum and maximum pixel as set by user
	this.tilesize = [256,256]			// Size of a tile in pixel
	this.offset = [0,0]					// Current offset

	this.map =  null
	this.buffer = null

	// Some caches for faster processing
	this.mapsize = [0,0,0,0]			// Size of viewable area and map container (minx, miny, maxx, maxy)
	this.mapoffset = [0,0]				// Position of map
	this.bufferoffset = [0,0]			// Position of buffer
	
	this.refresh_speed = 500
	this.refresh_interval = null

	var obj = this
	obj.refresh = function() {
		/* Adds a new map whenever needed (call every second or so) */
	    if(obj.mapoffset[0] > 0
		|| obj.mapoffset[0] + obj.mapsize[2] < obj.mapsize[0]
		|| obj.mapoffset[1] > 0
		|| obj.mapoffset[1] + obj.mapsize[3] < obj.mapsize[1] )
			obj.new_map()

		obj.refresh_interval = setTimeout(obj.refresh, obj.refresh_speed)
	    return
	}

	this.view.wait(function(c) {
		obj.new_map()
		obj.refresh()
	})
	
}


Lucullus.ViewMap.prototype.new_map = function () {
	if(this.view && !this.view.error && this.view.width && this.view.height && this.view.offset) {
		var width = this.view.width
		var height = this.view.height
		var ox = this.view.offset[0]
		var oy = this.view.offset[1]
		this.clipping[0] = Math.max(ox, this.manclipp[0])
		this.clipping[1] = Math.max(oy, this.manclipp[1])
		this.clipping[2] = Math.min(width+ox, this.manclipp[2])
		this.clipping[3] = Math.min(height+oy, this.manclipp[3])
		var obj = this
		obj.imgurl = function(numberx, numbery, sizex, sizey) {
			return obj.view.api.server + '/r' + obj.view.id + '/x'+(numberx*sizex)+'y'+(numbery*sizey)+'w'+sizex+'h'+sizey+'.png'
		}
	} else {
		return
	}
	
	this.node.width(this.node.parent().width()+'px')
	this.node.height(this.node.parent().height()+'px')
	var w = this.node.width()
	var h = this.node.height()
	this.mapsize = [w,h,0,0]
	if(h == 0 || w == 0) return
	// Number of tiles that fit into that area (+1 for a spare tile in every direction)
	var overlap = 0 // Spare tiles in every direction (mor tiles, fewer refreshes)
	var tiles_x = Math.ceil(w / this.tilesize[0] ) + 1 + overlap * 2
	var tiles_y = Math.ceil(h / this.tilesize[1] ) + 1 + overlap * 2
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
	this.map.html(this.imagetiles(nx, ny, tiles_x, tiles_y))
	this.node.append(this.map)
}

Lucullus.ViewMap.prototype.imagetiles = function(nx, ny, cx, cy) {
	/* Fills the current map with images using (nx,ny) as number of top left tile and (cx,cy) as number of tiles to show */
	var tx = this.tilesize[0]
	var ty = this.tilesize[1]
	var images = []
	for(var y=0; y<cy; y++) {
		for(var x=0; x<cx; x++) {
			// Image URL
			var url = this.imgurl(x+nx, y+ny, tx, ty)
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
	return images.join("\n")
}
	
Lucullus.ViewMap.prototype.move = function(dx, dy) {
	/* Moves the map (and buffer) by (dx,dy) pixel and returns the actual movement */

	// Normalise movement (clipping)
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
	if(this.map) {
		this.map.css({'left': this.mapoffset[0] + 'px', 'top': this.mapoffset[1] + 'px'})
	}
	
	if(this.buffer) {
		this.bufferoffset[0] += dx
		this.bufferoffset[1] += dy
		this.buffer.css({'left': this.bufferoffset[0] + 'px', 'top': this.bufferoffset[1] + 'px'})
	}

	return [dx, dy].slice()
}

Lucullus.ViewMap.prototype.set_clipping = function(x,y,w,h) {
	/** Sets the size of the mapping area and invokes a refresh.*/
	this.manclipp = [x,y,x+w,y+h]
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












