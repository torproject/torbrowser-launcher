#!/bin/sh

# This script pushes updates to my Ubuntu PPA: https://launchpad.net/~micahflee/+archive/ppa
# If you want to use it, you'll need your own ~/.dput.cf and ssh key.
# More info: https://help.launchpad.net/Packaging/PPA/Uploading

VERSION=`cat version`

rm -rf deb_dist
python setup.py --command-packages=stdeb.command sdist_dsc
cd deb_dist/torbrowser-launcher-$VERSION
dpkg-buildpackage -S
cd ..
dput ppa:micahflee/ppa torbrowser-launcher_$VERSION-1_source.change
cd ..
