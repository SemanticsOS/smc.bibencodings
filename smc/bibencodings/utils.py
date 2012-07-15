# -*- coding: utf-8 -*-
#=============================================================================
# Copyright   : (c)2010-2012 semantics GmbH
# Rep./File   : $URL$
# Date        : $Date$
# Author      : Christian Heimes
# License     : BSD LICENSE
# Worker      : $Author$
# Revision    : $Rev$
# Purpose     : helper functions
#=============================================================================
"""help functions
"""
from __future__ import unicode_literals, print_function

class DecodeIterator(object):
    """Decoding iterator with peek and evolve
    """

    __slots__ = ("_data", "_length", "_pos")
    def __init__(self, data):
        self._data = data
        self._length = len(data)
        self._pos = 0

    def __iter__(self):
        while True:
            pos = self._pos
            if pos >= self._length:
                raise StopIteration
            yield self._data[pos]
            self._pos += 1

    def __len__(self):
        return self._length

    #def __getitem__(self, item):
    #    return self._data.__getitem__(item)

    @property
    def position(self):
        return self._pos

    def peek(self, amount=2):
        nextpos = self._pos + 1
        result = list(self._data[nextpos:nextpos + amount])
        if len(result) < amount:
            result.extend([None] * (amount - len(result)))
        return result

    def evolve(self, amount=1):
        self._pos += amount

    #def residual(self, amount=1):
    #    return self._length - self._pos > amount
