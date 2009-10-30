#!/usr/bin/env python
# encoding: utf-8
"""
color.py

Created by marcel Hellkamp on 2009-10-30.
Copyright (c) 2009 MPI PBC Goettingen. All rights reserved.
"""

def add_space(name, colors):
    if name not in space:
        spaces[name] = colors


def add_color(space, name, r, g, b, a=1.0):
    spaces.setdefault(space, dict())[name] = (r, g, b, a)


def get(space, name, default=KeyError):
    try:
        return spaces[space][name.lower()]
    except KeyError:
        if default == KeyError: raise
        return default


def guess(name, default=KeyError):
    ''' Returns a color searching in all known color spaces. '''
    for s in space:
        if name in spaces[s]:
            return spaces[s][name]
    if default == KeyError:
        raise KeyError("Unknown color name '%s'" % name)
    return default

    
def intcolor(i, reverse = False):
    """ Splits a 32 bit integer into RGBA color values using 8 bit for each
        color, lowest bit first. """
    r = float( i         % 256) / 255
    g = float((i >> 8  ) % 256) / 255
    b = float((i >> 16 ) % 256) / 255
    a = float((i >> 24 )      ) / 255
    if reverse:
        return (a,b,g,r)
    else:
        return (r,g,b,a)


def hexcolor(h):
    ''' Converts an #rgb, #rgba, #rrggbb or #rrggbbaa hex code to a quatuple
        (red, green, blue, alpha) of floats between 0.0 and 1.0 '''
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2 + 'ff'
    elif len(h) == 4:
        h = h[0]*2 + h[1]*2 + h[2]*2 + h[3]*2
    elif len(h) == 6:
        h = h + 'ff'
    elif len(h) == 8:
        pass
    return intcolor(int(h,16), reverse=True)


# Color namespaces
spaces = dict()

# 16 basic colors defined by w3c
spaces['basic'] = dict()
spaces['basic']['aqua'] = hexcolor('#00ffff')
spaces['basic']['black'] = hexcolor('#000000')
spaces['basic']['blue'] = hexcolor('#0000ff')
spaces['basic']['fuchsia'] = hexcolor('#ff00ff')
spaces['basic']['gray'] = hexcolor('#808080')
spaces['basic']['green'] = hexcolor('#008000')
spaces['basic']['lime'] = hexcolor('#00ff00')
spaces['basic']['maroon'] = hexcolor('#800000')
spaces['basic']['navy'] = hexcolor('#000080')
spaces['basic']['olive'] = hexcolor('#808000')
spaces['basic']['purple'] = hexcolor('#800080')
spaces['basic']['red'] = hexcolor('#ff0000')
spaces['basic']['silver'] = hexcolor('#c0c0c0')
spaces['basic']['teal'] = hexcolor('#008080')
spaces['basic']['white'] = hexcolor('#ffffff')
spaces['basic']['yellow'] = hexcolor('#ffff00')

# Additional (non standard) css colors
spaces['css'] = dict()
spaces['css']['aliceblue'] = hexcolor('#f0f8ff')
spaces['css']['antiquewhite'] = hexcolor('#faebd7')
spaces['css']['aqua'] = hexcolor('#00ffff')
spaces['css']['aquamarine'] = hexcolor('#7fffd4')
spaces['css']['azure'] = hexcolor('#f0ffff')
spaces['css']['beige'] = hexcolor('#f5f5dc')
spaces['css']['bisque'] = hexcolor('#ffe4c4')
spaces['css']['black'] = hexcolor('#000000')
spaces['css']['blanchedalmond'] = hexcolor('#ffebcd')
spaces['css']['blue'] = hexcolor('#0000ff')
spaces['css']['blueviolet'] = hexcolor('#8a2be2')
spaces['css']['brown'] = hexcolor('#a52a2a')
spaces['css']['burlywood'] = hexcolor('#deb887')
spaces['css']['cadetblue'] = hexcolor('#5f9ea0')
spaces['css']['chartreuse'] = hexcolor('#7fff00')
spaces['css']['chocolate'] = hexcolor('#d2691e')
spaces['css']['coral'] = hexcolor('#ff7f50')
spaces['css']['cornflowerblue'] = hexcolor('#6495ed')
spaces['css']['cornsilk'] = hexcolor('#fff8dc')
spaces['css']['crimson'] = hexcolor('#dc143c')
spaces['css']['cyan'] = hexcolor('#00ffff')
spaces['css']['darkblue'] = hexcolor('#00008b')
spaces['css']['darkcyan'] = hexcolor('#008b8b')
spaces['css']['darkgoldenrod'] = hexcolor('#b8860b')
spaces['css']['darkgray'] = hexcolor('#a9a9a9')
spaces['css']['darkgreen'] = hexcolor('#006400')
spaces['css']['darkkhaki'] = hexcolor('#bdb76b')
spaces['css']['darkmagenta'] = hexcolor('#8b008b')
spaces['css']['darkolivegreen'] = hexcolor('#556b2f')
spaces['css']['darkorange'] = hexcolor('#ff8c00')
spaces['css']['darkorchid'] = hexcolor('#9932cc')
spaces['css']['darkred'] = hexcolor('#8b0000')
spaces['css']['darksalmon'] = hexcolor('#e9967a')
spaces['css']['darkseagreen'] = hexcolor('#8fbc8f')
spaces['css']['darkslateblue'] = hexcolor('#483d8b')
spaces['css']['darkslategray'] = hexcolor('#2f4f4f')
spaces['css']['darkturquoise'] = hexcolor('#00ced1')
spaces['css']['darkviolet'] = hexcolor('#9400d3')
spaces['css']['deeppink'] = hexcolor('#ff1493')
spaces['css']['deepskyblue'] = hexcolor('#00bfff')
spaces['css']['dimgray'] = hexcolor('#696969')
spaces['css']['dodgerblue'] = hexcolor('#1e90ff')
spaces['css']['firebrick'] = hexcolor('#b22222')
spaces['css']['floralwhite'] = hexcolor('#fffaf0')
spaces['css']['forestgreen'] = hexcolor('#228b22')
spaces['css']['fuchsia'] = hexcolor('#ff00ff')
spaces['css']['gainsboro'] = hexcolor('#dcdcdc')
spaces['css']['ghostwhite'] = hexcolor('#f8f8ff')
spaces['css']['gold'] = hexcolor('#ffd700')
spaces['css']['goldenrod'] = hexcolor('#daa520')
spaces['css']['gray'] = hexcolor('#808080')
spaces['css']['green'] = hexcolor('#008000')
spaces['css']['greenyellow'] = hexcolor('#adff2f')
spaces['css']['honeydew'] = hexcolor('#f0fff0')
spaces['css']['hotpink'] = hexcolor('#ff69b4')
spaces['css']['indianred'] = hexcolor('#cd5c5c')
spaces['css']['indigo'] = hexcolor('#4b0082')
spaces['css']['ivory'] = hexcolor('#fffff0')
spaces['css']['khaki'] = hexcolor('#f0e68c')
spaces['css']['lavender'] = hexcolor('#e6e6fa')
spaces['css']['lavenderblush'] = hexcolor('#fff0f5')
spaces['css']['lawngreen'] = hexcolor('#7cfc00')
spaces['css']['lemonchiffon'] = hexcolor('#fffacd')
spaces['css']['lightblue'] = hexcolor('#add8e6')
spaces['css']['lightcoral'] = hexcolor('#f08080')
spaces['css']['lightcyan'] = hexcolor('#e0ffff')
spaces['css']['lightgoldenrodyellow'] = hexcolor('#fafad2')
spaces['css']['lightgrey'] = hexcolor('#d3d3d3')
spaces['css']['lightgreen'] = hexcolor('#90ee90')
spaces['css']['lightpink'] = hexcolor('#ffb6c1')
spaces['css']['lightsalmon'] = hexcolor('#ffa07a')
spaces['css']['lightseagreen'] = hexcolor('#20b2aa')
spaces['css']['lightskyblue'] = hexcolor('#87cefa')
spaces['css']['lightslategray'] = hexcolor('#778899')
spaces['css']['lightsteelblue'] = hexcolor('#b0c4de')
spaces['css']['lightyellow'] = hexcolor('#ffffe0')
spaces['css']['lime'] = hexcolor('#00ff00')
spaces['css']['limegreen'] = hexcolor('#32cd32')
spaces['css']['linen'] = hexcolor('#faf0e6')
spaces['css']['magenta'] = hexcolor('#ff00ff')
spaces['css']['maroon'] = hexcolor('#800000')
spaces['css']['mediumaquamarine'] = hexcolor('#66cdaa')
spaces['css']['mediumblue'] = hexcolor('#0000cd')
spaces['css']['mediumorchid'] = hexcolor('#ba55d3')
spaces['css']['mediumpurple'] = hexcolor('#9370d8')
spaces['css']['mediumseagreen'] = hexcolor('#3cb371')
spaces['css']['mediumslateblue'] = hexcolor('#7b68ee')
spaces['css']['mediumspringgreen'] = hexcolor('#00fa9a')
spaces['css']['mediumturquoise'] = hexcolor('#48d1cc')
spaces['css']['mediumvioletred'] = hexcolor('#c71585')
spaces['css']['midnightblue'] = hexcolor('#191970')
spaces['css']['mintcream'] = hexcolor('#f5fffa')
spaces['css']['mistyrose'] = hexcolor('#ffe4e1')
spaces['css']['moccasin'] = hexcolor('#ffe4b5')
spaces['css']['navajowhite'] = hexcolor('#ffdead')
spaces['css']['navy'] = hexcolor('#000080')
spaces['css']['oldlace'] = hexcolor('#fdf5e6')
spaces['css']['olive'] = hexcolor('#808000')
spaces['css']['olivedrab'] = hexcolor('#6b8e23')
spaces['css']['orange'] = hexcolor('#ffa500')
spaces['css']['orangered'] = hexcolor('#ff4500')
spaces['css']['orchid'] = hexcolor('#da70d6')
spaces['css']['palegoldenrod'] = hexcolor('#eee8aa')
spaces['css']['palegreen'] = hexcolor('#98fb98')
spaces['css']['paleturquoise'] = hexcolor('#afeeee')
spaces['css']['palevioletred'] = hexcolor('#d87093')
spaces['css']['papayawhip'] = hexcolor('#ffefd5')
spaces['css']['peachpuff'] = hexcolor('#ffdab9')
spaces['css']['peru'] = hexcolor('#cd853f')
spaces['css']['pink'] = hexcolor('#ffc0cb')
spaces['css']['plum'] = hexcolor('#dda0dd')
spaces['css']['powderblue'] = hexcolor('#b0e0e6')
spaces['css']['purple'] = hexcolor('#800080')
spaces['css']['red'] = hexcolor('#ff0000')
spaces['css']['rosybrown'] = hexcolor('#bc8f8f')
spaces['css']['royalblue'] = hexcolor('#4169e1')
spaces['css']['saddlebrown'] = hexcolor('#8b4513')
spaces['css']['salmon'] = hexcolor('#fa8072')
spaces['css']['sandybrown'] = hexcolor('#f4a460')
spaces['css']['seagreen'] = hexcolor('#2e8b57')
spaces['css']['seashell'] = hexcolor('#fff5ee')
spaces['css']['sienna'] = hexcolor('#a0522d')
spaces['css']['silver'] = hexcolor('#c0c0c0')
spaces['css']['skyblue'] = hexcolor('#87ceeb')
spaces['css']['slateblue'] = hexcolor('#6a5acd')
spaces['css']['slategray'] = hexcolor('#708090')
spaces['css']['snow'] = hexcolor('#fffafa')
spaces['css']['springgreen'] = hexcolor('#00ff7f')
spaces['css']['steelblue'] = hexcolor('#4682b4')
spaces['css']['tan'] = hexcolor('#d2b48c')
spaces['css']['teal'] = hexcolor('#008080')
spaces['css']['thistle'] = hexcolor('#d8bfd8')
spaces['css']['tomato'] = hexcolor('#ff6347')
spaces['css']['turquoise'] = hexcolor('#40e0d0')
spaces['css']['violet'] = hexcolor('#ee82ee')
spaces['css']['wheat'] = hexcolor('#f5deb3')
spaces['css']['white'] = hexcolor('#ffffff')
spaces['css']['whitesmoke'] = hexcolor('#f5f5f5')
spaces['css']['yellow'] = hexcolor('#ffff00')
spaces['css']['yellowgreen'] = hexcolor('#9acd32')

# Colors defined by BioSeq
spaces['bio'] = dict()
spaces['bio']['amino-*'] = hexcolor('#000000')
spaces['bio']['amino--'] = hexcolor('#999999')
spaces['bio']['amino-a'] = hexcolor('#008000')
spaces['bio']['amino-c'] = hexcolor('#a20000')
spaces['bio']['amino-e'] = hexcolor('#ff0000')
spaces['bio']['amino-d'] = hexcolor('#ff0000')
spaces['bio']['amino-g'] = hexcolor('#ff00ff')
spaces['bio']['amino-f'] = hexcolor('#008000')
spaces['bio']['amino-i'] = hexcolor('#008000')
spaces['bio']['amino-h'] = hexcolor('#0080ff')
spaces['bio']['amino-k'] = hexcolor('#0000d9')
spaces['bio']['amino-m'] = hexcolor('#008000')
spaces['bio']['amino-l'] = hexcolor('#008000')
spaces['bio']['amino-n'] = hexcolor('#8080c0')
spaces['bio']['amino-q'] = hexcolor('#7171b9')
spaces['bio']['amino-p'] = hexcolor('#d9d900')
spaces['bio']['amino-s'] = hexcolor('#ff8000')
spaces['bio']['amino-r'] = hexcolor('#0000ff')
spaces['bio']['amino-t'] = hexcolor('#ff8000')
spaces['bio']['amino-w'] = hexcolor('#00ff00')
spaces['bio']['amino-v'] = hexcolor('#008000')
spaces['bio']['amino-y'] = hexcolor('#008000')
spaces['bio']['amino-x'] = hexcolor('#000000')
spaces['bio']['amino-section2'] = hexcolor('#eeeeee')
spaces['bio']['amino-section1'] = hexcolor('#ffffff')