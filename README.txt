================
smc.bibencodings
================

ISO-5426 (MAB2) and MARC (USMARC, ANSEL) encodings for Python. The encodings
are used in bibliographic information systems and Z.3950 interfaces of OPACs.


Background
==========

ISO-5426 and USMARC encodings are historic encodings that are still in use by
bibliographic information systems. They are extensions to Latin codec family
and implement a variable length encoding someward similar to UTF-8 and
decomposed unicode (NFD) forms.

Non-ASCII chars are expressed as combining chars. For example umlaut a (LATIN
SMALL LETTER U WITH DIAERESIS) is written in MAB2 encoding as '\xc8u', where
'\xc8' is the sign for combining diaeresis. Contrary to unicode the combining
chars are writte as prefix while unicode has combinig suffixes.

Both MAB2 and MARC encoding support up to two combining chars in front of a
letter, for example '\xc5\xc8u' for LATIN SMALL LETTER U WITH DIAERESIS
AND MACRON.

smc.bibencodings implements small deviations from the standards as it supports
all chars from 0x00 to 0x7e as well as more combining chars. The code has been
tested against several German and Swiss OPACs.


Usage
=====

You just have to import "smc.bibencodings" somehwere in your code to enable
the codecs

iso-5426, iso5426, mab2::
  standard ISO-5426 encoding

iso-5426-xe0, iso5426-xe0, mab2-xe0::
  special ISO-5426 encoding with special identity mapping for 0xa4, 0xe0-0xff

marc, usmarc, ansel::
  MARC encoding

>>> import smc.bibencodings
>>> b"Abr\xc2eg\xc2e Historique De L'Origine".decode("mab2")
"Abrégé Historique De L'Origine"


Data source
===========

The encoding tables are extracted from Thomas Berger's excellent page
http://www.gymel.com/charsets/chartab.html and linked pages. Thank you
very much!


Authors
=======

Christian Heimes


Copyright
=========
 
Copyright (C) 2008-2012 semantics GmbH. All Rights Reserved.::

  semantics
  Kommunikationsmanagement GmbH
  Viktoriaallee 45
  D-52066 Aachen
  Germany

  Tel.: +49 241 89 49 89 29
  eMail: info(at)semantics.de
  http://www.semantics.de/
