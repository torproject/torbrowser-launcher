#!/bin/sh

VERSION=`cat share/torbrowser-launcher/version`

# clean up from last build
rm -r build dist

# build binary package
python setup.py bdist_rpm --requires="python-twisted, gnupg, fakeroot, pygtk2, python2-gpg"

# install it
echo ""
echo "To install, run:"
if [ -n "$(lsb_release -si | grep -i blackPanther)" ];then
echo "installing dist/torbrowser-launcher-$VERSION-1.noarch.rpm"
else
echo "sudo dnf install dist/torbrowser-launcher-$VERSION-1.noarch.rpm"
fi