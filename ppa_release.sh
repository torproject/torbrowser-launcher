#!/bin/sh

# This script pushes updates to my Ubuntu PPA: https://launchpad.net/~micahflee/+archive/ppa
# More info: https://help.launchpad.net/Packaging/PPA/Uploading
#
# If you want to use it, you'll need your own ~/.dput.cf. Here's mine:
#
# [ppa]
# fqdn = ppa.launchpad.net
# method = ftp
# incoming = ~micahflee/ubuntu/ppa/
# login = anonymous
# allow_unsigned_uploads = 0

VERSION=`cat share/torbrowser-launcher/version`

# Make a source pacakge
rm -rf deb_dist
python3 setup.py --command-packages=stdeb.command sdist_dsc

# Sign it
cd deb_dist/torbrowser-launcher-$VERSION
dpkg-buildpackage -S
#dpkg-buildpackage -S -pqubes-gpg-client-wrapper -k927F419D7EC82C2F149C1BD1403C2657CD994F73
cd ..

# Push it to the ppa
dput ppa torbrowser-launcher_$VERSION-1_source.changes
cd ..
