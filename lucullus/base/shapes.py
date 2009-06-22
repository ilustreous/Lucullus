import math

def path_roundrectangle(c,x,y,w,h,rx=0,ry=0,rrx=0.5,rry=0.5,border=0):
	""" Rectangle with rounded corners.
		x/y	    Position
		w/h	    Size
		rx/ry   Corner radius
		rrx/rry Roundness of corner. 0.0 (cut) 0.5 (round) 1.0 (peak)
		border	Size of border"""
	# Shrink shape to draw border within w/h
	if border != 0.0:
		x += border
		y += border
		w -= border*2
		h -= border*2
		rx -= border/2
		ry -= border/2
	# Cap ry,ry,rrx and rry to sane values
	rx = max(0.0,min(rx,w/2))
	ry = max(0.0,min(ry,h/2))
	rrx = max(0.0,min(1.0,rrx))
	rry = max(0.0,min(1.0,rry))
	# Draw the path beginning with the top right corner
	c.move_to(x+w-rx,y)
	c.curve_to(x+w-rx+rx*rrx,y,x+w,y+ry-ry*rry,x+w,y+ry)
	if h > ry*2: c.line_to(x+w,y+h-ry)
	c.curve_to(x+w,y+h-ry+ry*rry,x+w-rx+rx*rrx,y+h,x+w-rx,y+h)
	if w > rx*2: c.line_to(x+rx,y+h)
	c.curve_to(x+rx-rx*rrx,y+h,x,y+h-ry+ry*rry,x,y+h-ry)
	if h > ry*2: c.line_to(x,y+ry)
	c.curve_to(x,y+ry-ry*rry,x+rx-rx*rrx,y,x+rx,y)
	c.close_path()
	
def path_arrowd(c,x,y,w,h,t=0.25,s=0.25,b=0.0,border=0.0):
	""" Dynamic Arrow (head parameter are relative to arrow size)
		x/y	    Position
		w/h	    Size
		t		Length of head (relative to w)
		s		Boldness of tail (relative to h)
		b		
		border	"""
	if border != 0.0:
		x += border
		y += border
		w -= border*2
		h -= border*2

	c.move_to(x,y+(h-h*s)/2)
	c.line_to(x+w-w*t,y+(h-h*s)/2)
	c.line_to(x+w-w*t-w*b,y)
	c.line_to(x+w,y+h/2)
	c.line_to(x+w-w*t-w*b,y+h)
	c.line_to(x+w-w*t,y+(h+h*s)/2)
	c.line_to(x,y+(h+h*s)/2)
	c.close_path()

def path_arrow(c,x,y,w,h,t,s,b=0.0,border=0.0):
	""" Arrow with fixed head
		x/y	    Position
		w/h	    Size
		t		Length of head
		s		Boldness of tail
		b		Size of 
		border	"""
	'''               |--t--|
	              |-b-|
	              o 
	               oo
	                o o
	- oooooooooooooooo  o
	| o                   o
	s o                     o
	| o                   o
	- oooooooooooooooo  o
	                o o
	               oo
	              o
	''' 
	if border != 0.0:
		x += border
		y += border
		w -= border*2
		h -= border*2

	c.move_to(x,y+(h-s)/2)
	c.line_to(x+w-t,y+(h-s)/2)
	c.line_to(x+w-t-b,y)
	c.line_to(x+w,y+h/2)
	c.line_to(x+w-t-b,y+h)
	c.line_to(x+w-t,y+(h+s)/2)
	c.line_to(x,y+(h+s)/2)
	c.close_path()
		

def path_tube(c,x,y,w,h,border=0.0):
	if border != 0.0:
		x += border
		y += border
		w -= border*2
		h -= border*2

	c.move_to(x+w-h/2,y)
	c.line_to(x+w-h/2,y+h)
	c.line_to(x+h/2,y+h)
	c.arc(x+h/2,y+h/2,h/2,90.0/180*math.pi,270.0/180*math.pi)
	c.close_path()

