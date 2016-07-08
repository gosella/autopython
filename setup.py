# -*- coding: utf-8 -*-

import codecs
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from autopython import VERSION

README = os.path.join(os.path.dirname(__file__), 'README.rst')
with codecs.open(README, encoding='utf-8') as readme_file:
    long_description = readme_file.read()

PY_VER = str(sys.version_info[0])

setup(
    name='autopython',
    version=VERSION,
    license='GPLv3',

    description='Autoscripting for Python ' + PY_VER,
    long_description=long_description,

    packages=['autopython'],
    entry_points={
        'console_scripts': [
          'autopython' + PY_VER + ' = autopython.main:autopython',
          'autoipython' + PY_VER + ' = autopython.main:autoipython [ipython]',
        ],
    },

    extras_require={
        'highlighting': ['colorama', 'Pygments>=0.10'],
        'ipython': ['ipython>=1.0']
    },

    url='https://github.com/gosella/autopython',
    download_url='https://github.com/gosella/autopython/tarball/' + VERSION,

    author='Germán Osella Massa',
    author_email='german.osella@nexo.unnoba.edu.ar',
    maintainer='Germán Osella Massa',
    maintainer_email='german.osella@nexo.unnoba.edu.ar',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Education',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],

    keywords=['presentation', 'automatic', 'typing', 'ipython'],
)
