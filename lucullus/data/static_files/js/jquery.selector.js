
jQuery.selectArea = function(callback, options) {
    /* This is a tool to select an area. Use obj.start(callback) to start it. */
    var obj = this
    this.settings = jQuery.extend({
        color: 'darkblue',
        bordercolor: 'blue',
        opacity: 0.2,
        showhelp: true,
        helptext: 'Press and hold your left mouse button to select an area on the screen.',
        dragtext: 'Release the mouse button to finish, press escape to abort.',
        onstart: function(){},
        onchange: function(){}
    }, options)

    this.callback = callback
    this.startX = NaN
    this.startY = NaN
    this.stopX = NaN
    this.stopY = NaN
    this.area = [NaN, NaN, NaN, NaN]
    this.aborted = false
    this.node = $('<div />')
      .css('background-color', this.settings.color)
      .css('border','1px solid '+ this.settings.bordercolor)
      .css('position','absolute')
      .css('z-index','9999')
      .css('display','none')
      .css('overflow','hidden')
      .css('opacity', this.settings.opacity + '')
    this.node.appendTo($('body'))

    this.protect = $('<div />')
      .css('position','fixed')
      .css('width','100%')
      .css('height','100%')
      .css('top','0px')
      .css('left','0px')
      .css('z-index','9999')
    this.protect.appendTo($('body'))
    
    this.status = $('<div />')
      .css('background-color','white')
      .css('border-bottom','1px solid grey')
      .css('color','black')
      .css('text-align','center')
      .css('display', this.settings.showhelp ? 'block' : 'none')
    this.status.text(this.settings.helptext)
    this.status.appendTo(this.protect)

    this.on_start = function(event) {
        event.stopPropagation()
        event.preventDefault()
        obj.startX = event.pageX
        obj.startY = event.pageY
        obj.status.text(obj.settings.dragtext)
        obj.protect.bind('mousemove', obj.on_move);
        obj.protect.bind('mouseup', obj.on_end);
        $(document).bind('keyup', obj.on_end);
        obj.on_move(event)
        obj.settings.onstart(obj)
    }

    this.on_move = function(event) {
        event.stopPropagation()
        event.preventDefault()
        obj.stopX = event.pageX
        obj.stopY = event.pageY
        obj.area[0] = Math.min(obj.startX, obj.stopX)
        obj.area[1] = Math.min(obj.startY, obj.stopY)
        obj.area[2] = Math.max(obj.startX, obj.stopX)
        obj.area[3] = Math.max(obj.startY, obj.stopY)
        obj.node
          .css('display','block')
          .css('left', obj.area[0]+'px')
          .css('top', obj.area[1]+'px')
          .css('width', Math.max(1, obj.area[2]-obj.area[0]-2)+'px')
          .css('height', Math.max(1, obj.area[3]-obj.area[1]-2)+'px')
          obj.settings.onchange(obj, event)
    }

    this.on_end = function(event) {
        event.stopPropagation()
        event.preventDefault()
        if (event) {
            if (event.type == 'mouseup') {
                obj.on_move(event)
            } else if (event.type == 'keyup' && event.keyCode == 27) {
                obj.aborted = true
            } else { return }
        }
        obj.protect.unbind('mousedown', obj.on_start);
        obj.protect.unbind('mousemove', obj.on_move);
        obj.protect.unbind('mouseup', obj.on_end);
        $(document).unbind('keyup', obj.on_end);
        obj.node.remove()
        obj.protect.remove()
        if(obj.callback)
            obj.callback(obj)
    }

    this.protect.bind('mousedown', this.on_start);
    this.protect.bind('mousemove', this.on_move);
}
