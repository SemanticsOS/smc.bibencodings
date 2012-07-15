#!/usr/bin/env python2.7
import lxml.etree
import lxml.html


def parseTables(fname="chartab.html", pos=18):
    # parse http://www.gymel.com/charsets/chartab.html
    tree = lxml.html.parse(fname)
    trs = tree.xpath("//table/tr[td]")
    for tr in trs:
        result = parseLine(tr, pos)
        if result is not None:
            yield result


def parseLine(tr, pos):
    # 17: MAB2, 18: USMARC/ANSEL, 19: PICA
    tds = tr.findall("./td")
    uni = int(tds[0].findall("./small")[-1].text, 16)
    uniname = tds[1].find("a").text
    code = tds[pos].findall("./small")
    code = tuple(int(x) for x in code[-1].text.split(" ")) if code else None
    if code is not None:
        return uni, uniname, "".join(chr(x) for x in code)

for uni, name, bytes in parseTables():
    print u"    u'\\u%04x': %r, # %s" % (uni, bytes, name)
