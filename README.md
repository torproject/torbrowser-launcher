Tor Browser Launcher
====================
Tor Browser Launcher is intended to make the Tor Browser Bundle (TBB) easier to
maintain and use for GNU/Linux users. You install ```torbrowser-launcher``` from your
distribution's package manager and it handles everything else, including:

* Downloading the most recent version of TBB for you, in your language and for
  your architecture
* Automatically updating (while preserving your bookmarks and preferences)
* Verifying the TBB's [GnuPG signature](http://www.gnupg.org/gph/en/manual/x135.html)
* Adding a "Tor Browser" application launcher to your desktop environment's menu

When you first launch Tor Browser Launcher, it will download TBB from
https://www.torproject.org/ and extract it in ```~/.torproject```, and then execute
it. When you run it after that it will just execute TBB.

Building a Debian package
=========================

Dependencies
------------

You need to have ```stdeb``` installed. If you're using Debian or Ubuntu you can
install it like this:

    apt-get install python-stdeb

Also install the ```torbrowser-launcher``` dependencies:

    apt-get install python-gtk2 python-psutil python-twisted wmctrl gnupg

Building and Installing
-----------------------

If you're using a Debian-based distribution, you can build a ```.deb``` and install it
in one step by running:

    ./build_and_install.sh

To build a Debian source package:

    python setup.py --command-packages=stdeb.command sdist_dsc

To build a Debian binary package:

    python setup.py --command-packages=stdeb.command bdist_deb

Once you've made a ```.deb```, you can install by running this as root:

    dpkg -i deb_dist/torbrowser-launcher_VERSION_all.deb
