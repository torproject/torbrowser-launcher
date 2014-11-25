# Tor Browser Launcher

Tor Browser Launcher is intended to make the Tor Browser Bundle (TBB) easier to maintain and use for GNU/Linux users. You install ```torbrowser-launcher``` from your distribution's package manager and it handles everything else, including:

* Downloading the most recent version of TBB for you, in your language and for your architecture
* Automatically updating (while preserving your bookmarks and preferences)
* Verifying the TBB's [GnuPG signature](http://www.gnupg.org/gph/en/manual/x135.html)
* Includes AppArmor profiles to make a Tor Browser compromise not as bad
* Adding a "Tor Browser" application launcher to your desktop environment's menu, and letting you set Tor Browser as your default browser
* Optionally playing a modem sound when you open Tor Browser (because Tor is so slow)

Tor Browser Launcher is included in Ubuntu 14.10+, Debian 8+, and Fedora 20+. To install it in any other distribution, see the [build instructions](/BUILD.md).

You might want to check out the [security design doc](/security_design.md).

![Tor Browser Launcher screenshot](/screenshot.png)

## Installing in Ubuntu 14.04 and earlier

I've created a PPA where I'm maintaining torbrowser-launcher binaries. You can install in an Ubuntu-based distribution like this:

    sudo add-apt-repository ppa:micahflee/ppa
    sudo apt-get update
    sudo apt-get install torbrowser-launcher

