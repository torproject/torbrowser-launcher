#!/usr/bin/env python

"""
Setup script for the Parsley distribution.
"""

from distutils.core import setup
setup(
    name="Parsley",
    version="1.1",
    url="http://launchpad.net/parsley",
    description="Parsing and pattern matching made easy.",
    author="Allen Short",
    author_email="washort42@gmail.com",
    license="MIT License",
    long_description=open("README").read(),
    packages=["ometa", "terml", "ometa._generated", "terml._generated",
              "ometa.test", "terml.test"],
    py_modules=["parsley"]
)
