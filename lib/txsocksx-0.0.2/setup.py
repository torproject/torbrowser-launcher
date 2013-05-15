#!/usr/bin/env python
from setuptools import setup
setup(name='txsocksx',
    version='0.0.2',
    packages=['txsocksx'],
    install_requires=[
        "parsley",
        "Twisted>=12.0"
    ]
)
