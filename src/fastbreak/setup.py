##############################################################################
#
# Copyright (c) 2011 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os
import sys

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    README = ''
    CHANGES = ''

requires = [
    'waitress',
    'pyramid_tm',
    'substanced'
]

if sys.version_info < (2, 6, 0):
    requires.append('simplejson')

setupkw = dict(
    name='fastbreak',
    version='0.0.0',
    description='Software for managing youth sports leagues',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
    ],
    keywords='sports league',
    author="Paul Everitt, Agendaless Consulting",
    author_email="pauleveritt@me.com",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=requires,
    install_requires=requires,
    test_suite="fastbreak",
    entry_points="""\
      [console_scripts]
      populate = fastbreak.populate:main
      """
)

setup(**setupkw)
