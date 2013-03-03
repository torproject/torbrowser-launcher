#!/bin/sh

# clean up from last time
rm -rf ~/.torbrowser

# build binary package
python setup.py --command-packages=stdeb.command bdist_deb

# install it
sudo dpkg -i deb_dist/torbrowser-launcher_0.1-1_all.deb

