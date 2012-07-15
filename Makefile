# -*- coding: utf-8 -*-
#=============================================================================
# Copyright   : (c) 2008-2012 semantics GmbH
# Rep./File   : $URL$
# Date        : $Date$
# Author      : Christian Heimes
# Worker      : $Author$
# Revision    : $Rev$
# Purpose     : Makefile
#=============================================================================

PYTHON=python2.7
SETUPFLAGS=
COMPILEFLAGS=

.PHONY: inplace all rebuild test_inplace test clean realclean egg_info egg 
.PHONY: develop sdist

inplace:
	$(PYTHON) setup.py $(SETUPFLAGS) build_ext -i $(COMPILEFLAGS)

all: inplace

rebuild: clean all

test_inplace: inplace
	$(PYTHON) -m smc.bibencodings.tests

test: test_inplace

clean:
	find . \( -name '*.o' -or -name '*.so' -or -name '*.py[cod]' \) -delete

realclean: clean
	$(PYTHON) setup.py clean -a
	rm -rf build
	rm -rf dist
	rm -f TAGS tags
	rm -rf smc.bibencodings.egg-info

egg_info:
	rm -rf smc.bibencodings.egg-info
	$(PYTHON) setup.py egg_info

egg: egg_info inplace
	$(PYTHON) setup.py bdist_egg

develop: egg_info inplace
	$(PYTHON) setup.py develop

sdist: egg_info
	$(PYTHON) setup.py sdist
 
