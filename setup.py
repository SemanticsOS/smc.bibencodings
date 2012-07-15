#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#=============================================================================
# Copyright   : (c) 2008-2012 semantics GmbH. All Rights Reserved.
# Rep./File   : $URL$
# Date        : $Date$
# Author      : Christian Heimes
# License     : BSD LICENSE
# Worker      : $Author$
# Revision    : $Rev$
# Purpose     : distutils setup routines
#=============================================================================
try:
    import setuptools
except ImportError:
    from distutils.core import setup
else:
    from setuptools import setup

setup_info = dict(
    name="smc.bibencodings",
    version="0.1",
    #setup_requires=["setuptools>=0.6c11"],
    packages=["smc.bibencodings"],
    namespace_packages=["smc"],
    zip_safe=True,
    author="semantics GmbH / Christian Heimes",
    author_email="c.heimes@semantics.de",
    maintainer="Christian Heimes",
    maintainer_email="c.heimes@semantics.de",
    url="https://bitbucket.org/tiran/smc.bibencodings",
    keywords="encoding codec bibliographic opac mab2 iso-5426 marc ansel",
    license="BSD",
    description="",
    long_description=open("README.txt").read(),
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ),
)

setup(**setup_info)

