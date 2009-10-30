#!/usr/bin/env python
# encoding: utf-8
"""
cimg.py

Created by Marcel Hellkamp on 2008-01-11.
Copyright (c) 2008 Marcel Hellkamp. All rights reserved.

Base classes for cairo renderer.
class CimgTarget (CimgTargetFile, ...)
  Desctiptor for render destinations (svg, png, GTK-surface,...)
class Cimg
  Base class for render engines

Exception Tree
  InvalidSourceException
  OutputFormatException
  OutOfRangeException
    SizeOfRangeException
    AreaOutOfRangeException
    ZoomOutOfRangeException

"""

import cairo, math, random, os, sys
import shapes


# Helper

def draw_stripes(context, x, y, w, h, weight, c1, c2):
    '''Rendert einen gestreiften Hintergrund'''
    # Compute start color
    if math.floor(float(x) / weight) % 2:
        (c1, c2) = (c2, c1) #swap
    # offset is the absolute x position of the first section
    offset = - (x % weight )
    while offset < w:
        (c1, c2) = (c2, c1) #swap
        context.set_source_rgba(c1[0], c1[1], c1[2], c1[3])
        context.rectangle(x+offset,y,weight,h)
        context.fill()
        offset += weight

# Not used anymore but helpful
def intcolor(i, reverse = False):
    """Splits a 32 bit integer into 4x8bit and represents them as floats between 0.0 and 1.0
       This can be used to split an 32bit color code into its RGBA values
       From low to high: red, green, blue, alpha """
    r = float( i         % 256) / 255
    g = float((i >> 8  ) % 256) / 255
    b = float((i >> 16 ) % 256) / 255
    a = float((i >> 24 )      ) / 255
    if reverse:
        return (a,b,g,r)
    else:
        return (r,g,b,a)

def hexcolor(h):
    '''Converts an #rgb, #rgba, #rrggbb or #rrggbbaa hex code to a quatuple (red,green,blue,alpha) of floats between 0.0 and 1.0'''
    h = h.strip()
    h = h.lstrip('#')
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2 + 'ff'
    elif len(h) == 4:
        h = h[0]*2 + h[1]*2 + h[2]*2 + h[3]*2
    elif len(h) == 6:
        h = h + 'ff'
    elif len(h) == 8:
        pass
    else:
        raise AttributeError, "This is not a valid hex color code: %s" % h
    i = int(h,16)
    return intcolor(i, reverse=True)
