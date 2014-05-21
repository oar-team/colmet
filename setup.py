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

import os.path as op
from setuptools import setup, find_packages
from colmet import VERSION

here = op.abspath(op.dirname(__file__))


def read(fname):
    ''' Return the file content. '''
    with open(op.join(here, fname)) as f:
        return f.read()


setup(
    name="colmet",
    version=VERSION.strip('-dev'),
    description=("A utility to monitor the jobs ressources in a HPC"
                 " environment, espacially OAR"),
    keywords="monitoring, taskstat, oar, hpc, sciences",
    maintainer='Salem Harrache',
    maintainer_email='salem.harrache@inria.fr',
    author="Philippe Le Brouster, Olivier Richard",
    author_email="philippe.le-brouster@imag.fr, olivier.richard@imag.fr",
    url="http://oar.imag.fr/",
    packages=find_packages(),
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    install_requires=read('requirements.txt').splitlines(),
    platforms=['Linux'],
    license="GNU GPL",
    tests_require=['nose>=1.0'],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'colmet-node = colmet.node.main:main',
            'colmet-collector = colmet.collector.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Clustering',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
)
