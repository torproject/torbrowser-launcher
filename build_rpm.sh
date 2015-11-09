#!/bin/sh

VERSION=`cat share/torbrowser-launcher/version`

# clean up from last build
rm -r build dist

# build binary package
python setup.py bdist_rpm --requires="python-psutil, python-twisted, gnupg, fakeroot, pygtk2"

# install it
echo ""
echo "To install, run:"
echo "sudo yum install dist/torbrowser-launcher-$VERSION-1.noarch.rpm"
