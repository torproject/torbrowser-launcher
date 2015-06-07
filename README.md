# Tor Browser Launcher

Tor Browser Launcher is intended to make the Tor Browser Bundle (TBB) easier to maintain and use for GNU/Linux users. You install ```torbrowser-launcher``` from your distribution's package manager and it handles everything else, including:

* Downloading the most recent version of TBB for you, in your language and for your architecture
* Automatically updating (not preserving your bookmarks and preferences)
* Verifying the TBB's [GnuPG signature](http://www.gnupg.org/gph/en/manual/x135.html)
* Includes AppArmor profiles to make a Tor Browser compromise not as bad
* Adding a "Tor Browser" application launcher to your desktop environment's menu
* Optionally playing a modem sound when you open Tor Browser (because Tor is so slow)

Tor Browser Launcher is included in Ubuntu 14.10+, Debian 8+, and Fedora 20+. To install it in any other distribution, see the [build instructions](/BUILD.md).

You might want to check out the [security design doc](/security_design.md).

![Tor Browser Launcher screenshot](/screenshot.png)

## Using Tor Browser as your default browser, and Firefox

Tor Browser Launcher allows you to set Tor Browser as your default web browser. Unfortunately, there's a gnarly issue that prevents this from working if Firefox is open in the background. If Tor Browser is set as your default browser and Firefox is open in the background, links will get opened in Firefox. Likewise, if Firefox is your default browser and Tor Browser is open in the background, links will get opened in Tor Browser. See more information [here](https://github.com/micahflee/torbrowser-launcher/issues/157).

You can only use Tor Browser as your default browser if you don't use Firefox at the same time. Other browser (such as Iceweasel, Chromium, or Chrome) will work fine. You must check "Allow opening links with Tor Browser" in the settings to enable it.

## Installing in Ubuntu 14.04 and later

I've created a PPA where I'm maintaining torbrowser-launcher binaries. You can install in an Ubuntu-based distribution like this:

```sh
sudo add-apt-repository ppa:micahflee/ppa
sudo apt-get update
sudo apt-get install torbrowser-launcher
```

