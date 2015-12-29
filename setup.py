#!/usr/bin/env python3.4
"""Setup script for slatium"""
# System
import os
import setuptools

# Local
from slatium import __project__, __version__, CLI, MAIN, DESCRIPTION


# TODO: Test this
if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ''  # a placeholder, readme is generated on release


# TODO: Test this
if os.path.exists('CHANGES.rst'):
    CHANGES = open('CHANGES.rst').read()
else:
    CHANGES = ''  # a placeholder, changelog is generated on release


setuptools.setup(
    name=__project__,
    version=__version__,

    description=DESCRIPTION,
    url='https://github.com/CptSpaceToaster/' + CLI,
    author='CptSpaceToaster',
    author_email='cptspacetoaster@gmail.com',

    packages=setuptools.find_packages(),

    entry_points={
        'console_scripts': [CLI + ' = ' + MAIN]
    },

    long_description=(README + '\n' + CHANGES),
    license='WTFPL',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: Freely Distributable',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Communications :: Chat',
    ],

    install_requires=[
        # 'natsort >= 4.0.3',
        # 'pillow >= 3.0.0',
        # 'numpy >= 1.10.1',
    ],
)
