#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name          = 'devhgcaltruth',
    version       = '0.2',
    license       = 'BSD 3-Clause License',
    description   = 'Description text',
    url           = 'https://github.com/tklijnsma/devhgcaltruth.git',
    author        = 'Thomas Klijnsma',
    author_email  = 'tklijnsm@gmail.com',
    packages      = ['devhgcaltruth'],
    zip_safe      = False,
    scripts       = [],
    install_requires=[
        'uptools',
        'matplotlib',
        'uptools',
        'tqdm',
        'numba',
        ],
    )