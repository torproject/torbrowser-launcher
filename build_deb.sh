#!/bin/sh

VERSION=`cat share/torbrowser-launcher/version`

# clean up from last build
if [ -d "build" ]
then
    rm -r build
fi

if [ -d "deb_dist" ]
then
    rm -r deb_dist
fi

# build binary package
python3 setup.py --command-packages=stdeb.command bdist_deb

# install it
echo ""
echo "To install, run:"
echo "sudo dpkg -i deb_dist/torbrowser-launcher_$VERSION-1_all.deb"
