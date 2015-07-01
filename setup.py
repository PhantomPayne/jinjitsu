#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'jinja2',
]

test_requirements = [
    'py.test',
    'tox'
]

setup(
    name='jinjitsu',
    version='0.1.0',
    description="A set of jinja extensions that'll help you write templates at lightning speeds.",
    long_description=readme + '\n\n' + history,
    author='Thomas',
    author_email='tpayne.code@gmail.com',
    url='https://github.com/PhantomPayne/jinjitsu',
    packages=[
        'jinjitsu',
    ],
    package_dir={'jinjitsu':
                 'jinjitsu'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='jinjitsu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)