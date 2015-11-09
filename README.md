# Tor Browser Launcher

Tor Browser Launcher is intended to make the Tor Browser easier to install and use for GNU/Linux users. You install ```torbrowser-launcher``` from your distribution's package manager and it handles everything else:

* Downloads the most recent version of Tor Browser in your language and for your computer's architecture (Tor Browser will automatically update itself)
* Certificate pins to https://www.torproject.org, so it doesn't rely on certificate authorities
* Verifies Tor Browser's [OpenPGP signature](https://www.torproject.org/docs/verifying-signatures.html.en) for you, to ensure the version you downloaded is not tampered with
* Adds "Tor Browser" and "Tor Browser Launcher Settings" application launcher to your desktop environment's menu
* Includes AppArmor profiles to make a Tor Browser compromise not as bad
* Optionally playing a modem sound when you open Tor Browser (because Tor is so slow)

Tor Browser Launcher is included in Ubuntu, Debian, and Fedora. To install it in any other distribution, see the [build instructions](/BUILD.md).

You might want to check out the [security design doc](/security_design.md).

![Tor Browser Launcher screenshot](/screenshot.png)

# Installing in Ubuntu

If you want to always have the latest version of the `torbrowser-launcher` package before your distribution gets it, you can use my PPA:

```sh
sudo add-apt-repository ppa:micahflee/ppa
sudo apt-get update
sudo apt-get install torbrowser-launcher
```

