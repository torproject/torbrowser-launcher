#!/bin/sh

VERSION=`cat share/torbrowser-launcher/version`

# clean up from last build
rm -r build deb_dist

# build binary package
python3 setup.py --command-packages=stdeb.command bdist_deb

# install it
echo ""
echo "To install, run:"
echo "sudo dpkg -i deb_dist/torbrowser-launcher_$VERSION-1_all.deb"
