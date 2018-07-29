#!/bin/sh

VERSION=`cat share/torbrowser-launcher/version`

# clean up from last build
rm -r build dist

# build binary package
python3 setup.py bdist_rpm --requires="python3-qt5, python3-gpg, python3-requests, python3-pysocks, gnupg2"

# install it
echo ""
echo "To install, run:"
echo "sudo dnf install dist/torbrowser-launcher-$VERSION-1.noarch.rpm"
