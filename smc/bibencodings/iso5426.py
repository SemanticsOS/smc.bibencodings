# -*- coding: utf-8 -*-
#=============================================================================
# Copyright   : (c)2010-2012 semantics GmbH
# Rep./File   : $URL$
# Date        : $Date$
# Author      : Christian Heimes
# License     : BSD LICENSE
# Worker      : $Author$
# Revision    : $Rev$
# Purpose     : ISO-5426 encoding
#=============================================================================
"""ISO-5426 / MAB2 codec
"""
from __future__ import unicode_literals, print_function
import codecs
from smc.bibencodings.utils import DecodeIterator


def encode(input, errors='strict'):
    """Encode unicode as ISO-5426
    """
    if errors not in set(['strict', 'replace', 'ignore']):
        raise ValueError("Invalid errors argument %s" % errors)
    result = []
    rappend = result.append
    uget = unicodemap.get
    for u in input:
        s = uget(u)
        if s is None:
            if errors == 'strict':
                raise UnicodeError(repr(u))
            elif errors == "replace":
                s = b'?'
            elif errors == "ignore":
                s = b''
            else: # pragma: no cover
                # should never be reached
                raise ValueError("Invalid errors argument %s" % errors)
        # special case combining char, move it in front of the last char
        if len(s) == 1 and 0xc0 <= ord(s) <= 0xdf:
            result.insert(-1, s)
        else:
            rappend(s)
    return b"".join(result), len(input)


def decode(input, errors='strict', special=None):
    """Decode unicode from ISO-5426
    """
    if errors not in set(['strict', 'replace', 'ignore', 'repr']):
        raise ValueError("Invalid errors argument %s" % errors)

    result = []
    di = DecodeIterator(input)
    # optimizations
    rappend = result.append
    cget = charmap.get

    for c in di:
        o = ord(c)
        # ASCII chars
        if c < b'\x7f':
            rappend(chr(o))
            #i += 1
            continue

        c1, c2 = di.peek(2)
        ccc2 = None
        # 0xc0 to 0xdf signals a combined char
        if 0xc0 <= o <= 0xdf and c1 is not None:
            # special case 0xc9: both 0xc9 and 0xc9 are combining diaeresis
            # use 0xc8 in favor of 0xc9
            if c == b'\xc9':
                c = b'\xc8'
            if c1 == b'\xc9':
                c1 = b'\xc8'
            # double combined char
            if 0xc0 <= ord(c1) <= 0xdf and c2 is not None:
                ccc2 = c + c1 + c2
                r = cget(ccc2)
                if r is not None:
                    # double combined found in table
                    rappend(r)
                    di.evolve(2)
                    continue
                # build combining unicode
                dc1 = cget(c)
                dc2 = cget(c1 + c2)
                if dc1 is not None and dc2 is not None: # pragma: no branch
                    # reverse order, in unicode, the combining char comes after the char
                    rappend(dc2 + dc1)
                    di.evolve(2)
                    continue
            else:
                cc1 = c + c1
                r = cget(cc1)
                if r is not None:
                    rappend(r)
                    di.evolve(1)
                    continue
                # denormalized unicode: char + combining
                r = cget(c)
                rn = cget(c1)
                if r is not None and rn is not None: # pragma: no branch
                    rappend(rn + r)
                    di.evolve(1)
                    continue

            # just the combining
            #r = cget(c)
            #if r is not None:
            #    result.append(r)
            #    continue

        # other chars, 0x80 <= o <= 0xbf or o >= 0xe0 or last combining
        if special is not None:
            r = special.get(c)
            if r is not None:
                rappend(r)
                continue

        r = cget(c)
        if r is not None:
            rappend(r)
            continue

        # only reached when no result was found
        if errors == "strict":
            p = di.position
            raise UnicodeError("Can't decode byte%s %r at position %i (context %r)" %
                               ("" if ccc2 is None else "s",
                                c if ccc2 is None else ccc2,
                                p, input[p - 3:p + 3]))
        elif errors == "replace":
            rappend('\ufffd')
        elif errors == "ignore":
            pass
        elif errors == "repr":
            rappend('\\x%x' % o)
        else: # pragma: no cover
            # should never be reached
            raise ValueError("Invalid errors argument %s" % errors)

    return "".join(result), di.position


### Codec APIs
class Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return encode(input, errors)

    def decode(self, input, errors='strict'):
        return decode(input, errors)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


### encodings module API
codecInfo = codecs.CodecInfo(
    name='iso-5426',
    encode=Codec().encode,
    decode=Codec().decode,
    streamreader=StreamReader,
    streamwriter=StreamWriter)


### Codec APIs
class SpecialXE0Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return encode(input, errors)

    def decode(self, input, errors='strict'):
        return decode(input, errors, special_xe0_map)


class SpecialXE0StreamWriter(SpecialXE0Codec, codecs.StreamWriter):
    pass


class SpecialXE0StreamReader(SpecialXE0Codec, codecs.StreamReader):
    pass


### encodings module API
specialXE0CodecInfo = codecs.CodecInfo(
    name='iso-5426-xe0',
    encode=SpecialXE0Codec().encode,
    decode=SpecialXE0Codec().decode,
    streamreader=SpecialXE0StreamReader,
    streamwriter=SpecialXE0StreamWriter)

# special identity mapping for 0xa4, 0xe0-0xff
special_xe0_map = {
    b'\xa4': '\xa4',
    b'\xe0': '\xe0',
    b'\xe1': '\xe1',
    b'\xe2': '\xe2',
    b'\xe3': '\xe3',
    b'\xe4': '\xe4',
    b'\xe5': '\xe5',
    b'\xe6': '\xe6',
    b'\xe7': '\xe7',
    b'\xe8': '\xe8',
    b'\xe9': '\xe9',
    b'\xea': '\xea',
    b'\xeb': '\xeb',
    b'\xec': '\xec',
    b'\xed': '\xed',
    b'\xee': '\xee',
    b'\xef': '\xef',
    b'\xf0': '\xf0',
    b'\xf1': '\xf1',
    b'\xf2': '\xf2',
    b'\xf3': '\xf3',
    b'\xf4': '\xf4',
    b'\xf5': '\xf5',
    b'\xf6': '\xf6',
    b'\xf7': '\xf7',
    b'\xf8': '\xf8',
    b'\xf9': '\xf9',
    b'\xfa': '\xfa',
    b'\xfb': '\xfb',
    b'\xfc': '\xfc',
    b'\xfd': '\xfd',
    b'\xfe': '\xfe',
    b'\xff': '\xff'}


unicodemap = {
    '\u001d': b'\x1d', # <control>
    '\u001e': b'\x1e', # <control>
    '\u001f': b'\x1f', # <control>
    '\u0020': b' ', # SPACE
    '\u0021': b'!', # EXCLAMATION MARK
    '\u0022': b'"', # QUOTATION MARK
    '\u0023': b'#', # NUMBER SIGN
    '\u0024': b'\xa4', # DOLLAR SIGN
    '\u0025': b'%', # PERCENT SIGN
    '\u0026': b'&', # AMPERSAND
    '\u0027': b"'", # APOSTROPHE
    '\u0028': b'(', # LEFT PARENTHESIS
    '\u0029': b')', # RIGHT PARENTHESIS
    '\u002a': b'*', # ASTERISK
    '\u002b': b'+', # PLUS SIGN
    '\u002c': b',', # COMMA
    '\u002d': b'-', # HYPHEN-MINUS
    '\u002e': b'.', # FULL STOP
    '\u002f': b'/', # SOLIDUS
    '\u0030': b'0', # DIGIT ZERO
    '\u0031': b'1', # DIGIT ONE
    '\u0032': b'2', # DIGIT TWO
    '\u0033': b'3', # DIGIT THREE
    '\u0034': b'4', # DIGIT FOUR
    '\u0035': b'5', # DIGIT FIVE
    '\u0036': b'6', # DIGIT SIX
    '\u0037': b'7', # DIGIT SEVEN
    '\u0038': b'8', # DIGIT EIGHT
    '\u0039': b'9', # DIGIT NINE
    '\u003a': b':', # COLON
    '\u003b': b';', # SEMICOLON
    '\u003c': b'<', # LESS-THAN SIGN
    '\u003d': b'=', # EQUALS SIGN
    '\u003e': b'>', # GREATER-THAN SIGN
    '\u003f': b'?', # QUESTION MARK
    '\u0040': b'@', # COMMERCIAL AT
    '\u0041': b'A', # LATIN CAPITAL LETTER A
    '\u0042': b'B', # LATIN CAPITAL LETTER B
    '\u0043': b'C', # LATIN CAPITAL LETTER C
    '\u0044': b'D', # LATIN CAPITAL LETTER D
    '\u0045': b'E', # LATIN CAPITAL LETTER E
    '\u0046': b'F', # LATIN CAPITAL LETTER F
    '\u0047': b'G', # LATIN CAPITAL LETTER G
    '\u0048': b'H', # LATIN CAPITAL LETTER H
    '\u0049': b'I', # LATIN CAPITAL LETTER I
    '\u004a': b'J', # LATIN CAPITAL LETTER J
    '\u004b': b'K', # LATIN CAPITAL LETTER K
    '\u004c': b'L', # LATIN CAPITAL LETTER L
    '\u004d': b'M', # LATIN CAPITAL LETTER M
    '\u004e': b'N', # LATIN CAPITAL LETTER N
    '\u004f': b'O', # LATIN CAPITAL LETTER O
    '\u0050': b'P', # LATIN CAPITAL LETTER P
    '\u0051': b'Q', # LATIN CAPITAL LETTER Q
    '\u0052': b'R', # LATIN CAPITAL LETTER R
    '\u0053': b'S', # LATIN CAPITAL LETTER S
    '\u0054': b'T', # LATIN CAPITAL LETTER T
    '\u0055': b'U', # LATIN CAPITAL LETTER U
    '\u0056': b'V', # LATIN CAPITAL LETTER V
    '\u0057': b'W', # LATIN CAPITAL LETTER W
    '\u0058': b'X', # LATIN CAPITAL LETTER X
    '\u0059': b'Y', # LATIN CAPITAL LETTER Y
    '\u005a': b'Z', # LATIN CAPITAL LETTER Z
    '\u005b': b'[', # LEFT SQUARE BRACKET
    '\u005c': b'\\', # REVERSE SOLIDUS
    '\u005d': b']', # RIGHT SQUARE BRACKET
    '\u005e': b'^', # CIRCUMFLEX ACCENT
    '\u005f': b'_', # LOW LINE
    '\u0060': b'`', # GRAVE ACCENT
    '\u0061': b'a', # LATIN SMALL LETTER A
    '\u0062': b'b', # LATIN SMALL LETTER B
    '\u0063': b'c', # LATIN SMALL LETTER C
    '\u0064': b'd', # LATIN SMALL LETTER D
    '\u0065': b'e', # LATIN SMALL LETTER E
    '\u0066': b'f', # LATIN SMALL LETTER F
    '\u0067': b'g', # LATIN SMALL LETTER G
    '\u0068': b'h', # LATIN SMALL LETTER H
    '\u0069': b'i', # LATIN SMALL LETTER I
    '\u006a': b'j', # LATIN SMALL LETTER J
    '\u006b': b'k', # LATIN SMALL LETTER K
    '\u006c': b'l', # LATIN SMALL LETTER L
    '\u006d': b'm', # LATIN SMALL LETTER M
    '\u006e': b'n', # LATIN SMALL LETTER N
    '\u006f': b'o', # LATIN SMALL LETTER O
    '\u0070': b'p', # LATIN SMALL LETTER P
    '\u0071': b'q', # LATIN SMALL LETTER Q
    '\u0072': b'r', # LATIN SMALL LETTER R
    '\u0073': b's', # LATIN SMALL LETTER S
    '\u0074': b't', # LATIN SMALL LETTER T
    '\u0075': b'u', # LATIN SMALL LETTER U
    '\u0076': b'v', # LATIN SMALL LETTER V
    '\u0077': b'w', # LATIN SMALL LETTER W
    '\u0078': b'x', # LATIN SMALL LETTER X
    '\u0079': b'y', # LATIN SMALL LETTER Y
    '\u007a': b'z', # LATIN SMALL LETTER Z
    '\u007b': b'{', # LEFT CURLY BRACKET
    '\u007c': b'|', # VERTICAL LINE
    '\u007d': b'}', # RIGHT CURLY BRACKET
    '\u007e': b'~', # TILDE
    '\u0088': b'\x88', # <control>
    '\u0089': b'\x89', # <control>
    # XXX not part of the standard but MARC equivalent of \x88, \x89
    #'\u0098': b'\x98', # <control>
    #'\u009c': b'\x9c', # <control>
    '\u00a1': b'\xa1', # INVERTED EXCLAMATION MARK
    '\u00a3': b'\xa3', # POUND SIGN
    '\u00a5': b'\xa5', # YEN SIGN
    '\u00a7': b'\xa7', # SECTION SIGN
    '\u00a9': b'\xad', # COPYRIGHT SIGN
    '\u00ab': b'\xab', # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    '\u00ae': b'\xaf', # REGISTERED SIGN
    '\u00b7': b'\xb7', # MIDDLE DOT
    '\u00bb': b'\xbb', # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    '\u00bf': b'\xbf', # INVERTED QUESTION MARK
    '\u00c0': b'\xc1A', # LATIN CAPITAL LETTER A WITH GRAVE
    '\u00c1': b'\xc2A', # LATIN CAPITAL LETTER A WITH ACUTE
    '\u00c2': b'\xc3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    '\u00c3': b'\xc4A', # LATIN CAPITAL LETTER A WITH TILDE
    '\u00c4': b'\xc8A', # LATIN CAPITAL LETTER A WITH DIAERESIS
    '\u00c5': b'\xcaA', # LATIN CAPITAL LETTER A WITH RING ABOVE
    '\u00c6': b'\xe1', # LATIN CAPITAL LETTER AE
    '\u00c7': b'\xd0C', # LATIN CAPITAL LETTER C WITH CEDILLA
    '\u00c8': b'\xc1E', # LATIN CAPITAL LETTER E WITH GRAVE
    '\u00c9': b'\xc2E', # LATIN CAPITAL LETTER E WITH ACUTE
    '\u00ca': b'\xc3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    '\u00cb': b'\xc8E', # LATIN CAPITAL LETTER E WITH DIAERESIS
    '\u00cc': b'\xc1I', # LATIN CAPITAL LETTER I WITH GRAVE
    '\u00cd': b'\xc2I', # LATIN CAPITAL LETTER I WITH ACUTE
    '\u00ce': b'\xc3I', # LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    '\u00cf': b'\xc8I', # LATIN CAPITAL LETTER I WITH DIAERESIS
    '\u00d1': b'\xc4N', # LATIN CAPITAL LETTER N WITH TILDE
    '\u00d2': b'\xc1O', # LATIN CAPITAL LETTER O WITH GRAVE
    '\u00d3': b'\xc2O', # LATIN CAPITAL LETTER O WITH ACUTE
    '\u00d4': b'\xc3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    '\u00d5': b'\xc4O', # LATIN CAPITAL LETTER O WITH TILDE
    '\u00d6': b'\xc8O', # LATIN CAPITAL LETTER O WITH DIAERESIS
    '\u00d8': b'\xe9', # LATIN CAPITAL LETTER O WITH STROKE
    '\u00d9': b'\xc1U', # LATIN CAPITAL LETTER U WITH GRAVE
    '\u00da': b'\xc2U', # LATIN CAPITAL LETTER U WITH ACUTE
    '\u00db': b'\xc3U', # LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    '\u00dc': b'\xc8U', # LATIN CAPITAL LETTER U WITH DIAERESIS
    '\u00dd': b'\xc2Y', # LATIN CAPITAL LETTER Y WITH ACUTE
    '\u00de': b'\xec', # LATIN CAPITAL LETTER THORN
    '\u00df': b'\xfb', # LATIN SMALL LETTER SHARP S
    '\u00e0': b'\xc1a', # LATIN SMALL LETTER A WITH GRAVE
    '\u00e1': b'\xc2a', # LATIN SMALL LETTER A WITH ACUTE
    '\u00e2': b'\xc3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX
    '\u00e3': b'\xc4a', # LATIN SMALL LETTER A WITH TILDE
    '\u00e4': b'\xc8a', # LATIN SMALL LETTER A WITH DIAERESIS
    '\u00e5': b'\xcaa', # LATIN SMALL LETTER A WITH RING ABOVE
    '\u00e6': b'\xf1', # LATIN SMALL LETTER AE
    '\u00e7': b'\xd0c', # LATIN SMALL LETTER C WITH CEDILLA
    '\u00e8': b'\xc1e', # LATIN SMALL LETTER E WITH GRAVE
    '\u00e9': b'\xc2e', # LATIN SMALL LETTER E WITH ACUTE
    '\u00ea': b'\xc3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX
    '\u00eb': b'\xc8e', # LATIN SMALL LETTER E WITH DIAERESIS
    '\u00ec': b'\xc1i', # LATIN SMALL LETTER I WITH GRAVE
    '\u00ed': b'\xc2i', # LATIN SMALL LETTER I WITH ACUTE
    '\u00ee': b'\xc3i', # LATIN SMALL LETTER I WITH CIRCUMFLEX
    '\u00ef': b'\xc8i', # LATIN SMALL LETTER I WITH DIAERESIS
    '\u00f0': b'\xf3', # LATIN SMALL LETTER ETH
    '\u00f1': b'\xc4n', # LATIN SMALL LETTER N WITH TILDE
    '\u00f2': b'\xc1o', # LATIN SMALL LETTER O WITH GRAVE
    '\u00f3': b'\xc2o', # LATIN SMALL LETTER O WITH ACUTE
    '\u00f4': b'\xc3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX
    '\u00f5': b'\xc4o', # LATIN SMALL LETTER O WITH TILDE
    '\u00f6': b'\xc8o', # LATIN SMALL LETTER O WITH DIAERESIS
    '\u00f8': b'\xf9', # LATIN SMALL LETTER O WITH STROKE
    '\u00f9': b'\xc1u', # LATIN SMALL LETTER U WITH GRAVE
    '\u00fa': b'\xc2u', # LATIN SMALL LETTER U WITH ACUTE
    '\u00fb': b'\xc3u', # LATIN SMALL LETTER U WITH CIRCUMFLEX
    '\u00fc': b'\xc8u', # LATIN SMALL LETTER U WITH DIAERESIS
    '\u00fd': b'\xc2y', # LATIN SMALL LETTER Y WITH ACUTE
    '\u00fe': b'\xfc', # LATIN SMALL LETTER THORN
    '\u00ff': b'\xc8y', # LATIN SMALL LETTER Y WITH DIAERESIS
    '\u0100': b'\xc5A', # LATIN CAPITAL LETTER A WITH MACRON
    '\u0101': b'\xc5a', # LATIN SMALL LETTER A WITH MACRON
    '\u0102': b'\xc6A', # LATIN CAPITAL LETTER A WITH BREVE
    '\u0103': b'\xc6a', # LATIN SMALL LETTER A WITH BREVE
    '\u0104': b'\xd3A', # LATIN CAPITAL LETTER A WITH OGONEK
    '\u0105': b'\xd3a', # LATIN SMALL LETTER A WITH OGONEK
    '\u0106': b'\xc2C', # LATIN CAPITAL LETTER C WITH ACUTE
    '\u0107': b'\xc2c', # LATIN SMALL LETTER C WITH ACUTE
    '\u0108': b'\xc3C', # LATIN CAPITAL LETTER C WITH CIRCUMFLEX
    '\u0109': b'\xc3c', # LATIN SMALL LETTER C WITH CIRCUMFLEX
    '\u010a': b'\xc7C', # LATIN CAPITAL LETTER C WITH DOT ABOVE
    '\u010b': b'\xc7c', # LATIN SMALL LETTER C WITH DOT ABOVE
    '\u010c': b'\xcfC', # LATIN CAPITAL LETTER C WITH CARON
    '\u010d': b'\xcfc', # LATIN SMALL LETTER C WITH CARON
    '\u010e': b'\xcfD', # LATIN CAPITAL LETTER D WITH CARON
    '\u010f': b'\xcfd', # LATIN SMALL LETTER D WITH CARON
    '\u0110': b'\xe2', # LATIN CAPITAL LETTER D WITH STROKE
    '\u0111': b'\xf2', # LATIN SMALL LETTER D WITH STROKE
    '\u0112': b'\xc5E', # LATIN CAPITAL LETTER E WITH MACRON
    '\u0113': b'\xc5e', # LATIN SMALL LETTER E WITH MACRON
    '\u0114': b'\xc6E', # LATIN CAPITAL LETTER E WITH BREVE
    '\u0115': b'\xc6e', # LATIN SMALL LETTER E WITH BREVE
    '\u0116': b'\xc7E', # LATIN CAPITAL LETTER E WITH DOT ABOVE
    '\u0117': b'\xc7e', # LATIN SMALL LETTER E WITH DOT ABOVE
    '\u0118': b'\xd3E', # LATIN CAPITAL LETTER E WITH OGONEK
    '\u0119': b'\xd3e', # LATIN SMALL LETTER E WITH OGONEK
    '\u011a': b'\xcfE', # LATIN CAPITAL LETTER E WITH CARON
    '\u011b': b'\xcfe', # LATIN SMALL LETTER E WITH CARON
    '\u011c': b'\xc3G', # LATIN CAPITAL LETTER G WITH CIRCUMFLEX
    '\u011d': b'\xc3g', # LATIN SMALL LETTER G WITH CIRCUMFLEX
    '\u011e': b'\xc6G', # LATIN CAPITAL LETTER G WITH BREVE
    '\u011f': b'\xc6g', # LATIN SMALL LETTER G WITH BREVE
    '\u0120': b'\xc7G', # LATIN CAPITAL LETTER G WITH DOT ABOVE
    '\u0121': b'\xc7g', # LATIN SMALL LETTER G WITH DOT ABOVE
    '\u0122': b'\xd0G', # LATIN CAPITAL LETTER G WITH CEDILLA
    '\u0123': b'\xd0g', # LATIN SMALL LETTER G WITH CEDILLA
    '\u0124': b'\xc3H', # LATIN CAPITAL LETTER H WITH CIRCUMFLEX
    '\u0125': b'\xc3h', # LATIN SMALL LETTER H WITH CIRCUMFLEX
    '\u0128': b'\xc4I', # LATIN CAPITAL LETTER I WITH TILDE
    '\u0129': b'\xc4i', # LATIN SMALL LETTER I WITH TILDE
    '\u012a': b'\xc5I', # LATIN CAPITAL LETTER I WITH MACRON
    '\u012b': b'\xc5i', # LATIN SMALL LETTER I WITH MACRON
    '\u012c': b'\xc6I', # LATIN CAPITAL LETTER I WITH BREVE
    '\u012d': b'\xc6i', # LATIN SMALL LETTER I WITH BREVE
    '\u012e': b'\xd3I', # LATIN CAPITAL LETTER I WITH OGONEK
    '\u012f': b'\xd3i', # LATIN SMALL LETTER I WITH OGONEK
    '\u0130': b'\xc7I', # LATIN CAPITAL LETTER I WITH DOT ABOVE
    '\u0131': b'\xf5', # LATIN SMALL LETTER DOTLESS I
    '\u0132': b'\xe6', # LATIN CAPITAL LIGATURE IJ
    '\u0133': b'\xf6', # LATIN SMALL LIGATURE IJ
    '\u0134': b'\xc3J', # LATIN CAPITAL LETTER J WITH CIRCUMFLEX
    '\u0135': b'\xc3j', # LATIN SMALL LETTER J WITH CIRCUMFLEX
    '\u0136': b'\xd0K', # LATIN CAPITAL LETTER K WITH CEDILLA
    '\u0137': b'\xd0k', # LATIN SMALL LETTER K WITH CEDILLA
    '\u0139': b'\xc2L', # LATIN CAPITAL LETTER L WITH ACUTE
    '\u013a': b'\xc2l', # LATIN SMALL LETTER L WITH ACUTE
    '\u013b': b'\xd0L', # LATIN CAPITAL LETTER L WITH CEDILLA
    '\u013c': b'\xd0l', # LATIN SMALL LETTER L WITH CEDILLA
    '\u013d': b'\xcfL', # LATIN CAPITAL LETTER L WITH CARON
    '\u013e': b'\xcfl', # LATIN SMALL LETTER L WITH CARON
    '\u0141': b'\xe8', # LATIN CAPITAL LETTER L WITH STROKE
    '\u0142': b'\xf8', # LATIN SMALL LETTER L WITH STROKE
    '\u0143': b'\xc2N', # LATIN CAPITAL LETTER N WITH ACUTE
    '\u0144': b'\xc2n', # LATIN SMALL LETTER N WITH ACUTE
    '\u0145': b'\xd0N', # LATIN CAPITAL LETTER N WITH CEDILLA
    '\u0146': b'\xd0n', # LATIN SMALL LETTER N WITH CEDILLA
    '\u0147': b'\xcfN', # LATIN CAPITAL LETTER N WITH CARON
    '\u0148': b'\xcfn', # LATIN SMALL LETTER N WITH CARON
    '\u014c': b'\xc5O', # LATIN CAPITAL LETTER O WITH MACRON
    '\u014d': b'\xc5o', # LATIN SMALL LETTER O WITH MACRON
    '\u014e': b'\xc6O', # LATIN CAPITAL LETTER O WITH BREVE
    '\u014f': b'\xc6o', # LATIN SMALL LETTER O WITH BREVE
    '\u0150': b'\xcdO', # LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
    '\u0151': b'\xcdo', # LATIN SMALL LETTER O WITH DOUBLE ACUTE
    '\u0152': b'\xea', # LATIN CAPITAL LIGATURE OE
    '\u0153': b'\xfa', # LATIN SMALL LIGATURE OE
    '\u0154': b'\xc2R', # LATIN CAPITAL LETTER R WITH ACUTE
    '\u0155': b'\xc2r', # LATIN SMALL LETTER R WITH ACUTE
    '\u0156': b'\xd0R', # LATIN CAPITAL LETTER R WITH CEDILLA
    '\u0157': b'\xd0r', # LATIN SMALL LETTER R WITH CEDILLA
    '\u0158': b'\xcfR', # LATIN CAPITAL LETTER R WITH CARON
    '\u0159': b'\xcfr', # LATIN SMALL LETTER R WITH CARON
    '\u015a': b'\xc2S', # LATIN CAPITAL LETTER S WITH ACUTE
    '\u015b': b'\xc2s', # LATIN SMALL LETTER S WITH ACUTE
    '\u015c': b'\xc3S', # LATIN CAPITAL LETTER S WITH CIRCUMFLEX
    '\u015d': b'\xc3s', # LATIN SMALL LETTER S WITH CIRCUMFLEX
    '\u015e': b'\xd0S', # LATIN CAPITAL LETTER S WITH CEDILLA
    '\u015f': b'\xd0s', # LATIN SMALL LETTER S WITH CEDILLA
    '\u0160': b'\xcfS', # LATIN CAPITAL LETTER S WITH CARON
    '\u0161': b'\xcfs', # LATIN SMALL LETTER S WITH CARON
    '\u0162': b'\xd0T', # LATIN CAPITAL LETTER T WITH CEDILLA
    '\u0163': b'\xd0t', # LATIN SMALL LETTER T WITH CEDILLA
    '\u0164': b'\xcfT', # LATIN CAPITAL LETTER T WITH CARON
    '\u0165': b'\xcft', # LATIN SMALL LETTER T WITH CARON
    '\u0168': b'\xc4U', # LATIN CAPITAL LETTER U WITH TILDE
    '\u0169': b'\xc4u', # LATIN SMALL LETTER U WITH TILDE
    '\u016a': b'\xc5U', # LATIN CAPITAL LETTER U WITH MACRON
    '\u016b': b'\xc5u', # LATIN SMALL LETTER U WITH MACRON
    '\u016c': b'\xc6U', # LATIN CAPITAL LETTER U WITH BREVE
    '\u016d': b'\xc6u', # LATIN SMALL LETTER U WITH BREVE
    '\u016e': b'\xcaU', # LATIN CAPITAL LETTER U WITH RING ABOVE
    '\u016f': b'\xcau', # LATIN SMALL LETTER U WITH RING ABOVE
    '\u0170': b'\xcdU', # LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
    '\u0171': b'\xcdu', # LATIN SMALL LETTER U WITH DOUBLE ACUTE
    '\u0172': b'\xd3U', # LATIN CAPITAL LETTER U WITH OGONEK
    '\u0173': b'\xd3u', # LATIN SMALL LETTER U WITH OGONEK
    '\u0174': b'\xc3W', # LATIN CAPITAL LETTER W WITH CIRCUMFLEX
    '\u0175': b'\xc3w', # LATIN SMALL LETTER W WITH CIRCUMFLEX
    '\u0176': b'\xc3Y', # LATIN CAPITAL LETTER Y WITH CIRCUMFLEX
    '\u0177': b'\xc3y', # LATIN SMALL LETTER Y WITH CIRCUMFLEX
    '\u0178': b'\xc8Y', # LATIN CAPITAL LETTER Y WITH DIAERESIS
    '\u0179': b'\xc2Z', # LATIN CAPITAL LETTER Z WITH ACUTE
    '\u017a': b'\xc2z', # LATIN SMALL LETTER Z WITH ACUTE
    '\u017b': b'\xc7Z', # LATIN CAPITAL LETTER Z WITH DOT ABOVE
    '\u017c': b'\xc7z', # LATIN SMALL LETTER Z WITH DOT ABOVE
    '\u017d': b'\xcfZ', # LATIN CAPITAL LETTER Z WITH CARON
    '\u017e': b'\xcfz', # LATIN SMALL LETTER Z WITH CARON
    '\u01a0': b'\xceO', # LATIN CAPITAL LETTER O WITH HORN
    '\u01a1': b'\xceo', # LATIN SMALL LETTER O WITH HORN
    '\u01af': b'\xceU', # LATIN CAPITAL LETTER U WITH HORN
    '\u01b0': b'\xceu', # LATIN SMALL LETTER U WITH HORN
    '\u01cd': b'\xcfA', # LATIN CAPITAL LETTER A WITH CARON
    '\u01ce': b'\xcfa', # LATIN SMALL LETTER A WITH CARON
    '\u01cf': b'\xcfI', # LATIN CAPITAL LETTER I WITH CARON
    '\u01d0': b'\xcfi', # LATIN SMALL LETTER I WITH CARON
    '\u01d1': b'\xcfO', # LATIN CAPITAL LETTER O WITH CARON
    '\u01d2': b'\xcfo', # LATIN SMALL LETTER O WITH CARON
    '\u01d3': b'\xcfU', # LATIN CAPITAL LETTER U WITH CARON
    '\u01d4': b'\xcfu', # LATIN SMALL LETTER U WITH CARON
    '\u01d5': b'\xc5\xc8U', # LATIN CAPITAL LETTER U WITH DIAERESIS AND MACRON
    '\u01d6': b'\xc5\xc8u', # LATIN SMALL LETTER U WITH DIAERESIS AND MACRON
    '\u01d7': b'\xc2\xc8U', # LATIN CAPITAL LETTER U WITH DIAERESIS AND ACUTE
    '\u01d8': b'\xc2\xc8u', # LATIN SMALL LETTER U WITH DIAERESIS AND ACUTE
    '\u01d9': b'\xcf\xc8U', # LATIN CAPITAL LETTER U WITH DIAERESIS AND CARON
    '\u01da': b'\xcf\xc8u', # LATIN SMALL LETTER U WITH DIAERESIS AND CARON
    '\u01db': b'\xc1\xc8U', # LATIN CAPITAL LETTER U WITH DIAERESIS AND GRAVE
    '\u01dc': b'\xc1\xc8u', # LATIN SMALL LETTER U WITH DIAERESIS AND GRAVE
    '\u01de': b'\xc5\xc8A', # LATIN CAPITAL LETTER A WITH DIAERESIS AND MACRON
    '\u01df': b'\xc5\xc8a', # LATIN SMALL LETTER A WITH DIAERESIS AND MACRON
    '\u01e0': b'\xc5\xc7A', # LATIN CAPITAL LETTER A WITH DOT ABOVE AND MACRON
    '\u01e1': b'\xc5\xc7a', # LATIN SMALL LETTER A WITH DOT ABOVE AND MACRON
    '\u01e2': b'\xc5\xe1', # LATIN CAPITAL LETTER AE WITH MACRON
    '\u01e3': b'\xc5\xf1', # LATIN SMALL LETTER AE WITH MACRON
    '\u01e6': b'\xcfG', # LATIN CAPITAL LETTER G WITH CARON
    '\u01e7': b'\xcfg', # LATIN SMALL LETTER G WITH CARON
    '\u01e8': b'\xcfK', # LATIN CAPITAL LETTER K WITH CARON
    '\u01e9': b'\xcfk', # LATIN SMALL LETTER K WITH CARON
    '\u01ea': b'\xd3O', # LATIN CAPITAL LETTER O WITH OGONEK
    '\u01eb': b'\xd3o', # LATIN SMALL LETTER O WITH OGONEK
    '\u01ec': b'\xc5\xd3O', # LATIN CAPITAL LETTER O WITH OGONEK AND MACRON
    '\u01ed': b'\xc5\xd3o', # LATIN SMALL LETTER O WITH OGONEK AND MACRON
    '\u01f0': b'\xcfj', # LATIN SMALL LETTER J WITH CARON
    '\u01f4': b'\xc2G', # LATIN CAPITAL LETTER G WITH ACUTE
    '\u01f5': b'\xc2g', # LATIN SMALL LETTER G WITH ACUTE
    '\u01f8': b'\xc1N', # LATIN CAPITAL LETTER N WITH GRAVE
    '\u01f9': b'\xc1n', # LATIN SMALL LETTER N WITH GRAVE
    '\u01fa': b'\xc2\xcaA', # LATIN CAPITAL LETTER A WITH RING ABOVE AND ACUTE
    '\u01fb': b'\xc2\xcaa', # LATIN SMALL LETTER A WITH RING ABOVE AND ACUTE
    '\u01fc': b'\xc2\xe1', # LATIN CAPITAL LETTER AE WITH ACUTE
    '\u01fd': b'\xc2\xf1', # LATIN SMALL LETTER AE WITH ACUTE
    '\u01fe': b'\xc2\xe9', # LATIN CAPITAL LETTER O WITH STROKE AND ACUTE
    '\u01ff': b'\xc2\xf9', # LATIN SMALL LETTER O WITH STROKE AND ACUTE
    '\u0218': b'\xd2S', # LATIN CAPITAL LETTER S WITH COMMA BELOW
    '\u0219': b'\xd2s', # LATIN SMALL LETTER S WITH COMMA BELOW
    '\u021a': b'\xd2T', # LATIN CAPITAL LETTER T WITH COMMA BELOW
    '\u021b': b'\xd2t', # LATIN SMALL LETTER T WITH COMMA BELOW
    '\u021e': b'\xcfH', # LATIN CAPITAL LETTER H WITH CARON
    '\u021f': b'\xcfh', # LATIN SMALL LETTER H WITH CARON
    '\u0226': b'\xc7A', # LATIN CAPITAL LETTER A WITH DOT ABOVE
    '\u0227': b'\xc7a', # LATIN SMALL LETTER A WITH DOT ABOVE
    '\u0228': b'\xd0E', # LATIN CAPITAL LETTER E WITH CEDILLA
    '\u0229': b'\xd0e', # LATIN SMALL LETTER E WITH CEDILLA
    '\u022a': b'\xc5\xc8O', # LATIN CAPITAL LETTER O WITH DIAERESIS AND MACRON
    '\u022b': b'\xc5\xc8o', # LATIN SMALL LETTER O WITH DIAERESIS AND MACRON
    '\u022c': b'\xc5\xc4O', # LATIN CAPITAL LETTER O WITH TILDE AND MACRON
    '\u022d': b'\xc5\xc4o', # LATIN SMALL LETTER O WITH TILDE AND MACRON
    '\u022e': b'\xc7O', # LATIN CAPITAL LETTER O WITH DOT ABOVE
    '\u022f': b'\xc7o', # LATIN SMALL LETTER O WITH DOT ABOVE
    '\u0230': b'\xc5\xc7O', # LATIN CAPITAL LETTER O WITH DOT ABOVE AND MACRON
    '\u0231': b'\xc5\xc7o', # LATIN SMALL LETTER O WITH DOT ABOVE AND MACRON
    '\u0232': b'\xc5Y', # LATIN CAPITAL LETTER Y WITH MACRON
    '\u0233': b'\xc5y', # LATIN SMALL LETTER Y WITH MACRON
    '\u02b9': b'\xbd', # MODIFIER LETTER PRIME
    '\u02ba': b'\xbe', # MODIFIER LETTER DOUBLE PRIME
    '\u02bb': b'\xb0', # MODIFIER LETTER TURNED COMMA
    '\u02bc': b'\xb1', # MODIFIER LETTER APOSTROPHE
    '\u0300': b'\xc1', # COMBINING GRAVE ACCENT
    '\u0301': b'\xc2', # COMBINING ACUTE ACCENT
    '\u0302': b'\xc3', # COMBINING CIRCUMFLEX ACCENT
    '\u0303': b'\xc4', # COMBINING TILDE
    '\u0304': b'\xc5', # COMBINING MACRON
    '\u0306': b'\xc6', # COMBINING BREVE
    '\u0307': b'\xc7', # COMBINING DOT ABOVE
    '\u0308': b'\xc8', # COMBINING DIAERESIS
    '\u0309': b'\xc0', # COMBINING HOOK ABOVE
    '\u030a': b'\xca', # COMBINING RING ABOVE
    '\u030b': b'\xcd', # COMBINING DOUBLE ACUTE ACCENT
    '\u030c': b'\xcf', # COMBINING CARON
    '\u0312': b'\xcc', # COMBINING TURNED COMMA ABOVE
    '\u0315': b'\xcb', # COMBINING COMMA ABOVE RIGHT
    '\u031b': b'\xce', # COMBINING HORN
    '\u031c': b'\xd1', # COMBINING LEFT HALF RING BELOW
    '\u0323': b'\xd6', # COMBINING DOT BELOW
    '\u0324': b'\xd7', # COMBINING DIAERESIS BELOW
    '\u0325': b'\xd4', # COMBINING RING BELOW
    '\u0326': b'\xd2', # COMBINING COMMA BELOW
    '\u0327': b'\xd0', # COMBINING CEDILLA
    '\u0328': b'\xd3', # COMBINING OGONEK
    '\u0329': b'\xda', # COMBINING VERTICAL LINE BELOW
    '\u032d': b'\xdb', # COMBINING CIRCUMFLEX ACCENT BELOW
    '\u032e': b'\xd5', # COMBINING BREVE BELOW
    '\u0332': b'\xd8', # COMBINING LOW LINE
    '\u0333': b'\xd9', # COMBINING DOUBLE LOW LINE
    '\u0340': b'\xc1', # COMBINING GRAVE TONE MARK
    '\u0341': b'\xc2', # COMBINING ACUTE TONE MARK
    '\u0344': b'\xc2\xc8', # COMBINING GREEK DIALYTIKA TONOS
    '\u0374': b'\xbd', # GREEK NUMERAL SIGN
    '\u037e': b';', # GREEK QUESTION MARK
    '\u0387': b'\xb7', # GREEK ANO TELEIA
    '\u1e00': b'\xd4A', # LATIN CAPITAL LETTER A WITH RING BELOW
    '\u1e01': b'\xd4a', # LATIN SMALL LETTER A WITH RING BELOW
    '\u1e02': b'\xc7B', # LATIN CAPITAL LETTER B WITH DOT ABOVE
    '\u1e03': b'\xc7b', # LATIN SMALL LETTER B WITH DOT ABOVE
    '\u1e04': b'\xd6B', # LATIN CAPITAL LETTER B WITH DOT BELOW
    '\u1e05': b'\xd6b', # LATIN SMALL LETTER B WITH DOT BELOW
    '\u1e08': b'\xc2\xd0C', # LATIN CAPITAL LETTER C WITH CEDILLA AND ACUTE
    '\u1e09': b'\xc2\xd0c', # LATIN SMALL LETTER C WITH CEDILLA AND ACUTE
    '\u1e0a': b'\xc7D', # LATIN CAPITAL LETTER D WITH DOT ABOVE
    '\u1e0b': b'\xc7d', # LATIN SMALL LETTER D WITH DOT ABOVE
    '\u1e0c': b'\xd6D', # LATIN CAPITAL LETTER D WITH DOT BELOW
    '\u1e0d': b'\xd6d', # LATIN SMALL LETTER D WITH DOT BELOW
    '\u1e10': b'\xd0D', # LATIN CAPITAL LETTER D WITH CEDILLA
    '\u1e11': b'\xd0d', # LATIN SMALL LETTER D WITH CEDILLA
    '\u1e12': b'\xdbD', # LATIN CAPITAL LETTER D WITH CIRCUMFLEX BELOW
    '\u1e13': b'\xdbd', # LATIN SMALL LETTER D WITH CIRCUMFLEX BELOW
    '\u1e14': b'\xc1\xc5E', # LATIN CAPITAL LETTER E WITH MACRON AND GRAVE
    '\u1e15': b'\xc1\xc5e', # LATIN SMALL LETTER E WITH MACRON AND GRAVE
    '\u1e16': b'\xc2\xc5E', # LATIN CAPITAL LETTER E WITH MACRON AND ACUTE
    '\u1e17': b'\xc2\xc5e', # LATIN SMALL LETTER E WITH MACRON AND ACUTE
    '\u1e18': b'\xdbE', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX BELOW
    '\u1e19': b'\xdbe', # LATIN SMALL LETTER E WITH CIRCUMFLEX BELOW
    '\u1e1c': b'\xc6\xd0E', # LATIN CAPITAL LETTER E WITH CEDILLA AND BREVE
    '\u1e1d': b'\xc6\xd0e', # LATIN SMALL LETTER E WITH CEDILLA AND BREVE
    '\u1e1e': b'\xc7F', # LATIN CAPITAL LETTER F WITH DOT ABOVE
    '\u1e1f': b'\xc7f', # LATIN SMALL LETTER F WITH DOT ABOVE
    '\u1e20': b'\xc5G', # LATIN CAPITAL LETTER G WITH MACRON
    '\u1e21': b'\xc5g', # LATIN SMALL LETTER G WITH MACRON
    '\u1e22': b'\xc7H', # LATIN CAPITAL LETTER H WITH DOT ABOVE
    '\u1e23': b'\xc7h', # LATIN SMALL LETTER H WITH DOT ABOVE
    '\u1e24': b'\xd6H', # LATIN CAPITAL LETTER H WITH DOT BELOW
    '\u1e25': b'\xd6h', # LATIN SMALL LETTER H WITH DOT BELOW
    '\u1e26': b'\xc8H', # LATIN CAPITAL LETTER H WITH DIAERESIS
    '\u1e27': b'\xc8h', # LATIN SMALL LETTER H WITH DIAERESIS
    '\u1e28': b'\xd0H', # LATIN CAPITAL LETTER H WITH CEDILLA
    '\u1e29': b'\xd0h', # LATIN SMALL LETTER H WITH CEDILLA
    '\u1e2a': b'\xd5H', # LATIN CAPITAL LETTER H WITH BREVE BELOW
    '\u1e2b': b'\xd5h', # LATIN SMALL LETTER H WITH BREVE BELOW
    '\u1e2e': b'\xc2\xc8I', # LATIN CAPITAL LETTER I WITH DIAERESIS AND ACUTE
    '\u1e2f': b'\xc2\xc8i', # LATIN SMALL LETTER I WITH DIAERESIS AND ACUTE
    '\u1e30': b'\xc2K', # LATIN CAPITAL LETTER K WITH ACUTE
    '\u1e31': b'\xc2k', # LATIN SMALL LETTER K WITH ACUTE
    '\u1e32': b'\xd6K', # LATIN CAPITAL LETTER K WITH DOT BELOW
    '\u1e33': b'\xd6k', # LATIN SMALL LETTER K WITH DOT BELOW
    '\u1e36': b'\xd6L', # LATIN CAPITAL LETTER L WITH DOT BELOW
    '\u1e37': b'\xd6l', # LATIN SMALL LETTER L WITH DOT BELOW
    '\u1e38': b'\xc5\xd6L', # LATIN CAPITAL LETTER L WITH DOT BELOW AND MACRON
    '\u1e39': b'\xc5\xd6l', # LATIN SMALL LETTER L WITH DOT BELOW AND MACRON
    '\u1e3c': b'\xdbL', # LATIN CAPITAL LETTER L WITH CIRCUMFLEX BELOW
    '\u1e3d': b'\xdbl', # LATIN SMALL LETTER L WITH CIRCUMFLEX BELOW
    '\u1e3e': b'\xc2M', # LATIN CAPITAL LETTER M WITH ACUTE
    '\u1e3f': b'\xc2m', # LATIN SMALL LETTER M WITH ACUTE
    '\u1e40': b'\xc7M', # LATIN CAPITAL LETTER M WITH DOT ABOVE
    '\u1e41': b'\xc7m', # LATIN SMALL LETTER M WITH DOT ABOVE
    '\u1e42': b'\xd6M', # LATIN CAPITAL LETTER M WITH DOT BELOW
    '\u1e43': b'\xd6m', # LATIN SMALL LETTER M WITH DOT BELOW
    '\u1e44': b'\xc7N', # LATIN CAPITAL LETTER N WITH DOT ABOVE
    '\u1e45': b'\xc7n', # LATIN SMALL LETTER N WITH DOT ABOVE
    '\u1e46': b'\xd6N', # LATIN CAPITAL LETTER N WITH DOT BELOW
    '\u1e47': b'\xd6n', # LATIN SMALL LETTER N WITH DOT BELOW
    '\u1e4a': b'\xdbN', # LATIN CAPITAL LETTER N WITH CIRCUMFLEX BELOW
    '\u1e4b': b'\xdbn', # LATIN SMALL LETTER N WITH CIRCUMFLEX BELOW
    '\u1e4c': b'\xc2\xc4O', # LATIN CAPITAL LETTER O WITH TILDE AND ACUTE
    '\u1e4d': b'\xc2\xc4o', # LATIN SMALL LETTER O WITH TILDE AND ACUTE
    '\u1e4e': b'\xc8\xc4O', # LATIN CAPITAL LETTER O WITH TILDE AND DIAERESIS
    '\u1e4f': b'\xc8\xc4o', # LATIN SMALL LETTER O WITH TILDE AND DIAERESIS
    '\u1e50': b'\xc1\xc5O', # LATIN CAPITAL LETTER O WITH MACRON AND GRAVE
    '\u1e51': b'\xc1\xc5o', # LATIN SMALL LETTER O WITH MACRON AND GRAVE
    '\u1e52': b'\xc2\xc5O', # LATIN CAPITAL LETTER O WITH MACRON AND ACUTE
    '\u1e53': b'\xc2\xc5o', # LATIN SMALL LETTER O WITH MACRON AND ACUTE
    '\u1e54': b'\xc2P', # LATIN CAPITAL LETTER P WITH ACUTE
    '\u1e55': b'\xc2p', # LATIN SMALL LETTER P WITH ACUTE
    '\u1e56': b'\xc7P', # LATIN CAPITAL LETTER P WITH DOT ABOVE
    '\u1e57': b'\xc7p', # LATIN SMALL LETTER P WITH DOT ABOVE
    '\u1e58': b'\xc7R', # LATIN CAPITAL LETTER R WITH DOT ABOVE
    '\u1e59': b'\xc7r', # LATIN SMALL LETTER R WITH DOT ABOVE
    '\u1e5a': b'\xd6R', # LATIN CAPITAL LETTER R WITH DOT BELOW
    '\u1e5b': b'\xd6r', # LATIN SMALL LETTER R WITH DOT BELOW
    '\u1e5c': b'\xc5\xd6R', # LATIN CAPITAL LETTER R WITH DOT BELOW AND MACRON
    '\u1e5d': b'\xc5\xd6r', # LATIN SMALL LETTER R WITH DOT BELOW AND MACRON
    '\u1e60': b'\xc7S', # LATIN CAPITAL LETTER S WITH DOT ABOVE
    '\u1e61': b'\xc7s', # LATIN SMALL LETTER S WITH DOT ABOVE
    '\u1e62': b'\xd6S', # LATIN CAPITAL LETTER S WITH DOT BELOW
    '\u1e63': b'\xd6s', # LATIN SMALL LETTER S WITH DOT BELOW
    '\u1e64': b'\xc7\xc2S', # LATIN CAPITAL LETTER S WITH ACUTE AND DOT ABOVE
    '\u1e65': b'\xc7\xc2s', # LATIN SMALL LETTER S WITH ACUTE AND DOT ABOVE
    '\u1e66': b'\xc7\xcfS', # LATIN CAPITAL LETTER S WITH CARON AND DOT ABOVE
    '\u1e67': b'\xc7\xcfs', # LATIN SMALL LETTER S WITH CARON AND DOT ABOVE
    '\u1e68': b'\xc7\xd6S', # LATIN CAPITAL LETTER S WITH DOT BELOW AND DOT ABOVE
    '\u1e69': b'\xc7\xd6s', # LATIN SMALL LETTER S WITH DOT BELOW AND DOT ABOVE
    '\u1e6a': b'\xc7T', # LATIN CAPITAL LETTER T WITH DOT ABOVE
    '\u1e6b': b'\xc7t', # LATIN SMALL LETTER T WITH DOT ABOVE
    '\u1e6c': b'\xd6T', # LATIN CAPITAL LETTER T WITH DOT BELOW
    '\u1e6d': b'\xd6t', # LATIN SMALL LETTER T WITH DOT BELOW
    '\u1e70': b'\xdbT', # LATIN CAPITAL LETTER T WITH CIRCUMFLEX BELOW
    '\u1e71': b'\xdbt', # LATIN SMALL LETTER T WITH CIRCUMFLEX BELOW
    '\u1e72': b'\xd7U', # LATIN CAPITAL LETTER U WITH DIAERESIS BELOW
    '\u1e73': b'\xd7u', # LATIN SMALL LETTER U WITH DIAERESIS BELOW
    '\u1e76': b'\xdbU', # LATIN CAPITAL LETTER U WITH CIRCUMFLEX BELOW
    '\u1e77': b'\xdbu', # LATIN SMALL LETTER U WITH CIRCUMFLEX BELOW
    '\u1e78': b'\xc2\xc4U', # LATIN CAPITAL LETTER U WITH TILDE AND ACUTE
    '\u1e79': b'\xc2\xc4u', # LATIN SMALL LETTER U WITH TILDE AND ACUTE
    '\u1e7a': b'\xc8\xc5U', # LATIN CAPITAL LETTER U WITH MACRON AND DIAERESIS
    '\u1e7b': b'\xc8\xc5u', # LATIN SMALL LETTER U WITH MACRON AND DIAERESIS
    '\u1e7c': b'\xc4V', # LATIN CAPITAL LETTER V WITH TILDE
    '\u1e7d': b'\xc4v', # LATIN SMALL LETTER V WITH TILDE
    '\u1e7e': b'\xd6V', # LATIN CAPITAL LETTER V WITH DOT BELOW
    '\u1e7f': b'\xd6v', # LATIN SMALL LETTER V WITH DOT BELOW
    '\u1e80': b'\xc1W', # LATIN CAPITAL LETTER W WITH GRAVE
    '\u1e81': b'\xc1w', # LATIN SMALL LETTER W WITH GRAVE
    '\u1e82': b'\xc2W', # LATIN CAPITAL LETTER W WITH ACUTE
    '\u1e83': b'\xc2w', # LATIN SMALL LETTER W WITH ACUTE
    '\u1e84': b'\xc8W', # LATIN CAPITAL LETTER W WITH DIAERESIS
    '\u1e85': b'\xc8w', # LATIN SMALL LETTER W WITH DIAERESIS
    '\u1e86': b'\xc7W', # LATIN CAPITAL LETTER W WITH DOT ABOVE
    '\u1e87': b'\xc7w', # LATIN SMALL LETTER W WITH DOT ABOVE
    '\u1e88': b'\xd6W', # LATIN CAPITAL LETTER W WITH DOT BELOW
    '\u1e89': b'\xd6w', # LATIN SMALL LETTER W WITH DOT BELOW
    '\u1e8a': b'\xc7X', # LATIN CAPITAL LETTER X WITH DOT ABOVE
    '\u1e8b': b'\xc7x', # LATIN SMALL LETTER X WITH DOT ABOVE
    '\u1e8c': b'\xc8X', # LATIN CAPITAL LETTER X WITH DIAERESIS
    '\u1e8d': b'\xc8x', # LATIN SMALL LETTER X WITH DIAERESIS
    '\u1e8e': b'\xc7Y', # LATIN CAPITAL LETTER Y WITH DOT ABOVE
    '\u1e8f': b'\xc7y', # LATIN SMALL LETTER Y WITH DOT ABOVE
    '\u1e90': b'\xc3Z', # LATIN CAPITAL LETTER Z WITH CIRCUMFLEX
    '\u1e91': b'\xc3z', # LATIN SMALL LETTER Z WITH CIRCUMFLEX
    '\u1e92': b'\xd6Z', # LATIN CAPITAL LETTER Z WITH DOT BELOW
    '\u1e93': b'\xd6z', # LATIN SMALL LETTER Z WITH DOT BELOW
    '\u1e97': b'\xc8t', # LATIN SMALL LETTER T WITH DIAERESIS
    '\u1e98': b'\xcaw', # LATIN SMALL LETTER W WITH RING ABOVE
    '\u1e99': b'\xcay', # LATIN SMALL LETTER Y WITH RING ABOVE
    '\u1ea0': b'\xd6A', # LATIN CAPITAL LETTER A WITH DOT BELOW
    '\u1ea1': b'\xd6a', # LATIN SMALL LETTER A WITH DOT BELOW
    '\u1ea2': b'\xc0A', # LATIN CAPITAL LETTER A WITH HOOK ABOVE
    '\u1ea3': b'\xc0a', # LATIN SMALL LETTER A WITH HOOK ABOVE
    '\u1ea4': b'\xc2\xc3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND ACUTE
    '\u1ea5': b'\xc2\xc3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND ACUTE
    '\u1ea6': b'\xc1\xc3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND GRAVE
    '\u1ea7': b'\xc1\xc3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND GRAVE
    '\u1ea8': b'\xc0\xc3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ea9': b'\xc0\xc3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1eaa': b'\xc4\xc3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND TILDE
    '\u1eab': b'\xc4\xc3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND TILDE
    '\u1eac': b'\xc3\xd6A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND DOT BELOW
    '\u1ead': b'\xc3\xd6a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND DOT BELOW
    '\u1eae': b'\xc2\xc6A', # LATIN CAPITAL LETTER A WITH BREVE AND ACUTE
    '\u1eaf': b'\xc2\xc6a', # LATIN SMALL LETTER A WITH BREVE AND ACUTE
    '\u1eb0': b'\xc1\xc6A', # LATIN CAPITAL LETTER A WITH BREVE AND GRAVE
    '\u1eb1': b'\xc1\xc6a', # LATIN SMALL LETTER A WITH BREVE AND GRAVE
    '\u1eb2': b'\xc0\xc6A', # LATIN CAPITAL LETTER A WITH BREVE AND HOOK ABOVE
    '\u1eb3': b'\xc0\xc6a', # LATIN SMALL LETTER A WITH BREVE AND HOOK ABOVE
    '\u1eb4': b'\xc4\xc6A', # LATIN CAPITAL LETTER A WITH BREVE AND TILDE
    '\u1eb5': b'\xc4\xc6a', # LATIN SMALL LETTER A WITH BREVE AND TILDE
    '\u1eb6': b'\xc6\xd6A', # LATIN CAPITAL LETTER A WITH BREVE AND DOT BELOW
    '\u1eb7': b'\xc6\xd6a', # LATIN SMALL LETTER A WITH BREVE AND DOT BELOW
    '\u1eb8': b'\xd6E', # LATIN CAPITAL LETTER E WITH DOT BELOW
    '\u1eb9': b'\xd6e', # LATIN SMALL LETTER E WITH DOT BELOW
    '\u1eba': b'\xc0E', # LATIN CAPITAL LETTER E WITH HOOK ABOVE
    '\u1ebb': b'\xc0e', # LATIN SMALL LETTER E WITH HOOK ABOVE
    '\u1ebc': b'\xc4E', # LATIN CAPITAL LETTER E WITH TILDE
    '\u1ebd': b'\xc4e', # LATIN SMALL LETTER E WITH TILDE
    '\u1ebe': b'\xc2\xc3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND ACUTE
    '\u1ebf': b'\xc2\xc3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND ACUTE
    '\u1ec0': b'\xc1\xc3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND GRAVE
    '\u1ec1': b'\xc1\xc3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND GRAVE
    '\u1ec2': b'\xc0\xc3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ec3': b'\xc0\xc3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ec4': b'\xc4\xc3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND TILDE
    '\u1ec5': b'\xc4\xc3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND TILDE
    '\u1ec6': b'\xc3\xd6E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND DOT BELOW
    '\u1ec7': b'\xc3\xd6e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND DOT BELOW
    '\u1ec8': b'\xc0I', # LATIN CAPITAL LETTER I WITH HOOK ABOVE
    '\u1ec9': b'\xc0i', # LATIN SMALL LETTER I WITH HOOK ABOVE
    '\u1eca': b'\xd6I', # LATIN CAPITAL LETTER I WITH DOT BELOW
    '\u1ecb': b'\xd6i', # LATIN SMALL LETTER I WITH DOT BELOW
    '\u1ecc': b'\xd6O', # LATIN CAPITAL LETTER O WITH DOT BELOW
    '\u1ecd': b'\xd6o', # LATIN SMALL LETTER O WITH DOT BELOW
    '\u1ece': b'\xc0O', # LATIN CAPITAL LETTER O WITH HOOK ABOVE
    '\u1ecf': b'\xc0o', # LATIN SMALL LETTER O WITH HOOK ABOVE
    '\u1ed0': b'\xc2\xc3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND ACUTE
    '\u1ed1': b'\xc2\xc3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND ACUTE
    '\u1ed2': b'\xc1\xc3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND GRAVE
    '\u1ed3': b'\xc1\xc3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND GRAVE
    '\u1ed4': b'\xc0\xc3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ed5': b'\xc0\xc3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ed6': b'\xc4\xc3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND TILDE
    '\u1ed7': b'\xc4\xc3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND TILDE
    '\u1ed8': b'\xc3\xd6O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND DOT BELOW
    '\u1ed9': b'\xc3\xd6o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND DOT BELOW
    '\u1eda': b'\xc2\xceO', # LATIN CAPITAL LETTER O WITH HORN AND ACUTE
    '\u1edb': b'\xc2\xceo', # LATIN SMALL LETTER O WITH HORN AND ACUTE
    '\u1edc': b'\xc1\xceO', # LATIN CAPITAL LETTER O WITH HORN AND GRAVE
    '\u1edd': b'\xc1\xceo', # LATIN SMALL LETTER O WITH HORN AND GRAVE
    '\u1ede': b'\xc0\xceO', # LATIN CAPITAL LETTER O WITH HORN AND HOOK ABOVE
    '\u1edf': b'\xc0\xceo', # LATIN SMALL LETTER O WITH HORN AND HOOK ABOVE
    '\u1ee0': b'\xc4\xceO', # LATIN CAPITAL LETTER O WITH HORN AND TILDE
    '\u1ee1': b'\xc4\xceo', # LATIN SMALL LETTER O WITH HORN AND TILDE
    '\u1ee2': b'\xd6\xceO', # LATIN CAPITAL LETTER O WITH HORN AND DOT BELOW
    '\u1ee3': b'\xd6\xceo', # LATIN SMALL LETTER O WITH HORN AND DOT BELOW
    '\u1ee4': b'\xd6U', # LATIN CAPITAL LETTER U WITH DOT BELOW
    '\u1ee5': b'\xd6u', # LATIN SMALL LETTER U WITH DOT BELOW
    '\u1ee6': b'\xc0U', # LATIN CAPITAL LETTER U WITH HOOK ABOVE
    '\u1ee7': b'\xc0u', # LATIN SMALL LETTER U WITH HOOK ABOVE
    '\u1ee8': b'\xc2\xceU', # LATIN CAPITAL LETTER U WITH HORN AND ACUTE
    '\u1ee9': b'\xc2\xceu', # LATIN SMALL LETTER U WITH HORN AND ACUTE
    '\u1eea': b'\xc1\xceU', # LATIN CAPITAL LETTER U WITH HORN AND GRAVE
    '\u1eeb': b'\xc1\xceu', # LATIN SMALL LETTER U WITH HORN AND GRAVE
    '\u1eec': b'\xc0\xceU', # LATIN CAPITAL LETTER U WITH HORN AND HOOK ABOVE
    '\u1eed': b'\xc0\xceu', # LATIN SMALL LETTER U WITH HORN AND HOOK ABOVE
    '\u1eee': b'\xc4\xceU', # LATIN CAPITAL LETTER U WITH HORN AND TILDE
    '\u1eef': b'\xc4\xceu', # LATIN SMALL LETTER U WITH HORN AND TILDE
    '\u1ef0': b'\xd6\xceU', # LATIN CAPITAL LETTER U WITH HORN AND DOT BELOW
    '\u1ef1': b'\xd6\xceu', # LATIN SMALL LETTER U WITH HORN AND DOT BELOW
    '\u1ef2': b'\xc1Y', # LATIN CAPITAL LETTER Y WITH GRAVE
    '\u1ef3': b'\xc1y', # LATIN SMALL LETTER Y WITH GRAVE
    '\u1ef4': b'\xd6Y', # LATIN CAPITAL LETTER Y WITH DOT BELOW
    '\u1ef5': b'\xd6y', # LATIN SMALL LETTER Y WITH DOT BELOW
    '\u1ef6': b'\xc0Y', # LATIN CAPITAL LETTER Y WITH HOOK ABOVE
    '\u1ef7': b'\xc0y', # LATIN SMALL LETTER Y WITH HOOK ABOVE
    '\u1ef8': b'\xc4Y', # LATIN CAPITAL LETTER Y WITH TILDE
    '\u1ef9': b'\xc4y', # LATIN SMALL LETTER Y WITH TILDE
    '\u1fef': b'`', # GREEK VARIA
    '\u2018': b'\xa9', # LEFT SINGLE QUOTATION MARK
    '\u2019': b'\xb9', # RIGHT SINGLE QUOTATION MARK
    '\u201a': b'\xb2', # SINGLE LOW-9 QUOTATION MARK
    '\u201c': b'\xaa', # LEFT DOUBLE QUOTATION MARK
    '\u201d': b'\xba', # RIGHT DOUBLE QUOTATION MARK
    '\u201e': b'\xa2', # DOUBLE LOW-9 QUOTATION MARK
    '\u2020': b'\xa6', # DAGGER
    '\u2021': b'\xb6', # DOUBLE DAGGER
    '\u2032': b'\xa8', # PRIME
    '\u2033': b'\xb8', # DOUBLE PRIME
    '\u2117': b'\xae', # SOUND RECORDING COPYRIGHT
    #'\u212a': b'K', # KELVIN SIGN
    '\u212b': b'\xcaA', # ANGSTROM SIGN
    '\u266d': b'\xac', # MUSIC FLAT SIGN
    '\u266f': b'\xbc', # MUSIC SHARP SIGN
    '\ufe20': b'\xdd', # COMBINING LIGATURE LEFT HALF
    '\ufe21': b'\xde', # COMBINING LIGATURE RIGHT HALF
    '\ufe23': b'\xdf', # COMBINING DOUBLE TILDE RIGHT HALF
}

charmap = {}
for uni, char in getattr(unicodemap, "iteritems", unicodemap.items)():
    if char in charmap:
        continue
    charmap[char] = uni
