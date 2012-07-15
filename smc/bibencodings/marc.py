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
"""MARC codec (USMARC / ANSEL)
"""
from __future__ import unicode_literals, print_function
import codecs
from smc.bibencodings.utils import DecodeIterator

# combining 0xe0 to 0xfe except 0xec, 0xfb, 0xfc, 0xfd
_combining = set([224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235,
                  237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248,
                  249, 250, 254])


def encode(input, errors='strict'):
    """Encode unicode as USMARC
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
        rappend(s)
    return b"".join(result), len(input)


def decode(input, errors='strict', special=None):
    """Decode unicode from USMARC
    """
    if errors not in set(['strict', 'replace', 'ignore', 'repr']):
        raise ValueError("Invalid errors argument %s" % errors)

    result = []
    di = DecodeIterator(input)

    # optimizations
    combining = _combining
    rappend = result.append
    cget = charmap.get

    for c in di:
        o = ord(c)
        # ASCII chars
        if c <= b'\x7f':
            rappend(chr(o))
            continue

        c1, c2 = di.peek(2)
        cc = None
        # 0xe0 to 0xff signals a combined char
        if o in combining and c1 is not None:
            # double combined char
            if ord(c1) in combining and c2 is not None:
                cc = c + c1 + c2
                inc = 2
            else:
                cc = c + c1
                inc = 1
            r = cget(cc)
            if r is not None:
                rappend(r)
                di.evolve(inc)
                continue
            # just the combining
            #r = cget(c)
            #if r is not None:
            #    rappend(r)
            #    i += 1
            #    continue

        # other chars
        #if special is not None:
        #    r = special.get(c)
        #    if r is not None:
        #        rappend(r)
        #        i += 1
        #        continue

        r = cget(c)
        if r is not None:
            rappend(r)
            continue
        # only reached when no result was found
        if errors == "strict":
            pos = di.position
            raise UnicodeError("Can't decode byte%s %r at position %i (context %r)" %
                               ("" if cc is None else "s",
                                c if cc is None else cc,
                                pos, input[pos - 3:pos + 3]))
        elif errors == "replace":
            result.append('\ufffd')
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
    name='marc',
    encode=Codec().encode,
    decode=Codec().decode,
    streamreader=StreamReader,
    streamwriter=StreamWriter)

unicodemap = {
    '\u001b': b'\x1b', # <control>
    '\u001d': b'\x1d', # <control>
    '\u001e': b'\x1e', # <control>
    '\u001f': b'\x1f', # <control>
    '\u0020': b' ', # SPACE
    '\u0021': b'!', # EXCLAMATION MARK
    '\u0022': b'"', # QUOTATION MARK
    '\u0023': b'#', # NUMBER SIGN
    '\u0024': b'$', # DOLLAR SIGN
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
    '\u0098': b'\x88', # <control>
    '\u009c': b'\x89', # <control>
    '\u00a1': b'\xc6', # INVERTED EXCLAMATION MARK
    '\u00a3': b'\xb9', # POUND SIGN
    '\u00a9': b'\xc3', # COPYRIGHT SIGN
    '\u00ae': b'\xaa', # REGISTERED SIGN
    '\u00b0': b'\xc0', # DEGREE SIGN
    '\u00b1': b'\xab', # PLUS-MINUS SIGN
    '\u00b7': b'\xa8', # MIDDLE DOT
    '\u00bf': b'\xc5', # INVERTED QUESTION MARK
    '\u00c0': b'\xe1A', # LATIN CAPITAL LETTER A WITH GRAVE
    '\u00c1': b'\xe2A', # LATIN CAPITAL LETTER A WITH ACUTE
    '\u00c2': b'\xe3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    '\u00c3': b'\xe4A', # LATIN CAPITAL LETTER A WITH TILDE
    '\u00c4': b'\xe8A', # LATIN CAPITAL LETTER A WITH DIAERESIS
    '\u00c5': b'\xeaA', # LATIN CAPITAL LETTER A WITH RING ABOVE
    '\u00c6': b'\xa5', # LATIN CAPITAL LETTER AE
    '\u00c7': b'\xf0C', # LATIN CAPITAL LETTER C WITH CEDILLA
    '\u00c8': b'\xe1E', # LATIN CAPITAL LETTER E WITH GRAVE
    '\u00c9': b'\xe2E', # LATIN CAPITAL LETTER E WITH ACUTE
    '\u00ca': b'\xe3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    '\u00cb': b'\xe8E', # LATIN CAPITAL LETTER E WITH DIAERESIS
    '\u00cc': b'\xe1I', # LATIN CAPITAL LETTER I WITH GRAVE
    '\u00cd': b'\xe2I', # LATIN CAPITAL LETTER I WITH ACUTE
    '\u00ce': b'\xe3I', # LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    '\u00cf': b'\xe8I', # LATIN CAPITAL LETTER I WITH DIAERESIS
    '\u00d1': b'\xe4N', # LATIN CAPITAL LETTER N WITH TILDE
    '\u00d2': b'\xe1O', # LATIN CAPITAL LETTER O WITH GRAVE
    '\u00d3': b'\xe2O', # LATIN CAPITAL LETTER O WITH ACUTE
    '\u00d4': b'\xe3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    '\u00d5': b'\xe4O', # LATIN CAPITAL LETTER O WITH TILDE
    '\u00d6': b'\xe8O', # LATIN CAPITAL LETTER O WITH DIAERESIS
    '\u00d8': b'\xa2', # LATIN CAPITAL LETTER O WITH STROKE
    '\u00d9': b'\xe1U', # LATIN CAPITAL LETTER U WITH GRAVE
    '\u00da': b'\xe2U', # LATIN CAPITAL LETTER U WITH ACUTE
    '\u00db': b'\xe3U', # LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    '\u00dc': b'\xe8U', # LATIN CAPITAL LETTER U WITH DIAERESIS
    '\u00dd': b'\xe2Y', # LATIN CAPITAL LETTER Y WITH ACUTE
    '\u00de': b'\xa4', # LATIN CAPITAL LETTER THORN
    '\u00df': b'\xc7', # LATIN SMALL LETTER SHARP S
    '\u00e0': b'\xe1a', # LATIN SMALL LETTER A WITH GRAVE
    '\u00e1': b'\xe2a', # LATIN SMALL LETTER A WITH ACUTE
    '\u00e2': b'\xe3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX
    '\u00e3': b'\xe4a', # LATIN SMALL LETTER A WITH TILDE
    '\u00e4': b'\xe8a', # LATIN SMALL LETTER A WITH DIAERESIS
    '\u00e5': b'\xeaa', # LATIN SMALL LETTER A WITH RING ABOVE
    '\u00e6': b'\xb5', # LATIN SMALL LETTER AE
    '\u00e7': b'\xf0c', # LATIN SMALL LETTER C WITH CEDILLA
    '\u00e8': b'\xe1e', # LATIN SMALL LETTER E WITH GRAVE
    '\u00e9': b'\xe2e', # LATIN SMALL LETTER E WITH ACUTE
    '\u00ea': b'\xe3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX
    '\u00eb': b'\xe8e', # LATIN SMALL LETTER E WITH DIAERESIS
    '\u00ec': b'\xe1i', # LATIN SMALL LETTER I WITH GRAVE
    '\u00ed': b'\xe2i', # LATIN SMALL LETTER I WITH ACUTE
    '\u00ee': b'\xe3i', # LATIN SMALL LETTER I WITH CIRCUMFLEX
    '\u00ef': b'\xe8i', # LATIN SMALL LETTER I WITH DIAERESIS
    '\u00f0': b'\xba', # LATIN SMALL LETTER ETH
    '\u00f1': b'\xe4n', # LATIN SMALL LETTER N WITH TILDE
    '\u00f2': b'\xe1o', # LATIN SMALL LETTER O WITH GRAVE
    '\u00f3': b'\xe2o', # LATIN SMALL LETTER O WITH ACUTE
    '\u00f4': b'\xe3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX
    '\u00f5': b'\xe4o', # LATIN SMALL LETTER O WITH TILDE
    '\u00f6': b'\xe8o', # LATIN SMALL LETTER O WITH DIAERESIS
    '\u00f8': b'\xb2', # LATIN SMALL LETTER O WITH STROKE
    '\u00f9': b'\xe1u', # LATIN SMALL LETTER U WITH GRAVE
    '\u00fa': b'\xe2u', # LATIN SMALL LETTER U WITH ACUTE
    '\u00fb': b'\xe3u', # LATIN SMALL LETTER U WITH CIRCUMFLEX
    '\u00fc': b'\xe8u', # LATIN SMALL LETTER U WITH DIAERESIS
    '\u00fd': b'\xe2y', # LATIN SMALL LETTER Y WITH ACUTE
    '\u00fe': b'\xb4', # LATIN SMALL LETTER THORN
    '\u00ff': b'\xe8y', # LATIN SMALL LETTER Y WITH DIAERESIS
    '\u0100': b'\xe5A', # LATIN CAPITAL LETTER A WITH MACRON
    '\u0101': b'\xe5a', # LATIN SMALL LETTER A WITH MACRON
    '\u0102': b'\xe6A', # LATIN CAPITAL LETTER A WITH BREVE
    '\u0103': b'\xe6a', # LATIN SMALL LETTER A WITH BREVE
    '\u0104': b'\xf1A', # LATIN CAPITAL LETTER A WITH OGONEK
    '\u0105': b'\xf1a', # LATIN SMALL LETTER A WITH OGONEK
    '\u0106': b'\xe2C', # LATIN CAPITAL LETTER C WITH ACUTE
    '\u0107': b'\xe2c', # LATIN SMALL LETTER C WITH ACUTE
    '\u0108': b'\xe3C', # LATIN CAPITAL LETTER C WITH CIRCUMFLEX
    '\u0109': b'\xe3c', # LATIN SMALL LETTER C WITH CIRCUMFLEX
    '\u010a': b'\xe7C', # LATIN CAPITAL LETTER C WITH DOT ABOVE
    '\u010b': b'\xe7c', # LATIN SMALL LETTER C WITH DOT ABOVE
    '\u010c': b'\xe9C', # LATIN CAPITAL LETTER C WITH CARON
    '\u010d': b'\xe9c', # LATIN SMALL LETTER C WITH CARON
    '\u010e': b'\xe9D', # LATIN CAPITAL LETTER D WITH CARON
    '\u010f': b'\xe9d', # LATIN SMALL LETTER D WITH CARON
    '\u0110': b'\xa3', # LATIN CAPITAL LETTER D WITH STROKE
    '\u0111': b'\xb3', # LATIN SMALL LETTER D WITH STROKE
    '\u0112': b'\xe5E', # LATIN CAPITAL LETTER E WITH MACRON
    '\u0113': b'\xe5e', # LATIN SMALL LETTER E WITH MACRON
    '\u0114': b'\xe6E', # LATIN CAPITAL LETTER E WITH BREVE
    '\u0115': b'\xe6e', # LATIN SMALL LETTER E WITH BREVE
    '\u0116': b'\xe7E', # LATIN CAPITAL LETTER E WITH DOT ABOVE
    '\u0117': b'\xe7e', # LATIN SMALL LETTER E WITH DOT ABOVE
    '\u0118': b'\xf1E', # LATIN CAPITAL LETTER E WITH OGONEK
    '\u0119': b'\xf1e', # LATIN SMALL LETTER E WITH OGONEK
    '\u011a': b'\xe9E', # LATIN CAPITAL LETTER E WITH CARON
    '\u011b': b'\xe9e', # LATIN SMALL LETTER E WITH CARON
    '\u011c': b'\xe3G', # LATIN CAPITAL LETTER G WITH CIRCUMFLEX
    '\u011d': b'\xe3g', # LATIN SMALL LETTER G WITH CIRCUMFLEX
    '\u011e': b'\xe6G', # LATIN CAPITAL LETTER G WITH BREVE
    '\u011f': b'\xe6g', # LATIN SMALL LETTER G WITH BREVE
    '\u0120': b'\xe7G', # LATIN CAPITAL LETTER G WITH DOT ABOVE
    '\u0121': b'\xe7g', # LATIN SMALL LETTER G WITH DOT ABOVE
    '\u0122': b'\xf0G', # LATIN CAPITAL LETTER G WITH CEDILLA
    '\u0123': b'\xf0g', # LATIN SMALL LETTER G WITH CEDILLA
    '\u0124': b'\xe3H', # LATIN CAPITAL LETTER H WITH CIRCUMFLEX
    '\u0125': b'\xe3h', # LATIN SMALL LETTER H WITH CIRCUMFLEX
    '\u0128': b'\xe4I', # LATIN CAPITAL LETTER I WITH TILDE
    '\u0129': b'\xe4i', # LATIN SMALL LETTER I WITH TILDE
    '\u012a': b'\xe5I', # LATIN CAPITAL LETTER I WITH MACRON
    '\u012b': b'\xe5i', # LATIN SMALL LETTER I WITH MACRON
    '\u012c': b'\xe6I', # LATIN CAPITAL LETTER I WITH BREVE
    '\u012d': b'\xe6i', # LATIN SMALL LETTER I WITH BREVE
    '\u012e': b'\xf1I', # LATIN CAPITAL LETTER I WITH OGONEK
    '\u012f': b'\xf1i', # LATIN SMALL LETTER I WITH OGONEK
    '\u0130': b'\xe7I', # LATIN CAPITAL LETTER I WITH DOT ABOVE
    '\u0131': b'\xb8', # LATIN SMALL LETTER DOTLESS I
    '\u0134': b'\xe3J', # LATIN CAPITAL LETTER J WITH CIRCUMFLEX
    '\u0135': b'\xe3j', # LATIN SMALL LETTER J WITH CIRCUMFLEX
    '\u0136': b'\xf0K', # LATIN CAPITAL LETTER K WITH CEDILLA
    '\u0137': b'\xf0k', # LATIN SMALL LETTER K WITH CEDILLA
    '\u0139': b'\xe2L', # LATIN CAPITAL LETTER L WITH ACUTE
    '\u013a': b'\xe2l', # LATIN SMALL LETTER L WITH ACUTE
    '\u013b': b'\xf0L', # LATIN CAPITAL LETTER L WITH CEDILLA
    '\u013c': b'\xf0l', # LATIN SMALL LETTER L WITH CEDILLA
    '\u013d': b'\xe9L', # LATIN CAPITAL LETTER L WITH CARON
    '\u013e': b'\xe9l', # LATIN SMALL LETTER L WITH CARON
    '\u0141': b'\xa1', # LATIN CAPITAL LETTER L WITH STROKE
    '\u0142': b'\xb1', # LATIN SMALL LETTER L WITH STROKE
    '\u0143': b'\xe2N', # LATIN CAPITAL LETTER N WITH ACUTE
    '\u0144': b'\xe2n', # LATIN SMALL LETTER N WITH ACUTE
    '\u0145': b'\xf0N', # LATIN CAPITAL LETTER N WITH CEDILLA
    '\u0146': b'\xf0n', # LATIN SMALL LETTER N WITH CEDILLA
    '\u0147': b'\xe9N', # LATIN CAPITAL LETTER N WITH CARON
    '\u0148': b'\xe9n', # LATIN SMALL LETTER N WITH CARON
    '\u014c': b'\xe5O', # LATIN CAPITAL LETTER O WITH MACRON
    '\u014d': b'\xe5o', # LATIN SMALL LETTER O WITH MACRON
    '\u014e': b'\xe6O', # LATIN CAPITAL LETTER O WITH BREVE
    '\u014f': b'\xe6o', # LATIN SMALL LETTER O WITH BREVE
    '\u0150': b'\xeeO', # LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
    '\u0151': b'\xeeo', # LATIN SMALL LETTER O WITH DOUBLE ACUTE
    '\u0152': b'\xa6', # LATIN CAPITAL LIGATURE OE
    '\u0153': b'\xb6', # LATIN SMALL LIGATURE OE
    '\u0154': b'\xe2R', # LATIN CAPITAL LETTER R WITH ACUTE
    '\u0155': b'\xe2r', # LATIN SMALL LETTER R WITH ACUTE
    '\u0156': b'\xf0R', # LATIN CAPITAL LETTER R WITH CEDILLA
    '\u0157': b'\xf0r', # LATIN SMALL LETTER R WITH CEDILLA
    '\u0158': b'\xe9R', # LATIN CAPITAL LETTER R WITH CARON
    '\u0159': b'\xe9r', # LATIN SMALL LETTER R WITH CARON
    '\u015a': b'\xe2S', # LATIN CAPITAL LETTER S WITH ACUTE
    '\u015b': b'\xe2s', # LATIN SMALL LETTER S WITH ACUTE
    '\u015c': b'\xe3S', # LATIN CAPITAL LETTER S WITH CIRCUMFLEX
    '\u015d': b'\xe3s', # LATIN SMALL LETTER S WITH CIRCUMFLEX
    '\u015e': b'\xf0S', # LATIN CAPITAL LETTER S WITH CEDILLA
    '\u015f': b'\xf0s', # LATIN SMALL LETTER S WITH CEDILLA
    '\u0160': b'\xe9S', # LATIN CAPITAL LETTER S WITH CARON
    '\u0161': b'\xe9s', # LATIN SMALL LETTER S WITH CARON
    '\u0162': b'\xf0T', # LATIN CAPITAL LETTER T WITH CEDILLA
    '\u0163': b'\xf0t', # LATIN SMALL LETTER T WITH CEDILLA
    '\u0164': b'\xe9T', # LATIN CAPITAL LETTER T WITH CARON
    '\u0165': b'\xe9t', # LATIN SMALL LETTER T WITH CARON
    '\u0168': b'\xe4U', # LATIN CAPITAL LETTER U WITH TILDE
    '\u0169': b'\xe4u', # LATIN SMALL LETTER U WITH TILDE
    '\u016a': b'\xe5U', # LATIN CAPITAL LETTER U WITH MACRON
    '\u016b': b'\xe5u', # LATIN SMALL LETTER U WITH MACRON
    '\u016c': b'\xe6U', # LATIN CAPITAL LETTER U WITH BREVE
    '\u016d': b'\xe6u', # LATIN SMALL LETTER U WITH BREVE
    '\u016e': b'\xeaU', # LATIN CAPITAL LETTER U WITH RING ABOVE
    '\u016f': b'\xeau', # LATIN SMALL LETTER U WITH RING ABOVE
    '\u0170': b'\xeeU', # LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
    '\u0171': b'\xeeu', # LATIN SMALL LETTER U WITH DOUBLE ACUTE
    '\u0172': b'\xf1U', # LATIN CAPITAL LETTER U WITH OGONEK
    '\u0173': b'\xf1u', # LATIN SMALL LETTER U WITH OGONEK
    '\u0174': b'\xe3W', # LATIN CAPITAL LETTER W WITH CIRCUMFLEX
    '\u0175': b'\xe3w', # LATIN SMALL LETTER W WITH CIRCUMFLEX
    '\u0176': b'\xe3Y', # LATIN CAPITAL LETTER Y WITH CIRCUMFLEX
    '\u0177': b'\xe3y', # LATIN SMALL LETTER Y WITH CIRCUMFLEX
    '\u0178': b'\xe8Y', # LATIN CAPITAL LETTER Y WITH DIAERESIS
    '\u0179': b'\xe2Z', # LATIN CAPITAL LETTER Z WITH ACUTE
    '\u017a': b'\xe2z', # LATIN SMALL LETTER Z WITH ACUTE
    '\u017b': b'\xe7Z', # LATIN CAPITAL LETTER Z WITH DOT ABOVE
    '\u017c': b'\xe7z', # LATIN SMALL LETTER Z WITH DOT ABOVE
    '\u017d': b'\xe9Z', # LATIN CAPITAL LETTER Z WITH CARON
    '\u017e': b'\xe9z', # LATIN SMALL LETTER Z WITH CARON
    '\u01a0': b'\xac', # LATIN CAPITAL LETTER O WITH HORN
    '\u01a1': b'\xbc', # LATIN SMALL LETTER O WITH HORN
    '\u01af': b'\xad', # LATIN CAPITAL LETTER U WITH HORN
    '\u01b0': b'\xbd', # LATIN SMALL LETTER U WITH HORN
    '\u01cd': b'\xe9A', # LATIN CAPITAL LETTER A WITH CARON
    '\u01ce': b'\xe9a', # LATIN SMALL LETTER A WITH CARON
    '\u01cf': b'\xe9I', # LATIN CAPITAL LETTER I WITH CARON
    '\u01d0': b'\xe9i', # LATIN SMALL LETTER I WITH CARON
    '\u01d1': b'\xe9O', # LATIN CAPITAL LETTER O WITH CARON
    '\u01d2': b'\xe9o', # LATIN SMALL LETTER O WITH CARON
    '\u01d3': b'\xe9U', # LATIN CAPITAL LETTER U WITH CARON
    '\u01d4': b'\xe9u', # LATIN SMALL LETTER U WITH CARON
    '\u01d5': b'\xe5\xe8U', # LATIN CAPITAL LETTER U WITH DIAERESIS AND MACRON
    '\u01d6': b'\xe5\xe8u', # LATIN SMALL LETTER U WITH DIAERESIS AND MACRON
    '\u01d7': b'\xe2\xe8U', # LATIN CAPITAL LETTER U WITH DIAERESIS AND ACUTE
    '\u01d8': b'\xe2\xe8u', # LATIN SMALL LETTER U WITH DIAERESIS AND ACUTE
    '\u01d9': b'\xe9\xe8U', # LATIN CAPITAL LETTER U WITH DIAERESIS AND CARON
    '\u01da': b'\xe9\xe8u', # LATIN SMALL LETTER U WITH DIAERESIS AND CARON
    '\u01db': b'\xe1\xe8U', # LATIN CAPITAL LETTER U WITH DIAERESIS AND GRAVE
    '\u01dc': b'\xe1\xe8u', # LATIN SMALL LETTER U WITH DIAERESIS AND GRAVE
    '\u01de': b'\xe5\xe8A', # LATIN CAPITAL LETTER A WITH DIAERESIS AND MACRON
    '\u01df': b'\xe5\xe8a', # LATIN SMALL LETTER A WITH DIAERESIS AND MACRON
    '\u01e0': b'\xe5\xe7A', # LATIN CAPITAL LETTER A WITH DOT ABOVE AND MACRON
    '\u01e1': b'\xe5\xe7a', # LATIN SMALL LETTER A WITH DOT ABOVE AND MACRON
    '\u01e2': b'\xe5\xa5', # LATIN CAPITAL LETTER AE WITH MACRON
    '\u01e3': b'\xe5\xb5', # LATIN SMALL LETTER AE WITH MACRON
    '\u01e6': b'\xe9G', # LATIN CAPITAL LETTER G WITH CARON
    '\u01e7': b'\xe9g', # LATIN SMALL LETTER G WITH CARON
    '\u01e8': b'\xe9K', # LATIN CAPITAL LETTER K WITH CARON
    '\u01e9': b'\xe9k', # LATIN SMALL LETTER K WITH CARON
    '\u01ea': b'\xf1O', # LATIN CAPITAL LETTER O WITH OGONEK
    '\u01eb': b'\xf1o', # LATIN SMALL LETTER O WITH OGONEK
    '\u01ec': b'\xe5\xf1O', # LATIN CAPITAL LETTER O WITH OGONEK AND MACRON
    '\u01ed': b'\xe5\xf1o', # LATIN SMALL LETTER O WITH OGONEK AND MACRON
    '\u01f0': b'\xe9j', # LATIN SMALL LETTER J WITH CARON
    '\u01f4': b'\xe2G', # LATIN CAPITAL LETTER G WITH ACUTE
    '\u01f5': b'\xe2g', # LATIN SMALL LETTER G WITH ACUTE
    '\u01f8': b'\xe1N', # LATIN CAPITAL LETTER N WITH GRAVE
    '\u01f9': b'\xe1n', # LATIN SMALL LETTER N WITH GRAVE
    '\u01fa': b'\xe2\xeaA', # LATIN CAPITAL LETTER A WITH RING ABOVE AND ACUTE
    '\u01fb': b'\xe2\xeaa', # LATIN SMALL LETTER A WITH RING ABOVE AND ACUTE
    '\u01fc': b'\xe2\xa5', # LATIN CAPITAL LETTER AE WITH ACUTE
    '\u01fd': b'\xe2\xb5', # LATIN SMALL LETTER AE WITH ACUTE
    '\u01fe': b'\xe2\xa2', # LATIN CAPITAL LETTER O WITH STROKE AND ACUTE
    '\u01ff': b'\xe2\xb2', # LATIN SMALL LETTER O WITH STROKE AND ACUTE
    '\u0218': b'\xf7S', # LATIN CAPITAL LETTER S WITH COMMA BELOW
    '\u0219': b'\xf7s', # LATIN SMALL LETTER S WITH COMMA BELOW
    '\u021a': b'\xf7T', # LATIN CAPITAL LETTER T WITH COMMA BELOW
    '\u021b': b'\xf7t', # LATIN SMALL LETTER T WITH COMMA BELOW
    '\u021e': b'\xe9H', # LATIN CAPITAL LETTER H WITH CARON
    '\u021f': b'\xe9h', # LATIN SMALL LETTER H WITH CARON
    '\u0226': b'\xe7A', # LATIN CAPITAL LETTER A WITH DOT ABOVE
    '\u0227': b'\xe7a', # LATIN SMALL LETTER A WITH DOT ABOVE
    '\u0228': b'\xf0E', # LATIN CAPITAL LETTER E WITH CEDILLA
    '\u0229': b'\xf0e', # LATIN SMALL LETTER E WITH CEDILLA
    '\u022a': b'\xe5\xe8O', # LATIN CAPITAL LETTER O WITH DIAERESIS AND MACRON
    '\u022b': b'\xe5\xe8o', # LATIN SMALL LETTER O WITH DIAERESIS AND MACRON
    '\u022c': b'\xe5\xe4O', # LATIN CAPITAL LETTER O WITH TILDE AND MACRON
    '\u022d': b'\xe5\xe4o', # LATIN SMALL LETTER O WITH TILDE AND MACRON
    '\u022e': b'\xe7O', # LATIN CAPITAL LETTER O WITH DOT ABOVE
    '\u022f': b'\xe7o', # LATIN SMALL LETTER O WITH DOT ABOVE
    '\u0230': b'\xe5\xe7O', # LATIN CAPITAL LETTER O WITH DOT ABOVE AND MACRON
    '\u0231': b'\xe5\xe7o', # LATIN SMALL LETTER O WITH DOT ABOVE AND MACRON
    '\u0232': b'\xe5Y', # LATIN CAPITAL LETTER Y WITH MACRON
    '\u0233': b'\xe5y', # LATIN SMALL LETTER Y WITH MACRON
    '\u02b9': b'\xa7', # MODIFIER LETTER PRIME
    '\u02ba': b'\xb7', # MODIFIER LETTER DOUBLE PRIME
    '\u02bb': b'\xb0', # MODIFIER LETTER TURNED COMMA
    '\u02bc': b'\xae', # MODIFIER LETTER APOSTROPHE
    '\u0300': b'\xe1', # COMBINING GRAVE ACCENT
    '\u0301': b'\xe2', # COMBINING ACUTE ACCENT
    '\u0302': b'\xe3', # COMBINING CIRCUMFLEX ACCENT
    '\u0303': b'\xe4', # COMBINING TILDE
    '\u0304': b'\xe5', # COMBINING MACRON
    '\u0306': b'\xe6', # COMBINING BREVE
    '\u0307': b'\xe7', # COMBINING DOT ABOVE
    '\u0308': b'\xe8', # COMBINING DIAERESIS
    '\u0309': b'\xe0', # COMBINING HOOK ABOVE
    '\u030a': b'\xea', # COMBINING RING ABOVE
    '\u030b': b'\xee', # COMBINING DOUBLE ACUTE ACCENT
    '\u030c': b'\xe9', # COMBINING CARON
    '\u0310': b'\xef', # COMBINING CANDRABINDU
    '\u0313': b'\xfe', # COMBINING COMMA ABOVE
    '\u0315': b'\xed', # COMBINING COMMA ABOVE RIGHT
    '\u031c': b'\xf8', # COMBINING LEFT HALF RING BELOW
    '\u0323': b'\xf2', # COMBINING DOT BELOW
    '\u0324': b'\xf3', # COMBINING DIAERESIS BELOW
    '\u0325': b'\xf4', # COMBINING RING BELOW
    '\u0326': b'\xf7', # COMBINING COMMA BELOW
    '\u0327': b'\xf0', # COMBINING CEDILLA
    '\u0328': b'\xf1', # COMBINING OGONEK
    '\u032e': b'\xf9', # COMBINING BREVE BELOW
    '\u0332': b'\xf6', # COMBINING LOW LINE
    '\u0333': b'\xf5', # COMBINING DOUBLE LOW LINE
    '\u0340': b'\xe1', # COMBINING GRAVE TONE MARK
    '\u0341': b'\xe2', # COMBINING ACUTE TONE MARK
    '\u0343': b'\xfe', # COMBINING GREEK KORONIS
    '\u0344': b'\xe2\xe8', # COMBINING GREEK DIALYTIKA TONOS
    '\u0360': b'\xfa', # COMBINING DOUBLE TILDE
    '\u0361': b'\xeb', # COMBINING DOUBLE INVERTED BREVE
    '\u0374': b'\xa7', # GREEK NUMERAL SIGN
    '\u037e': b';', # GREEK QUESTION MARK
    '\u0387': b'\xa8', # GREEK ANO TELEIA
    '\u1e00': b'\xf4A', # LATIN CAPITAL LETTER A WITH RING BELOW
    '\u1e01': b'\xf4a', # LATIN SMALL LETTER A WITH RING BELOW
    '\u1e02': b'\xe7B', # LATIN CAPITAL LETTER B WITH DOT ABOVE
    '\u1e03': b'\xe7b', # LATIN SMALL LETTER B WITH DOT ABOVE
    '\u1e04': b'\xf2B', # LATIN CAPITAL LETTER B WITH DOT BELOW
    '\u1e05': b'\xf2b', # LATIN SMALL LETTER B WITH DOT BELOW
    '\u1e08': b'\xe2\xf0C', # LATIN CAPITAL LETTER C WITH CEDILLA AND ACUTE
    '\u1e09': b'\xe2\xf0c', # LATIN SMALL LETTER C WITH CEDILLA AND ACUTE
    '\u1e0a': b'\xe7D', # LATIN CAPITAL LETTER D WITH DOT ABOVE
    '\u1e0b': b'\xe7d', # LATIN SMALL LETTER D WITH DOT ABOVE
    '\u1e0c': b'\xf2D', # LATIN CAPITAL LETTER D WITH DOT BELOW
    '\u1e0d': b'\xf2d', # LATIN SMALL LETTER D WITH DOT BELOW
    '\u1e10': b'\xf0D', # LATIN CAPITAL LETTER D WITH CEDILLA
    '\u1e11': b'\xf0d', # LATIN SMALL LETTER D WITH CEDILLA
    '\u1e14': b'\xe1\xe5E', # LATIN CAPITAL LETTER E WITH MACRON AND GRAVE
    '\u1e15': b'\xe1\xe5e', # LATIN SMALL LETTER E WITH MACRON AND GRAVE
    '\u1e16': b'\xe2\xe5E', # LATIN CAPITAL LETTER E WITH MACRON AND ACUTE
    '\u1e17': b'\xe2\xe5e', # LATIN SMALL LETTER E WITH MACRON AND ACUTE
    '\u1e1c': b'\xe6\xf0E', # LATIN CAPITAL LETTER E WITH CEDILLA AND BREVE
    '\u1e1d': b'\xe6\xf0e', # LATIN SMALL LETTER E WITH CEDILLA AND BREVE
    '\u1e1e': b'\xe7F', # LATIN CAPITAL LETTER F WITH DOT ABOVE
    '\u1e1f': b'\xe7f', # LATIN SMALL LETTER F WITH DOT ABOVE
    '\u1e20': b'\xe5G', # LATIN CAPITAL LETTER G WITH MACRON
    '\u1e21': b'\xe5g', # LATIN SMALL LETTER G WITH MACRON
    '\u1e22': b'\xe7H', # LATIN CAPITAL LETTER H WITH DOT ABOVE
    '\u1e23': b'\xe7h', # LATIN SMALL LETTER H WITH DOT ABOVE
    '\u1e24': b'\xf2H', # LATIN CAPITAL LETTER H WITH DOT BELOW
    '\u1e25': b'\xf2h', # LATIN SMALL LETTER H WITH DOT BELOW
    '\u1e26': b'\xe8H', # LATIN CAPITAL LETTER H WITH DIAERESIS
    '\u1e27': b'\xe8h', # LATIN SMALL LETTER H WITH DIAERESIS
    '\u1e28': b'\xf0H', # LATIN CAPITAL LETTER H WITH CEDILLA
    '\u1e29': b'\xf0h', # LATIN SMALL LETTER H WITH CEDILLA
    '\u1e2a': b'\xf9H', # LATIN CAPITAL LETTER H WITH BREVE BELOW
    '\u1e2b': b'\xf9h', # LATIN SMALL LETTER H WITH BREVE BELOW
    '\u1e2e': b'\xe2\xe8I', # LATIN CAPITAL LETTER I WITH DIAERESIS AND ACUTE
    '\u1e2f': b'\xe2\xe8i', # LATIN SMALL LETTER I WITH DIAERESIS AND ACUTE
    '\u1e30': b'\xe2K', # LATIN CAPITAL LETTER K WITH ACUTE
    '\u1e31': b'\xe2k', # LATIN SMALL LETTER K WITH ACUTE
    '\u1e32': b'\xf2K', # LATIN CAPITAL LETTER K WITH DOT BELOW
    '\u1e33': b'\xf2k', # LATIN SMALL LETTER K WITH DOT BELOW
    '\u1e36': b'\xf2L', # LATIN CAPITAL LETTER L WITH DOT BELOW
    '\u1e37': b'\xf2l', # LATIN SMALL LETTER L WITH DOT BELOW
    '\u1e38': b'\xe5\xf2L', # LATIN CAPITAL LETTER L WITH DOT BELOW AND MACRON
    '\u1e39': b'\xe5\xf2l', # LATIN SMALL LETTER L WITH DOT BELOW AND MACRON
    '\u1e3e': b'\xe2M', # LATIN CAPITAL LETTER M WITH ACUTE
    '\u1e3f': b'\xe2m', # LATIN SMALL LETTER M WITH ACUTE
    '\u1e40': b'\xe7M', # LATIN CAPITAL LETTER M WITH DOT ABOVE
    '\u1e41': b'\xe7m', # LATIN SMALL LETTER M WITH DOT ABOVE
    '\u1e42': b'\xf2M', # LATIN CAPITAL LETTER M WITH DOT BELOW
    '\u1e43': b'\xf2m', # LATIN SMALL LETTER M WITH DOT BELOW
    '\u1e44': b'\xe7N', # LATIN CAPITAL LETTER N WITH DOT ABOVE
    '\u1e45': b'\xe7n', # LATIN SMALL LETTER N WITH DOT ABOVE
    '\u1e46': b'\xf2N', # LATIN CAPITAL LETTER N WITH DOT BELOW
    '\u1e47': b'\xf2n', # LATIN SMALL LETTER N WITH DOT BELOW
    '\u1e4c': b'\xe2\xe4O', # LATIN CAPITAL LETTER O WITH TILDE AND ACUTE
    '\u1e4d': b'\xe2\xe4o', # LATIN SMALL LETTER O WITH TILDE AND ACUTE
    '\u1e4e': b'\xe8\xe4O', # LATIN CAPITAL LETTER O WITH TILDE AND DIAERESIS
    '\u1e4f': b'\xe8\xe4o', # LATIN SMALL LETTER O WITH TILDE AND DIAERESIS
    '\u1e50': b'\xe1\xe5O', # LATIN CAPITAL LETTER O WITH MACRON AND GRAVE
    '\u1e51': b'\xe1\xe5o', # LATIN SMALL LETTER O WITH MACRON AND GRAVE
    '\u1e52': b'\xe2\xe5O', # LATIN CAPITAL LETTER O WITH MACRON AND ACUTE
    '\u1e53': b'\xe2\xe5o', # LATIN SMALL LETTER O WITH MACRON AND ACUTE
    '\u1e54': b'\xe2P', # LATIN CAPITAL LETTER P WITH ACUTE
    '\u1e55': b'\xe2p', # LATIN SMALL LETTER P WITH ACUTE
    '\u1e56': b'\xe7P', # LATIN CAPITAL LETTER P WITH DOT ABOVE
    '\u1e57': b'\xe7p', # LATIN SMALL LETTER P WITH DOT ABOVE
    '\u1e58': b'\xe7R', # LATIN CAPITAL LETTER R WITH DOT ABOVE
    '\u1e59': b'\xe7r', # LATIN SMALL LETTER R WITH DOT ABOVE
    '\u1e5a': b'\xf2R', # LATIN CAPITAL LETTER R WITH DOT BELOW
    '\u1e5b': b'\xf2r', # LATIN SMALL LETTER R WITH DOT BELOW
    '\u1e5c': b'\xe5\xf2R', # LATIN CAPITAL LETTER R WITH DOT BELOW AND MACRON
    '\u1e5d': b'\xe5\xf2r', # LATIN SMALL LETTER R WITH DOT BELOW AND MACRON
    '\u1e60': b'\xe7S', # LATIN CAPITAL LETTER S WITH DOT ABOVE
    '\u1e61': b'\xe7s', # LATIN SMALL LETTER S WITH DOT ABOVE
    '\u1e62': b'\xf2S', # LATIN CAPITAL LETTER S WITH DOT BELOW
    '\u1e63': b'\xf2s', # LATIN SMALL LETTER S WITH DOT BELOW
    '\u1e64': b'\xe7\xe2S', # LATIN CAPITAL LETTER S WITH ACUTE AND DOT ABOVE
    '\u1e65': b'\xe7\xe2s', # LATIN SMALL LETTER S WITH ACUTE AND DOT ABOVE
    '\u1e66': b'\xe7\xe9S', # LATIN CAPITAL LETTER S WITH CARON AND DOT ABOVE
    '\u1e67': b'\xe7\xe9s', # LATIN SMALL LETTER S WITH CARON AND DOT ABOVE
    '\u1e68': b'\xe7\xf2S', # LATIN CAPITAL LETTER S WITH DOT BELOW AND DOT ABOVE
    '\u1e69': b'\xe7\xf2s', # LATIN SMALL LETTER S WITH DOT BELOW AND DOT ABOVE
    '\u1e6a': b'\xe7T', # LATIN CAPITAL LETTER T WITH DOT ABOVE
    '\u1e6b': b'\xe7t', # LATIN SMALL LETTER T WITH DOT ABOVE
    '\u1e6c': b'\xf2T', # LATIN CAPITAL LETTER T WITH DOT BELOW
    '\u1e6d': b'\xf2t', # LATIN SMALL LETTER T WITH DOT BELOW
    '\u1e72': b'\xf3U', # LATIN CAPITAL LETTER U WITH DIAERESIS BELOW
    '\u1e73': b'\xf3u', # LATIN SMALL LETTER U WITH DIAERESIS BELOW
    '\u1e78': b'\xe2\xe4U', # LATIN CAPITAL LETTER U WITH TILDE AND ACUTE
    '\u1e79': b'\xe2\xe4u', # LATIN SMALL LETTER U WITH TILDE AND ACUTE
    '\u1e7a': b'\xe8\xe5U', # LATIN CAPITAL LETTER U WITH MACRON AND DIAERESIS
    '\u1e7b': b'\xe8\xe5u', # LATIN SMALL LETTER U WITH MACRON AND DIAERESIS
    '\u1e7c': b'\xe4V', # LATIN CAPITAL LETTER V WITH TILDE
    '\u1e7d': b'\xe4v', # LATIN SMALL LETTER V WITH TILDE
    '\u1e7e': b'\xf2V', # LATIN CAPITAL LETTER V WITH DOT BELOW
    '\u1e7f': b'\xf2v', # LATIN SMALL LETTER V WITH DOT BELOW
    '\u1e80': b'\xe1W', # LATIN CAPITAL LETTER W WITH GRAVE
    '\u1e81': b'\xe1w', # LATIN SMALL LETTER W WITH GRAVE
    '\u1e82': b'\xe2W', # LATIN CAPITAL LETTER W WITH ACUTE
    '\u1e83': b'\xe2w', # LATIN SMALL LETTER W WITH ACUTE
    '\u1e84': b'\xe8W', # LATIN CAPITAL LETTER W WITH DIAERESIS
    '\u1e85': b'\xe8w', # LATIN SMALL LETTER W WITH DIAERESIS
    '\u1e86': b'\xe7W', # LATIN CAPITAL LETTER W WITH DOT ABOVE
    '\u1e87': b'\xe7w', # LATIN SMALL LETTER W WITH DOT ABOVE
    '\u1e88': b'\xf2W', # LATIN CAPITAL LETTER W WITH DOT BELOW
    '\u1e89': b'\xf2w', # LATIN SMALL LETTER W WITH DOT BELOW
    '\u1e8a': b'\xe7X', # LATIN CAPITAL LETTER X WITH DOT ABOVE
    '\u1e8b': b'\xe7x', # LATIN SMALL LETTER X WITH DOT ABOVE
    '\u1e8c': b'\xe8X', # LATIN CAPITAL LETTER X WITH DIAERESIS
    '\u1e8d': b'\xe8x', # LATIN SMALL LETTER X WITH DIAERESIS
    '\u1e8e': b'\xe7Y', # LATIN CAPITAL LETTER Y WITH DOT ABOVE
    '\u1e8f': b'\xe7y', # LATIN SMALL LETTER Y WITH DOT ABOVE
    '\u1e90': b'\xe3Z', # LATIN CAPITAL LETTER Z WITH CIRCUMFLEX
    '\u1e91': b'\xe3z', # LATIN SMALL LETTER Z WITH CIRCUMFLEX
    '\u1e92': b'\xf2Z', # LATIN CAPITAL LETTER Z WITH DOT BELOW
    '\u1e93': b'\xf2z', # LATIN SMALL LETTER Z WITH DOT BELOW
    '\u1e97': b'\xe8t', # LATIN SMALL LETTER T WITH DIAERESIS
    '\u1e98': b'\xeaw', # LATIN SMALL LETTER W WITH RING ABOVE
    '\u1e99': b'\xeay', # LATIN SMALL LETTER Y WITH RING ABOVE
    '\u1ea0': b'\xf2A', # LATIN CAPITAL LETTER A WITH DOT BELOW
    '\u1ea1': b'\xf2a', # LATIN SMALL LETTER A WITH DOT BELOW
    '\u1ea2': b'\xe0A', # LATIN CAPITAL LETTER A WITH HOOK ABOVE
    '\u1ea3': b'\xe0a', # LATIN SMALL LETTER A WITH HOOK ABOVE
    '\u1ea4': b'\xe2\xe3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND ACUTE
    '\u1ea5': b'\xe2\xe3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND ACUTE
    '\u1ea6': b'\xe1\xe3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND GRAVE
    '\u1ea7': b'\xe1\xe3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND GRAVE
    '\u1ea8': b'\xe0\xe3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ea9': b'\xe0\xe3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1eaa': b'\xe4\xe3A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND TILDE
    '\u1eab': b'\xe4\xe3a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND TILDE
    '\u1eac': b'\xe3\xf2A', # LATIN CAPITAL LETTER A WITH CIRCUMFLEX AND DOT BELOW
    '\u1ead': b'\xe3\xf2a', # LATIN SMALL LETTER A WITH CIRCUMFLEX AND DOT BELOW
    '\u1eae': b'\xe2\xe6A', # LATIN CAPITAL LETTER A WITH BREVE AND ACUTE
    '\u1eaf': b'\xe2\xe6a', # LATIN SMALL LETTER A WITH BREVE AND ACUTE
    '\u1eb0': b'\xe1\xe6A', # LATIN CAPITAL LETTER A WITH BREVE AND GRAVE
    '\u1eb1': b'\xe1\xe6a', # LATIN SMALL LETTER A WITH BREVE AND GRAVE
    '\u1eb2': b'\xe0\xe6A', # LATIN CAPITAL LETTER A WITH BREVE AND HOOK ABOVE
    '\u1eb3': b'\xe0\xe6a', # LATIN SMALL LETTER A WITH BREVE AND HOOK ABOVE
    '\u1eb4': b'\xe4\xe6A', # LATIN CAPITAL LETTER A WITH BREVE AND TILDE
    '\u1eb5': b'\xe4\xe6a', # LATIN SMALL LETTER A WITH BREVE AND TILDE
    '\u1eb6': b'\xe6\xf2A', # LATIN CAPITAL LETTER A WITH BREVE AND DOT BELOW
    '\u1eb7': b'\xe6\xf2a', # LATIN SMALL LETTER A WITH BREVE AND DOT BELOW
    '\u1eb8': b'\xf2E', # LATIN CAPITAL LETTER E WITH DOT BELOW
    '\u1eb9': b'\xf2e', # LATIN SMALL LETTER E WITH DOT BELOW
    '\u1eba': b'\xe0E', # LATIN CAPITAL LETTER E WITH HOOK ABOVE
    '\u1ebb': b'\xe0e', # LATIN SMALL LETTER E WITH HOOK ABOVE
    '\u1ebc': b'\xe4E', # LATIN CAPITAL LETTER E WITH TILDE
    '\u1ebd': b'\xe4e', # LATIN SMALL LETTER E WITH TILDE
    '\u1ebe': b'\xe2\xe3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND ACUTE
    '\u1ebf': b'\xe2\xe3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND ACUTE
    '\u1ec0': b'\xe1\xe3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND GRAVE
    '\u1ec1': b'\xe1\xe3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND GRAVE
    '\u1ec2': b'\xe0\xe3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ec3': b'\xe0\xe3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ec4': b'\xe4\xe3E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND TILDE
    '\u1ec5': b'\xe4\xe3e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND TILDE
    '\u1ec6': b'\xe3\xf2E', # LATIN CAPITAL LETTER E WITH CIRCUMFLEX AND DOT BELOW
    '\u1ec7': b'\xe3\xf2e', # LATIN SMALL LETTER E WITH CIRCUMFLEX AND DOT BELOW
    '\u1ec8': b'\xe0I', # LATIN CAPITAL LETTER I WITH HOOK ABOVE
    '\u1ec9': b'\xe0i', # LATIN SMALL LETTER I WITH HOOK ABOVE
    '\u1eca': b'\xf2I', # LATIN CAPITAL LETTER I WITH DOT BELOW
    '\u1ecb': b'\xf2i', # LATIN SMALL LETTER I WITH DOT BELOW
    '\u1ecc': b'\xf2O', # LATIN CAPITAL LETTER O WITH DOT BELOW
    '\u1ecd': b'\xf2o', # LATIN SMALL LETTER O WITH DOT BELOW
    '\u1ece': b'\xe0O', # LATIN CAPITAL LETTER O WITH HOOK ABOVE
    '\u1ecf': b'\xe0o', # LATIN SMALL LETTER O WITH HOOK ABOVE
    '\u1ed0': b'\xe2\xe3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND ACUTE
    '\u1ed1': b'\xe2\xe3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND ACUTE
    '\u1ed2': b'\xe1\xe3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND GRAVE
    '\u1ed3': b'\xe1\xe3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND GRAVE
    '\u1ed4': b'\xe0\xe3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ed5': b'\xe0\xe3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND HOOK ABOVE
    '\u1ed6': b'\xe4\xe3O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND TILDE
    '\u1ed7': b'\xe4\xe3o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND TILDE
    '\u1ed8': b'\xe3\xf2O', # LATIN CAPITAL LETTER O WITH CIRCUMFLEX AND DOT BELOW
    '\u1ed9': b'\xe3\xf2o', # LATIN SMALL LETTER O WITH CIRCUMFLEX AND DOT BELOW
    '\u1eda': b'\xe2\xac', # LATIN CAPITAL LETTER O WITH HORN AND ACUTE
    '\u1edb': b'\xe2\xbc', # LATIN SMALL LETTER O WITH HORN AND ACUTE
    '\u1edc': b'\xe1\xac', # LATIN CAPITAL LETTER O WITH HORN AND GRAVE
    '\u1edd': b'\xe1\xbc', # LATIN SMALL LETTER O WITH HORN AND GRAVE
    '\u1ede': b'\xe0\xac', # LATIN CAPITAL LETTER O WITH HORN AND HOOK ABOVE
    '\u1edf': b'\xe0\xbc', # LATIN SMALL LETTER O WITH HORN AND HOOK ABOVE
    '\u1ee0': b'\xe4\xac', # LATIN CAPITAL LETTER O WITH HORN AND TILDE
    '\u1ee1': b'\xe4\xbc', # LATIN SMALL LETTER O WITH HORN AND TILDE
    '\u1ee2': b'\xf2\xac', # LATIN CAPITAL LETTER O WITH HORN AND DOT BELOW
    '\u1ee3': b'\xf2\xbc', # LATIN SMALL LETTER O WITH HORN AND DOT BELOW
    '\u1ee4': b'\xf2U', # LATIN CAPITAL LETTER U WITH DOT BELOW
    '\u1ee5': b'\xf2u', # LATIN SMALL LETTER U WITH DOT BELOW
    '\u1ee6': b'\xe0U', # LATIN CAPITAL LETTER U WITH HOOK ABOVE
    '\u1ee7': b'\xe0u', # LATIN SMALL LETTER U WITH HOOK ABOVE
    '\u1ee8': b'\xe2\xad', # LATIN CAPITAL LETTER U WITH HORN AND ACUTE
    '\u1ee9': b'\xe2\xbd', # LATIN SMALL LETTER U WITH HORN AND ACUTE
    '\u1eea': b'\xe1\xad', # LATIN CAPITAL LETTER U WITH HORN AND GRAVE
    '\u1eeb': b'\xe1\xbd', # LATIN SMALL LETTER U WITH HORN AND GRAVE
    '\u1eec': b'\xe0\xad', # LATIN CAPITAL LETTER U WITH HORN AND HOOK ABOVE
    '\u1eed': b'\xe0\xbd', # LATIN SMALL LETTER U WITH HORN AND HOOK ABOVE
    '\u1eee': b'\xe4\xad', # LATIN CAPITAL LETTER U WITH HORN AND TILDE
    '\u1eef': b'\xe4\xbd', # LATIN SMALL LETTER U WITH HORN AND TILDE
    '\u1ef0': b'\xf2\xad', # LATIN CAPITAL LETTER U WITH HORN AND DOT BELOW
    '\u1ef1': b'\xf2\xbd', # LATIN SMALL LETTER U WITH HORN AND DOT BELOW
    '\u1ef2': b'\xe1Y', # LATIN CAPITAL LETTER Y WITH GRAVE
    '\u1ef3': b'\xe1y', # LATIN SMALL LETTER Y WITH GRAVE
    '\u1ef4': b'\xf2Y', # LATIN CAPITAL LETTER Y WITH DOT BELOW
    '\u1ef5': b'\xf2y', # LATIN SMALL LETTER Y WITH DOT BELOW
    '\u1ef6': b'\xe0Y', # LATIN CAPITAL LETTER Y WITH HOOK ABOVE
    '\u1ef7': b'\xe0y', # LATIN SMALL LETTER Y WITH HOOK ABOVE
    '\u1ef8': b'\xe4Y', # LATIN CAPITAL LETTER Y WITH TILDE
    '\u1ef9': b'\xe4y', # LATIN SMALL LETTER Y WITH TILDE
    '\u1fef': b'`', # GREEK VARIA
    '\u200c': b'\x8e', # ZERO WIDTH NON-JOINER
    '\u200d': b'\x8d', # ZERO WIDTH JOINER
    '\u20ac': b'\xc8', # EURO SIGN
    '\u2113': b'\xc1', # SCRIPT SMALL L
    '\u2117': b'\xc2', # SOUND RECORDING COPYRIGHT
    #u'\u212a': b'K', # KELVIN SIGN
    '\u212b': b'\xeaA', # ANGSTROM SIGN
    '\u266d': b'\xa9', # MUSIC FLAT SIGN
    '\u266f': b'\xc4', # MUSIC SHARP SIGN
}

charmap = {}
for uni, char in getattr(unicodemap, "iteritems", unicodemap.items)():
    if char in charmap:
        continue
    charmap[char] = uni
