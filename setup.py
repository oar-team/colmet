#!/usr/bin/env python
# *-* coding: utf-8 *-*

# Copyright 2012 Philippe Le Brouster <philippe.le-brouster@imag.fr> / LIG
# 
# This file is part of Colmet
# 
# Colmet is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Épeire is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
# 
# You should have received a copy of the GNU Affero Public License
# along with Épeire.  If not, see <http://www.gnu.org/licenses/>.


'''
Colmet Python setup file
'''

import os
#from distutils.core import setup
from setuptools import setup, find_packages
from colmet import VERSION

def read(fname):
    '''
    Return the file content
    '''
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "colmet",
    version = VERSION,
    description = ("A utility to monitor the jobs ressources in a HPC"
                   "environment, espacially OAR"),
    keywords = "monitoring, taskstat, oar, hpc, sciences",
    author = "Philippe Le Brouster, Olivier Richard",
    author_email = "philippe.le-brouster@imag.fr, olivier.richard@imag.fr",
    url = "http://oar.imag.fr/",
    packages= find_packages(),
    long_description=read('README'),
    platforms = ['Linux' ],
    license = "GNU GPL",
    tests_require=['nose>=1.0'],
    test_suite = 'nose.collector',
    entry_points={
        'console_scripts': [
            'colmet = colmet.ui:main'
        ],
    },
)
