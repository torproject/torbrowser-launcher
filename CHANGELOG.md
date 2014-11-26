# Tor Browser Launcher Changelog

## 0.1.7

* You can now pass URLs into TBL, and set it as your default browser
* Hides TBL window before launching TBB
* Default mirror switched to https://dist.torproject.org/
* Added AppData file to look better in software centers
* Exclude AppArmor profiles in Ubuntu, where they're broken

## 0.1.6

* Updated licensing confusion to just be MIT in all locations
* Fixed bug related to TBB 4.0's new folder structure
* Updated .desktop files to comply with standards

## 0.1.5

* Split source code into several files
* Several AppArmor updates
* Prepare for upcoming RecommendedTBBVersion format change
* More verbose UI when updating
* No longer detaches start-tor-browser as separate process
* Temporarily disable AppArmor profiles in Ubuntu

## 0.1.4

* RecommendedTBBVersion URL change
* Many AppArmor improvements
* Allow installation into a virtualenv

## 0.1.3

* Force installing stable release if available in RecommendedTBBVersions
* Removed Mike Perry's signing key and added Erinn Clark's signing key
* Fixed AppArmor profiles (thanks to troubadoour)

## 0.1.2

* Updated Dutch translation
* Fixed bug with loading mirrors list
* Huge refactor of AppArmor profiles
* Added OnionShare support to AppArmor profiles
* Suppresses output from detached TBB process
* Uses freedesktop xdg-user-dirs instead of ~/.torbrowser
* Removed all signing keys except Mike Perry's
* Made tor and python-txsocksx dependencies to update over Tor by default

## 0.1.1

* Added TBL_SHARE support, to more easily develop without installing systemwide
* Modem sound and python-pygame dependency is now optional
* Support for updating TBB over Tor using a system Tor
* Removed support for stable/alpha preference, forces stable now
* Added French translations

## 0.1.0

* Added Polish translations
* Version 0.1.0 marks first version in Debian!
* Changed GPG release signing key
  from 5C17616361BD9F92422AC08BB4D25A1E99999697
  to 0B1491929806596254700155FD720AD9EBA34B1C

## 0.0.9

* Fixed AppArmor rules that were broken in Ubuntu
* Added support for basic RPM packaging
* Removed un-used dependencies
* Fixed URLs to deal with TBB release filename changes

## 0.0.8

* Removed older code that's no longer used
* Updated list of Tor mirrors
* Replaced certificate for www.torproject.org post-heartbleed
* Fixed URLs to deal with TBB release filename changes

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
