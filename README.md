# Tor Browser Launcher

_**Are you getting an error?** Sometimes updates in Tor Browser itself will break Tor Browser Launcher. There's a good chance that the problem you're experiencing has already been fixed in the [newest version](https://github.com/micahflee/torbrowser-launcher/releases). Try installing from Flatpak (instructions below), or [build from source](/BUILD.md)._

Tor Browser Launcher is intended to make Tor Browser easier to install and use for GNU/Linux users. You install ```torbrowser-launcher``` from your distribution's package manager and it handles everything else:

* Downloads and installs the most recent version of Tor Browser in your language and for your computer's architecture, or launches Tor Browser if it's already installed (Tor Browser will automatically update itself)
* Verifies Tor Browser's [signature](https://www.torproject.org/docs/verifying-signatures.html.en) for you, to ensure the version you downloaded was cryptographically signed by Tor developers and was not tampered with
* Adds "Tor Browser" and "Tor Browser Launcher Settings" application launcher to your desktop environment's menu
* Includes AppArmor profiles to make a Tor Browser compromise not as bad
* Optionally plays a modem sound when you open Tor Browser (because Tor is so slow)

Tor Browser Launcher is included in Ubuntu, Debian, and Fedora. To install it in any other distribution, see the [build instructions](/BUILD.md).

You might want to check out the [security design doc](/security_design.md).

![Tor Browser Launcher screenshot](/screenshot.png)

# Installing

You can install `torbrowser-launcher` from your operating system's package manager, but it might be out-of-date and have issues working. If you want to make sure you always have the latest version, use one of the methods below to install:

## Installing in any Linux distro using Flatpak

Install Flatpak using these [instructions](https://flatpak.org/setup/).

Then install `torbrowser-launcher` like this:

```
flatpak install flathub com.github.micahflee.torbrowser-launcher -y
```

Run `torbrowser-launcher` either by using the GUI desktop launcher, or by running:

```
flatpak run com.github.micahflee.torbrowser-launcher
```

## Installing from the PPA

If you use Ubuntu or one of its derivatives:

```sh
sudo add-apt-repository ppa:micahflee/ppa
sudo apt update
sudo apt install torbrowser-launcher
```

Run `torbrowser-launcher` either by using the GUI desktop launcher, or by running:

```
torbrowser-launcher
```