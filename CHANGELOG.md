# Tor Browser Launcher Changelog

## 0.0.7

* Added AppArmor profiles for torbrowser-launcher and TBB
* Removed included libs in favor of adding new Debian package dependencies

## 0.0.6

* Fixed URLs to deal with changes in TBB releases for 3.x

## 0.0.5

* Updated paths because TBB 3.x changed directory structure
* mirrors.txt now has local version in /usr/local
* Updated TBB signature URL
* Made optional modem sound when launching Tor, because it's sooo slow :)
* Extra check to make sure the latest version is installed
