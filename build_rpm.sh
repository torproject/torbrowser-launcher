#!/bin/sh

VERSION=`cat version`

# clean up from last build
rm -r build dist

# build binary package
python setup.py bdist_rpm --requires="python-psutil, python-twisted, wmctrl, gnupg, fakeroot"

# install it
echo ""
echo "To install, run:"
echo "sudo yum install dist/torbrowser-launcher-$VERSION-1.noarch.rpm"
