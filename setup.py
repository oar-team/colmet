#!/usr/bin/env python
# *-* coding: utf-8 *-*
import re
import os.path as op
import os
from setuptools import setup, find_packages
from setuptools.command.install import install


here = op.abspath(op.dirname(__file__))


requirements = [
    'tables',
    'pyinotify',
    'pyzmq',
    'requests',
]


def read(fname):
    ''' Return the file content. '''
    with open(op.join(here, fname)) as fd:
        return fd.read()


def get_version():
    return re.compile(r".*__version__ = '(.*?)'", re.S)\
             .match(read(op.join(here, 'colmet', '__init__.py'))).group(1)


def install_c_libs():
    print("installing perfwh C library")
    os.system("make -C ./colmet/node/backends/lib_perf_hw/")
    print("installing RAPL C library")
    os.system("make -C ./colmet/node/backends/lib_rapl/")


class CustomInstall(install):
    def run(self):
        install.run(self)
        # Should be installed manually as the libs should match the target system
        #install_c_libs()


setup(
    name="colmet",
    version=get_version(),
    description=("A utility to monitor the jobs ressources in a HPC"
                 " environment, espacially OAR"),
    keywords="monitoring, taskstat, oar, hpc, sciences",
    maintainer='Salem Harrache',
    maintainer_email='salem.harrache@inria.fr',
    author="Philippe Le Brouster, Olivier Richard",
    author_email="philippe.le-brouster@imag.fr, olivier.richard@imag.fr",
    url="http://oar.imag.fr/",
    packages=find_packages(),
    long_description=read('README.md') + '\n\n' + read('CHANGES'),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    platforms=['Linux'],
    license="GNU GPL",
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
        'Programming Language :: Python :: 3.5'
    ],
    cmdclass={'install': CustomInstall}
)
