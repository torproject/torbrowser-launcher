#!/bin/sh

# to clean up from last time, run this:
# rm -rf ~/.torbrowser

# clean up from last build
rm -r deb_dist

# build binary package
python setup.py --command-packages=stdeb.command bdist_deb

# install it
sudo dpkg -i deb_dist/torbrowser-launcher_0.0.2-1_all.deb

