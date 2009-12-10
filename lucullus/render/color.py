#!/usr/bin/env python
# encoding: utf-8

    
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

def pick(color, strict=False):
    ''' Picks a color '''
    if color in names:
        return names[color]
    elif not strict:
        for cn in names.iterkeys():
            if cn.endswith('.' + color):
                return names[cn]
    if color.startswith('#'):
        return hexcolor(color)
    if isinstance(color, int):
        return intcolor(color)
    if len(color) == 3:
        return map(float, iter(color)) + [1.0]
    if len(color) == 4:
        return map(float, iter(color))

# Color namespaces
names = dict()

# 16 basic colors defined by w3c
names['aqua'] = hexcolor('#00ffff')
names['black'] = hexcolor('#000000')
names['blue'] = hexcolor('#0000ff')
names['fuchsia'] = hexcolor('#ff00ff')
names['gray'] = hexcolor('#808080')
names['green'] = hexcolor('#008000')
names['lime'] = hexcolor('#00ff00')
names['maroon'] = hexcolor('#800000')
names['navy'] = hexcolor('#000080')
names['olive'] = hexcolor('#808000')
names['purple'] = hexcolor('#800080')
names['red'] = hexcolor('#ff0000')
names['silver'] = hexcolor('#c0c0c0')
names['teal'] = hexcolor('#008080')
names['white'] = hexcolor('#ffffff')
names['yellow'] = hexcolor('#ffff00')

# Additional (non standard) css colors
names['css.aliceblue'] = hexcolor('#f0f8ff')
names['css.antiquewhite'] = hexcolor('#faebd7')
names['css.aqua'] = hexcolor('#00ffff')
names['css.aquamarine'] = hexcolor('#7fffd4')
names['css.azure'] = hexcolor('#f0ffff')
names['css.beige'] = hexcolor('#f5f5dc')
names['css.bisque'] = hexcolor('#ffe4c4')
names['css.black'] = hexcolor('#000000')
names['css.blanchedalmond'] = hexcolor('#ffebcd')
names['css.blue'] = hexcolor('#0000ff')
names['css.blueviolet'] = hexcolor('#8a2be2')
names['css.brown'] = hexcolor('#a52a2a')
names['css.burlywood'] = hexcolor('#deb887')
names['css.cadetblue'] = hexcolor('#5f9ea0')
names['css.chartreuse'] = hexcolor('#7fff00')
names['css.chocolate'] = hexcolor('#d2691e')
names['css.coral'] = hexcolor('#ff7f50')
names['css.cornflowerblue'] = hexcolor('#6495ed')
names['css.cornsilk'] = hexcolor('#fff8dc')
names['css.crimson'] = hexcolor('#dc143c')
names['css.cyan'] = hexcolor('#00ffff')
names['css.darkblue'] = hexcolor('#00008b')
names['css.darkcyan'] = hexcolor('#008b8b')
names['css.darkgoldenrod'] = hexcolor('#b8860b')
names['css.darkgray'] = hexcolor('#a9a9a9')
names['css.darkgreen'] = hexcolor('#006400')
names['css.darkkhaki'] = hexcolor('#bdb76b')
names['css.darkmagenta'] = hexcolor('#8b008b')
names['css.darkolivegreen'] = hexcolor('#556b2f')
names['css.darkorange'] = hexcolor('#ff8c00')
names['css.darkorchid'] = hexcolor('#9932cc')
names['css.darkred'] = hexcolor('#8b0000')
names['css.darksalmon'] = hexcolor('#e9967a')
names['css.darkseagreen'] = hexcolor('#8fbc8f')
names['css.darkslateblue'] = hexcolor('#483d8b')
names['css.darkslategray'] = hexcolor('#2f4f4f')
names['css.darkturquoise'] = hexcolor('#00ced1')
names['css.darkviolet'] = hexcolor('#9400d3')
names['css.deeppink'] = hexcolor('#ff1493')
names['css.deepskyblue'] = hexcolor('#00bfff')
names['css.dimgray'] = hexcolor('#696969')
names['css.dodgerblue'] = hexcolor('#1e90ff')
names['css.firebrick'] = hexcolor('#b22222')
names['css.floralwhite'] = hexcolor('#fffaf0')
names['css.forestgreen'] = hexcolor('#228b22')
names['css.fuchsia'] = hexcolor('#ff00ff')
names['css.gainsboro'] = hexcolor('#dcdcdc')
names['css.ghostwhite'] = hexcolor('#f8f8ff')
names['css.gold'] = hexcolor('#ffd700')
names['css.goldenrod'] = hexcolor('#daa520')
names['css.gray'] = hexcolor('#808080')
names['css.green'] = hexcolor('#008000')
names['css.greenyellow'] = hexcolor('#adff2f')
names['css.honeydew'] = hexcolor('#f0fff0')
names['css.hotpink'] = hexcolor('#ff69b4')
names['css.indianred'] = hexcolor('#cd5c5c')
names['css.indigo'] = hexcolor('#4b0082')
names['css.ivory'] = hexcolor('#fffff0')
names['css.khaki'] = hexcolor('#f0e68c')
names['css.lavender'] = hexcolor('#e6e6fa')
names['css.lavenderblush'] = hexcolor('#fff0f5')
names['css.lawngreen'] = hexcolor('#7cfc00')
names['css.lemonchiffon'] = hexcolor('#fffacd')
names['css.lightblue'] = hexcolor('#add8e6')
names['css.lightcoral'] = hexcolor('#f08080')
names['css.lightcyan'] = hexcolor('#e0ffff')
names['css.lightgoldenrodyellow'] = hexcolor('#fafad2')
names['css.lightgrey'] = hexcolor('#d3d3d3')
names['css.lightgreen'] = hexcolor('#90ee90')
names['css.lightpink'] = hexcolor('#ffb6c1')
names['css.lightsalmon'] = hexcolor('#ffa07a')
names['css.lightseagreen'] = hexcolor('#20b2aa')
names['css.lightskyblue'] = hexcolor('#87cefa')
names['css.lightslategray'] = hexcolor('#778899')
names['css.lightsteelblue'] = hexcolor('#b0c4de')
names['css.lightyellow'] = hexcolor('#ffffe0')
names['css.lime'] = hexcolor('#00ff00')
names['css.limegreen'] = hexcolor('#32cd32')
names['css.linen'] = hexcolor('#faf0e6')
names['css.magenta'] = hexcolor('#ff00ff')
names['css.maroon'] = hexcolor('#800000')
names['css.mediumaquamarine'] = hexcolor('#66cdaa')
names['css.mediumblue'] = hexcolor('#0000cd')
names['css.mediumorchid'] = hexcolor('#ba55d3')
names['css.mediumpurple'] = hexcolor('#9370d8')
names['css.mediumseagreen'] = hexcolor('#3cb371')
names['css.mediumslateblue'] = hexcolor('#7b68ee')
names['css.mediumspringgreen'] = hexcolor('#00fa9a')
names['css.mediumturquoise'] = hexcolor('#48d1cc')
names['css.mediumvioletred'] = hexcolor('#c71585')
names['css.midnightblue'] = hexcolor('#191970')
names['css.mintcream'] = hexcolor('#f5fffa')
names['css.mistyrose'] = hexcolor('#ffe4e1')
names['css.moccasin'] = hexcolor('#ffe4b5')
names['css.navajowhite'] = hexcolor('#ffdead')
names['css.navy'] = hexcolor('#000080')
names['css.oldlace'] = hexcolor('#fdf5e6')
names['css.olive'] = hexcolor('#808000')
names['css.olivedrab'] = hexcolor('#6b8e23')
names['css.orange'] = hexcolor('#ffa500')
names['css.orangered'] = hexcolor('#ff4500')
names['css.orchid'] = hexcolor('#da70d6')
names['css.palegoldenrod'] = hexcolor('#eee8aa')
names['css.palegreen'] = hexcolor('#98fb98')
names['css.paleturquoise'] = hexcolor('#afeeee')
names['css.palevioletred'] = hexcolor('#d87093')
names['css.papayawhip'] = hexcolor('#ffefd5')
names['css.peachpuff'] = hexcolor('#ffdab9')
names['css.peru'] = hexcolor('#cd853f')
names['css.pink'] = hexcolor('#ffc0cb')
names['css.plum'] = hexcolor('#dda0dd')
names['css.powderblue'] = hexcolor('#b0e0e6')
names['css.purple'] = hexcolor('#800080')
names['css.red'] = hexcolor('#ff0000')
names['css.rosybrown'] = hexcolor('#bc8f8f')
names['css.royalblue'] = hexcolor('#4169e1')
names['css.saddlebrown'] = hexcolor('#8b4513')
names['css.salmon'] = hexcolor('#fa8072')
names['css.sandybrown'] = hexcolor('#f4a460')
names['css.seagreen'] = hexcolor('#2e8b57')
names['css.seashell'] = hexcolor('#fff5ee')
names['css.sienna'] = hexcolor('#a0522d')
names['css.silver'] = hexcolor('#c0c0c0')
names['css.skyblue'] = hexcolor('#87ceeb')
names['css.slateblue'] = hexcolor('#6a5acd')
names['css.slategray'] = hexcolor('#708090')
names['css.snow'] = hexcolor('#fffafa')
names['css.springgreen'] = hexcolor('#00ff7f')
names['css.steelblue'] = hexcolor('#4682b4')
names['css.tan'] = hexcolor('#d2b48c')
names['css.teal'] = hexcolor('#008080')
names['css.thistle'] = hexcolor('#d8bfd8')
names['css.tomato'] = hexcolor('#ff6347')
names['css.turquoise'] = hexcolor('#40e0d0')
names['css.violet'] = hexcolor('#ee82ee')
names['css.wheat'] = hexcolor('#f5deb3')
names['css.white'] = hexcolor('#ffffff')
names['css.whitesmoke'] = hexcolor('#f5f5f5')
names['css.yellow'] = hexcolor('#ffff00')
names['css.yellowgreen'] = hexcolor('#9acd32')

# Colors defined by BioSeq
names['bio.amino-*'] = hexcolor('#000000')
names['bio.amino--'] = hexcolor('#999999')
names['bio.amino-A'] = hexcolor('#008000')
names['bio.amino-C'] = hexcolor('#a20000')
names['bio.amino-E'] = hexcolor('#ff0000')
names['bio.amino-D'] = hexcolor('#ff0000')
names['bio.amino-G'] = hexcolor('#ff00ff')
names['bio.amino-F'] = hexcolor('#008000')
names['bio.amino-I'] = hexcolor('#008000')
names['bio.amino-H'] = hexcolor('#0080ff')
names['bio.amino-K'] = hexcolor('#0000d9')
names['bio.amino-M'] = hexcolor('#008000')
names['bio.amino-L'] = hexcolor('#008000')
names['bio.amino-N'] = hexcolor('#8080c0')
names['bio.amino-Q'] = hexcolor('#7171b9')
names['bio.amino-P'] = hexcolor('#d9d900')
names['bio.amino-S'] = hexcolor('#ff8000')
names['bio.amino-R'] = hexcolor('#0000ff')
names['bio.amino-T'] = hexcolor('#ff8000')
names['bio.amino-W'] = hexcolor('#00ff00')
names['bio.amino-V'] = hexcolor('#008000')
names['bio.amino-Y'] = hexcolor('#008000')
names['bio.amino-X'] = hexcolor('#000000')
names['bio.amino-section2'] = hexcolor('#eeeeee')
names['bio.amino-section1'] = hexcolor('#ffffff')