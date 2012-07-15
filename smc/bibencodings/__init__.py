# -*- coding: utf-8 -*-
#=============================================================================
# Copyright   : (c)2010 semantics GmbH
# Rep./File   : $URL$
# Date        : $Date$
# Author      : Christian Heimes
# License     : BSD LICENSE
# Worker      : $Author$
# Revision    : $Rev$
# Purpose     : bibliographic encodings
#=============================================================================
"""bibliographic encodings
"""
import codecs
from smc.bibencodings import iso5426
from smc.bibencodings import marc


def search_func(encoding):
    if encoding in set(['iso-5426', 'iso5426', 'mab2']):
        return iso5426.codecInfo
    if encoding in set(['iso-5426-xe0', 'iso5426-xe0', 'mab2-xe0']):
        return iso5426.specialXE0CodecInfo
    if encoding in set(["marc", "usmarc", "ansel"]):
        return marc.codecInfo

codecs.register(search_func)
