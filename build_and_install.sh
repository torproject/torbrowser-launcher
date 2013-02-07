#!/bin/sh

# clean up from last time
rm -rf ~/.torbrowser

# build source dist
python setup.py sdist

# turn it into a debian source package
cd dist
py2dsc torbrowser-launcher-2.3.25-2-1.tar.gz

# turn it into a debian binary package
cd deb_dist/torbrowser-launcher-2.3.25-2-1
dpkg-buildpackage -rfakeroot -uc -us

# install it
cd ..
sudo dpkg -i python-torbrowser-launcher_2.3.25-2-1-1_all.deb
cd ../..

