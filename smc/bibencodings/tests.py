# -*- coding: utf-8 -*-
#=============================================================================
# Copyright   : (c)2010-2012 semantics GmbH
# Rep./File   : $URL$
# Date        : $Date$
# Author      : Christian Heimes
# License     : BSD LICENSE
# Worker      : $Author$
# Revision    : $Rev$
# Purpose     : smc.bibencodings unit testss
#=============================================================================
from __future__ import unicode_literals, print_function
import os
try:
    import unittest2
except ImportError:
    import unittest as unittest2
from glob import glob
from smc.bibencodings import iso5426
from smc.bibencodings import marc
from smc.bibencodings.utils import DecodeIterator

HERE = os.path.dirname(os.path.abspath(__file__))
TESTMABS = glob(os.path.join(HERE, "testdata", "record_?.mab"))
try:
    unicode
except NameError:
    unicode = str


class TestBibencodingUtils(unittest2.TestCase):
    def test_decodeiterator(self):
        di = DecodeIterator("")
        self.assertEqual(len(di), 0)
        self.assertEqual(list(di), [])

        di = DecodeIterator("abc")
        self.assertEqual(len(di), 3)
        self.assertEqual(list(di), ['a', 'b', 'c'])
        #self.assertEqual(di[1:3], "bc")

        di = DecodeIterator("abc")
        it = iter(di)
        self.assertEqual(di.position, 0)
        self.assertEqual(next(it), "a")
        self.assertEqual(di.peek(1), ["b"])
        self.assertEqual(di.peek(2), ["b", "c"])
        self.assertEqual(di.peek(3), ["b", "c", None])
        self.assertEqual(next(it), "b")
        self.assertEqual(di.peek(2), ["c", None])
        self.assertEqual(next(it), "c")
        self.assertEqual(di.position, 2)
        self.assertEqual(di.peek(2), [None, None])
        self.assertRaises(StopIteration, next, it)
        self.assertEqual(di.peek(2), [None, None])
        self.assertEqual(di.position, 3)

        di = DecodeIterator("abc")
        it = iter(di)
        self.assertEqual(next(it), "a")
        di.evolve(1)
        self.assertEqual(next(it), "c")
        di.evolve(1)


class Testiso5426(unittest2.TestCase):

    def assertIso5426(self, b, u):
        self.assertIsInstance(b, bytes)
        self.assertIsInstance(u, unicode)
        self.assertEqual(b.decode("iso-5426"), u)
        self.assertEqual(u.encode("iso-5426"), b)

    def test_iso5426(self):
        s = "abcdefgäöüậ"
        self.assertEqual(s.encode("iso-5426"), b'abcdefg\xc8a\xc8o\xc8u\xc3\xd6a')
        self.assertEqual(b'abcdefg\xc9a\xc9o\xc9u\xc3\xd6a'.decode("iso-5426"), s)
        self.assertEqual(b'abcdefg\xc8a\xc8o\xc8u\xc3\xd6a'.decode("iso-5426"), s)
        self.assertEqual(s.encode("iso-5426").decode("iso-5426"), s)
        self.assertEqual(b"\xc6m".decode("iso-5426"), "m\u0306")
        self.assertEqual("\u01e0".encode("iso-5426"), b"\xc5\xc7A")
        self.assertEqual(b"\xc5\xc7A".decode("iso-5426"), "\u01e0")
        self.assertEqual(b"\xca\x1e".decode("iso-5426"), "\x1e\u030a")
        for c, uc in iso5426.charmap.items():
            self.assertEqual(uc.encode("iso-5426"), c)
            self.assertEqual(c.decode("iso-5426"), uc)
        for mab in TESTMABS:
            with open(mab, "rb") as f:
                f.read().decode("iso-5426")

        self.assertRaises(UnicodeError, "Ф".encode, "iso-5426")
        self.assertRaises(ValueError, "Ф".encode, "iso-5426", "invalid")
        self.assertEqual("Ф".encode("iso-5426", "ignore"), b"")
        self.assertEqual("Ф".encode("iso-5426", "replace"), b"?")

        self.assertRaises(UnicodeError, b"\xff".decode, "iso-5426")
        self.assertRaises(ValueError, b"\xff".decode, "iso-5426", "invalid")
        self.assertEqual(b"\xff".decode("iso-5426", "ignore"), "")
        self.assertEqual(b"\xff".decode("iso-5426", "replace"), '\ufffd')
        self.assertEqual(b"\xff".decode("iso-5426", "repr"), '\\xff')

        self.assertEqual(b"Benk\xcd\xc9o".decode("mab2"), "Benkö\u030b")
        self.assertIso5426(b"Benk\xcd\xc8o", "Benkö\u030b")
        self.assertIso5426(b"Benk\xc8\xcdo", "Benk\u0151\u0308")
        self.assertIso5426(b"Abr\xc2eg\xc2e Historique De L'Origine",
                           "Abrégé Historique De L'Origine")
        self.assertIso5426(b'\xca4', '4\u030a')

    def test_iso5426_xe0(self):
        s = "abcdefgäöüậ"
        self.assertEqual(s.encode("iso-5426-xe0"), b'abcdefg\xc8a\xc8o\xc8u\xc3\xd6a')
        self.assertEqual(b'abcdefg\xc9a\xc9o\xc9u\xc3\xd6a'.decode("iso-5426-xe0"), s)
        self.assertEqual(b'abcdefg\xc8a\xc8o\xc8u\xc3\xd6a'.decode("iso-5426-xe0"), s)
        self.assertEqual(s.encode("iso-5426").decode("iso-5426-xe0"), s)
        self.assertEqual(b"gramatica dl ladin de gherd\xebina".decode("iso-5426-xe0"),
                         'gramatica dl ladin de gherdëina')
        self.assertEqual(b"Micur\xe1 de R\xc9u".decode("iso-5426-xe0"),
                         'Micurá de Rü')
        self.assertEqual(b'\xc5\xc8U'.decode("iso-5426-xe0"), '\u01d5')
        self.assertEqual(b'\xc5\xc8o'.decode("iso-5426-xe0"),
                         '\N{LATIN SMALL LETTER O WITH DIAERESIS AND MACRON}')

    def test_unknown_encoding(self):
        self.assertRaises(LookupError, "a".encode, "invalid")


class TestMarc(unittest2.TestCase):

    def test_marc(self):
        s = "abcdefgäöüậ"
        self.assertEqual(s.encode("marc"), b'abcdefg\xe8a\xe8o\xe8u\xe3\xf2a')
        self.assertEqual(b'abcdefg\xe8a\xe8o\xe8u\xe3\xf2a'.decode("marc"), s)
        for c, uc in marc.charmap.items():
            self.assertEqual(uc.encode("marc"), c)
            self.assertEqual(c.decode("marc"), uc)

        self.assertRaises(UnicodeError, "Ф".encode, "marc")
        self.assertRaises(ValueError, "Ф".encode, "marc", "invalid")
        self.assertEqual("Ф".encode("marc", "ignore"), b"")
        self.assertEqual("Ф".encode("marc", "replace"), b"?")

        self.assertRaises(UnicodeError, b"\xff".decode, "marc")
        self.assertRaises(ValueError, b"\xff".decode, "marc", "invalid")
        self.assertEqual(b"\xff".decode("marc", "ignore"), "")
        self.assertEqual(b"\xff".decode("marc", "replace"), '\ufffd')
        self.assertEqual(b"\xff".decode("marc", "repr"), '\\xff')
        self.assertEqual(b'\xe5\xe80'.decode('marc'), '\u0304\u03080')


def test_main():
    suite = unittest2.TestSuite()
    suite.addTest(unittest2.defaultTestLoader.loadTestsFromTestCase(Testiso5426))
    suite.addTest(unittest2.defaultTestLoader.loadTestsFromTestCase(TestMarc))
    suite.addTest(unittest2.defaultTestLoader.loadTestsFromTestCase(TestBibencodingUtils))
    return suite

if __name__ == "__main__": # pragma: no cover
    suite = test_main()
    #suite = unittest2.defaultTestLoader.loadTestsFromTestCase(TestBibencodingUtils)
    unittest2.TextTestRunner(verbosity=2).run(suite)
