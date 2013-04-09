#!/bin/sh

# to clean up from last time, run this:
# rm -rf ~/.torbrowser

# build binary package
python setup.py --command-packages=stdeb.command bdist_deb

# install it
sudo dpkg -i deb_dist/torbrowser-launcher_0.1-alpha-1_all.deb

