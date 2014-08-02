# Tor Browser Launcher

Tor Browser Launcher is intended to make the Tor Browser Bundle (TBB) easier to maintain and use for GNU/Linux users. You install ```torbrowser-launcher``` from your distribution's package manager and it handles everything else, including:

* Downloading the most recent version of TBB for you, in your language and for your architecture
* Automatically updating (while preserving your bookmarks and preferences)
* Verifying the TBB's [GnuPG signature](http://www.gnupg.org/gph/en/manual/x135.html)
* Includes AppArmor profiles to make a Tor Browser compromise not as bad
* Adding a "Tor Browser" application launcher to your desktop environment's menu
* Optionally playing a modem sound when you open Tor Browser (because Tor is so slow)

If you use Ubuntu, you can install it now from my PPA (see "Installing in Ubuntu" below). Tor Browser Launcher will be included in the main Ubuntu repository in 14.10, and is included is Debian Jessie. To install it in any other distribution, see the [build instructions](/BUILD.md).

You might want to check out the [security design doc](/security_design.md).

## Installing in Ubuntu

I've created a PPA where I'm maintaining torbrowser-launcher binaries. You can install in an Ubuntu-based distribution like this:

    sudo add-apt-repository ppa:micahflee/ppa
    sudo apt-get update
    sudo apt-get install torbrowser-launcher

