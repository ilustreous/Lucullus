/**
 * Lucullus Namespace
 */

var Lucullus = new Object();

Lucullus.current = null // Current connected API




/**
 * Request class
 * Used for delayed execution of callback functions on ajax requests.
 * Understands Lucullus API 1.0 error responses
 * @class Request
 * @constructor
 */

Lucullus.Trigger = function() {
    /** List of bound callbacks 
     * @type Array */
    this.callbacks = Array()
    /** Result object after calling self.finish(result) */
    this.result = null
    /** Error object after calling self.abort(error) */
    this.error = null
    this.aborted = false
}

/** Bind new callbacks.
 * Each callback is called once with the trigger object as its first argument as soon as possible.
 * You can recover from errors with t.finish(). All remaining callbacks will see a finished trigger 
 */

Lucullus.Trigger.prototype.wait = function() {
    var self = this
    jQuery.each(arguments, function(i, f) {
        if(jQuery.isFunction(f)) {
            self.callbacks.push(f)
        }
    })
    if(this.result) {
        while(this.callbacks.length && !this.aborted) {
            var c = this.callbacks.shift()
            c(this)
        }
    }
    return this
}

/** Recover from an error
 * @param newdata overwrite result object from error response **/
Lucullus.Trigger.prototype.success = function(result) {
    this.result = result
    this.error = null
    this.wait()
    return this
}

/** Recover from an error
 * @param newdata overwrite result object from error response **/
Lucullus.Trigger.prototype.fail = function(error, result) {
    this.result = result ? result : null
    this.error = error ? error : true
    this.wait()
    return this
}


/** Abort execution of other callbacks **/
Lucullus.Trigger.prototype.abort = function() {
    this.aborted = true
    return this
}

/** Recover from an error
 * @param newdata overwrite result object from error response **/
Lucullus.Trigger.prototype.recover = function(newdata) {
    if(!newdata)
        newdata = this.result
    this.aborted = false
    return this.success(newdata)
}








/**
 * Request class
 * Used for delayed execution of callback functions on ajax requests.
 * Understands Lucullus API 1.0 error responses
 * @class Request
 * @constructor
 */

Lucullus.Request = function(url, data, delayed) {
    this.constructor()
    /** URL for the request **/
    this.url = url
    /** Request Data (if any) **/
    this.data = (typeof data == 'object') ? data : null
    this.started = false
    if(!delayed) this.start()
}

Lucullus.Request.prototype = new Lucullus.Trigger()

Lucullus.Request.prototype.start = function() {
    if(this.started) return
    this.started = true
    var self = this
    jQuery.ajax({
        url: this.url,
        data: this.data,
        dataType: "json",
        type: "POST",
        success: function(d){
            if(typeof d !== 'object')
                d = {'error': 'no data', 'detail': 'Response did not contain any data'}
            if(d.error)
                self.fail(d.error, d)
            else
                self.success(d)
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            self.fail('http error', {'message':'HTTP Error: '+textStatus, 'HTTPStatus':textStatus})
        }
    });
}

/** Repeat the request with new data (to recover from errors)
 * @param newdata overwrite original data object **/

Lucullus.Request.prototype.restart = function(newdata) {
    this.data = (typeof newdata == 'object') ? newdata : null
    this.started = false
    this.start()
    return this
}






/**
 * API Object
 * @class Server API (evend based asyc execution)
 * @constructor
 */

Lucullus.api = function(server, key) {
    /** API location (url) http://www.example.com/seqmap/api 
     * @type string */
    this.server     = server
    /** API key 
     * @type string */
    this.key        = key
    /** List of known resources 
     * @type Dict */
    this.resources  = {}
    this.debug = function(msg){alert(msg)}
    Lucullus.current = this
}


/**
 * Calls an API method of a Lucullus Server
 * @param {string} Name of the API method
 * @param {string} Data to provide
 * @param {function} Callback
 * @return Lucutus.call object with $this attached to $call.api
 */

Lucullus.api.prototype.query = function(action, options, delayed) {
    var url = this.server + '/' + action
    if(options)
        options['apikey'] = this.key
    var request = new Lucullus.Request(url, options, delayed)
    request.api = api
    return request
}

/**
 * Creates a new Resource and returns a resource object equipped with
 * available api methods.
 * @param {string} type Type of the resource (one of api.plugins)
 * @param {function} Callback
 * @return Lucullus.Resource object
 */
Lucullus.api.prototype.create = function(type, options) {
    var resource = new Lucullus.Resource(this, type, options)
    var self = this
    resource.wait(function(response) {
        self.resources[resource.id] = resource
    })
    return resource
}







/**
 * Creates a server resource of a specific type.
 * @param {Lucullus.Api} api Session to use
 * @param {string} type Name of the resource classto create
 * @param {string} name Optional identifying name of the to-be-creates resource (overwriting existing)
 */
Lucullus.Resource = function(api, type, options) {
    this.api = api // API reference
    this.id = null // Resource ID
    this.type = type // Resource type
    this.methods = Array() // API methods for this resource
    this.state = Object() // Resource state
    this.queue = new Array() // All querys (executed and waiting)
    this.error_at = null // Index of Last error respose that stopped the queue
    var self = this
    
    // Request resource on server
    if(typeof options != 'object')
        var options = {}
    options['type'] = type
    var request = this.api.query('create', options)
    request.wait(function(response) {
        if(response.result && !response.error) {
            rid = response.result.id
            state = response.result.state
            methods = response.result.methods
            if(typeof rid !== 'string' || typeof rid !== 'number')
                self.id = rid
            if(typeof state === 'object') 
                self.self_update(state)
            if(jQuery.isArray(methods)) {
                this.methods = methods
                jQuery.each(methods, function(i, name) {
                    if(typeof self[name] === 'undefined') {
                        self[name] = function(opt) {
                            return self.query(name, opt)
                        }
                    }
                });
            }
        } else {
            self.api.debug("Could not create resource type" + self.type)
            self.error_at = 0
            response.abort()
        }
    })
    this.queue.push(request)
}


Lucullus.Resource.prototype.setup = function(opt) {
    return this.query('setup', opt)
}

/** Returns the last entry in the query queue */
Lucullus.Resource.prototype.lastquery = function() {
    return this.queue.slice(-1)[0]
}


/** Same as Request.lastquery().wait() */
Lucullus.Resource.prototype.wait = function() {
    var request = this.lastquery()
    jQuery.each(arguments, function(i, f) {
        if(jQuery.isFunction(f)) {
            request.wait(f)
        }
    })
    return this
}



/**
 * Runs a server resource api call and updates local attributes.
 * Does nothing if this.error() is true. Use this.recover() to continue.
 * Callbacks bound to the returned Trigger are executed before callbacks bound with Resource.wait()
 * @param {string} action Action to call
 * @param {object} parameter Dict of call parameters
 * @param {function} Callback
 * @return Trigger object with .resource, .request and .api attributes
 */
Lucullus.Resource.prototype.query = function(action, options) {
    var self = this
    if(!options) var options = {}
    var request = this.api.query('r' + this.id + '/' + action, options, true)
    var trigger = new Lucullus.Trigger()
    trigger.resource = this
    trigger.api = this.api
    trigger.request = request
    /* This is the first callback for this response.
       The start calls for future requests are bound later.
       An abort() will prevent these from being started */
    request.wait(function(response){
        if(response.error) {
            self.error_at = jQuery.inArray(response, self.queue)
            response.abort()
            trigger.fail(response.error, response.result)
            return
        }
        if(typeof response.result.state === 'object') {
            self.self_update(response.result.state)
        }
        if(response.result.result)
            trigger.success(response.result.result)
        else
            trigger.success({})
    })
    // Add to queue. Now it is accessable via Request.wait()
    var index = this.queue.push(trigger.request)
    // Make sure that this requests starts as soon as the previous one ends
    this.queue[index-2].wait(function(){
        if(self.error_at === null)
            request.start()
    })
    return trigger
}

Lucullus.Resource.prototype.close = function() {
    return this.query('close')
}

Lucullus.Resource.prototype.recover = function() {
    var e = this.error()
    if(e) {
        this.error_at = null
        e.recover({id:this.id})
    }
}

/**
 * Used to update attributes without overwriting default attributes or functions.
 * @param {object} dict Dictionary of new (or changed) attributes
 * @return Resource object (self)
 */
Lucullus.Resource.prototype.self_update = function(dict) {
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
 * Returns the request that caused an error, if any
 * @return Request object
 */
Lucullus.Resource.prototype.error = function() {
    if(this.error_at === null)
        return null
    else
        return this.queue[this.error_at]
}


Lucullus.Resource.prototype.imgurl = function(channel, x, y, width, height, format) {
    return this.api.server + '/r' + this.id + '/default-'+x+'-'+y+'-'+width+'-'+height+'.'+format+'?mtime=' + self.mtime
}














































Lucullus.ViewMap = function (root, view) {
    var self = this
    /* Shows a view in an element using a movable tile map */
    this.view = view
    this.root = $(root)
    this.node = $('<div></div>')

    /* Default values */
    this.clipping = [0,0,0,0]           // minimum and maximum pixel to show
    this.manclipp = [-Number.MAX_VALUE, -Number.MAX_VALUE, Number.MAX_VALUE, Number.MAX_VALUE]          // minimum and maximum pixel as set by user
    this.tilesize = [256,256]           // Size of a tile in pixel
    this.tiles    = [0,0]               // Number of tiles
    this.offset   = [0,0]               // Current offset (negative position of the upper left corner relative to the data area)

    this.map =  null
    this.buffer = null

    // Some caches for faster processing
    this.mapsize = [0,0]                // Size of viewable area
    this.mapoffset = [0,0]              // Position of map
    this.bufferoffset = [0,0]           // Position of buffer
    
    this.refresh_speed = 500
    this.refresh_interval = null
    this.overlap = 0
    
    // Setup
    this.node.css('overflow','hidden')
    this.node.css('position','relative')
    this.resize(this.root.innerWidth(), this.root.innerHeight())
    this.root.empty()
    this.root.append(this.node)
    // Start refresh loop when ready.
    this.view.wait(function() {
        self.refresh()
        self._refresh()
    })
}

Lucullus.ViewMap.prototype.resize = function(w, h) {
    // Resizes the map node
    w = w ? w : 0
    h = h ? h : 0
    this.node.width(w)
    this.node.height(h)
    var tiles_x = Math.ceil(w / this.tilesize[0] ) + 1 + this.overlap * 2
    var tiles_y = Math.ceil(h / this.tilesize[1] ) + 1 + this.overlap * 2
    this.mapsize = [w, h]
    this.tiles = [tiles_x, tiles_y]
    this.refresh()
}

Lucullus.ViewMap.prototype._refresh = function() {
    /* Adds a new map whenever needed (call every second or so) */
    if(this.mapoffset[0] > 0
    || this.mapoffset[0] + this.tiles[0]*this.tilesize[0] < this.mapsize[0]
    || this.mapoffset[1] > 0
    || this.mapoffset[1] + this.tiles[1]*this.tilesize[1] < this.mapsize[1] ) {
        this.refresh()
    }

    var self = this
    this.refresh_interval = setTimeout(function(){self._refresh()}, this.refresh_speed)
    return
}

Lucullus.ViewMap.prototype.imgurl = function(numberx, numbery, sizex, sizey) {
    return this.view.imgurl('default', (numberx*sizex), (numbery*sizey), sizex, sizey, 'png')
}


Lucullus.ViewMap.prototype.refresh = function () {
    var self = this
    // If the map is not visible, we don't have to do anything
    if(this.mapsize[0] == 0 || this.mapsize[1] == 0) return
    // React on changed view parameter
    if(this.view && !this.view.error() && this.view.width && this.view.height && this.view.offset) {
        var width = this.view.width
        var height = this.view.height
        var ox = this.view.offset[0]
        var oy = this.view.offset[1]
        this.clipping[0] = Math.max(ox, this.manclipp[0])
        this.clipping[1] = Math.max(oy, this.manclipp[1])
        this.clipping[2] = Math.min(width+ox, this.manclipp[2])
        this.clipping[3] = Math.min(height+oy, this.manclipp[3])
    } else {
        this.node.empty()
        return
    }
    
    // Index number of top left tile
    var nx = Math.floor(-this.offset[0] / this.tilesize[0]) - this.overlap
    var ny = Math.floor(-this.offset[1] / this.tilesize[1]) - this.overlap
    // Total offset of top left tile
    var ox = nx * this.tilesize[0] 
    var oy = ny * this.tilesize[1] 
    // Offset of top left tile relative to visible area
    var vox = ox+this.offset[0]
    var voy = oy+this.offset[1]

    if(this.buffer) {
        this.buffer.remove()
    }

    if(this.map){
        this.buffer = this.map
        this.bufferoffset = this.mapoffset
    }

    this.map = $('<div style="position:absolute; left:'+vox+'px; top:'+voy+'px; width:'+(this.mapsize[0])+'px; height:'+(this.mapsize[1])+'px">Loading...</div>')
    this.mapoffset = [vox, voy]
    this.map.html(this.imagetiles(nx, ny))
    this.node.append(this.map)
    
    if(this.cRefresh) this.cRefresh()
}

Lucullus.ViewMap.prototype.imagetiles = function(nx, ny) {
    /* Fills the current map with images using (nx,ny) as number of top left tile and (cx,cy) as number of tiles to show */
    var tx = this.tilesize[0]
    var ty = this.tilesize[1]
    var cx = this.tiles[0]
    var cy = this.tiles[1]
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
            } else {
                images.push('<div style="position:absolute; width:'+tx+'px; height:'+ty+'px; left:'+ox+'px; top:'+oy+'px;">No Image</div>')
            }
        }
    }
    return images.join("\n")
}

Lucullus.ViewMap.prototype.set_clipping = function(x,y,w,h) {
    /** Sets the size of the mapping area and invokes a refresh.*/
    this.manclipp = [x,y,x+w,y+h]
}

Lucullus.ViewMap.prototype.normalise_move = function(dx,dy) {
    /* Normalizes a movement (clipping) */
    if(!dx) dx=0
    if(!dy) dy=0
    dx = Math.min(- this.clipping[0], Math.max(this.mapsize[0] - this.clipping[2], this.offset[0] + Math.round(dx))) - this.offset[0]
    dy = Math.min(- this.clipping[1], Math.max(this.mapsize[1] - this.clipping[3], this.offset[1] + Math.round(dy))) - this.offset[1]
    return [dx, dy].slice()
}

Lucullus.ViewMap.prototype.move = function(dx, dy) {
    /* Moves the map (and buffer) by (dx,dy) pixel and returns the actual movement */
    if(!this.map) return
    // Normalise movement (clipping)
    [dx, dy] = this.normalise_move(dx, dy)

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
    if(this.cMove) this.cMove(dx,dy)
    return [dx, dy].slice()
}

Lucullus.ViewMap.prototype.scroll = function(x,y,step,speed) {
    // Move smoothly
    var obj = this
    if(!step) var step = 0.2
    if(!speed) var speed = 10
    var m = this.normalise_move(x, y)
    if(m[0] == 0 && m[1] == 0) return
    this.move(m[0]*step, m[1]*step)
    setTimeout(function() {obj.scroll(m[0]*(1-step), m[1]*(1-step), step, speed)}, speed)
}

Lucullus.ViewMap.prototype.move_to = function(x,y) {
    // Move to a fixed position
    if(x==null) x = this.offset[0]
    if(y==null) y = this.offset[1]
    var dx = x - this.offset[0]
    var dy = y - this.offset[1]
    this.move(dx, dy)
    return this.offset.slice()
}

Lucullus.ViewMap.prototype.scroll_to = function(x,y,step,speed) {
    // scroll to a fixed position
    if(x==null) x = this.offset[0]
    if(y==null) y = this.offset[1]
    var dx = x - this.offset[0]
    var dy = y - this.offset[1]
    this.scroll(dx, dy, step, speed)
}

Lucullus.ViewMap.prototype.get_size = function() {
    /** Returns the width and height of the viewable area */
    return [this.mapsize[0], this.mapsize[1]]
}

Lucullus.ViewMap.prototype.get_datasize = function() {
    /** Returns the width and height of the data area */
    return [this.clipping[2] - this.clipping[0], this.clipping[3] - this.clipping[1]]
}

Lucullus.ViewMap.prototype.get_position = function() {
    /** returns the current position of the upper left corner relative to the data area */
    return [- this.offset[0], - this.offset[1]]
}

Lucullus.ViewMap.prototype.get_center = function() {
    /** returns the current focus (center) of the map */
    x = this.get_position()[0] + this.get_size()[0] / 2
    y = this.get_position()[1] + this.get_size()[1] / 2
    return [x,y]
}

Lucullus.ViewMap.prototype.get_position_by_absolute = function(x,y) {
    /** Sets the size of the mapping area and invokes a refresh.*/
    x = x - this.node.offset().left - this.offset[0]
    y = y - this.node.offset().top - this.offset[1]
    return [x,y].slice()
}








/**
 * Listener for mouse movements
 * @constructor
 */
Lucullus.DragListener = function(element) {
    /** Tracks Drag&Drop starting from element without doing anything. */
    this.element = $(element)
    this.moving = false         // Currently moving ?

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
    this.listener   = []    // registred listener. ListenerObject, mode(0dead, 1linear, 2distance), scalex, scaley
    this.maps       = []    // registred maps to move
    this.speed      = 50

    var obj = this  // Used for events

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
        
        if(x||y) obj.move(x,y)
        // Do it again and again and ...
        obj.interval = setTimeout(obj.tick, obj.speed);
    }
    
    this.move = function(x, y) {
        // Move every connected map
        jQuery.each(obj.maps, function(i, map) {
            map[0].move(x*map[1],y*map[2])
        })
    }
    
    this.scroll = function(x, y, step, speed) {
        // Move every connected map
        jQuery.each(obj.maps, function(i, map) {
            map[0].scroll(x*map[1],y*map[2], step, speed)
        })
    }
    
    this.move_to = function(x, y) {
        jQuery.each(obj.maps, function(i, map) {
            var ix = x
            var iy = y
            if(ix) ix *= map[1]
            if(iy) iy *= map[2]
            map[0].move_to(ix,iy)
        })
    }

    this.scroll_to = function(x, y) {
        jQuery.each(obj.maps, function(i, map) {
            var ix = x
            var iy = y
            if(ix) ix *= map[1]
            if(iy) iy *= map[2]
            map[0].scroll_to(ix,iy)
        })
    }

    this.interval = setTimeout(obj.tick, obj.speed);
}


