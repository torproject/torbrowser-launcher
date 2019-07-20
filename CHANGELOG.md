# Tor Browser Launcher Changelog

## 0.3.2

* Switch to keys.openpgp.org when refreshing signing key, because SKS keyservers are broken
* Use new Tor Browser logo

## 0.3.1

* Ship with latest version of the Tor Browser Developers OpenPGP public key
* Fix bug where TBL window stays open after Tor Browser is launched

## 0.3.0

* Switched from python2 to python3
* Switched from gtk2 to Qt5
* Switched from twisted to requests/socks
* Use QThreads for async
* Removed modem sound
* Only refresh gpg keyring on verification error, instead of every time
* Updated AppArmor profiles
* Updated available languages, and fixed locale detection bug
* Fixed false signature verification error related to twisted

## 0.2.9

* Fixed crash issue related to Tor Browser 7.5 changing how the currently installed version number is stored
* Updated list of Tor Project dist mirrors
* Fixed edge case crash for when stdout isn't writable
* Updated AppStream metadata
* Updated AppArmor profiles

## 0.2.8

* Update URL to check for latest version, which changed in Tor Browser 7
* Automatically refresh GPG keyring, to prevent signature verification false positives
* Improve GnuPG code by using GPGME if available
* Updated AppArmor profiles
* Added Czech, Hungarian localization

## 0.2.7

* Updated Tor Browser signing key because they added a new subkey and verification was failing
* Updated AppArmor profiles
* Improved localization, and added Russian

## 0.2.6

* Fixed bug related to fallback to English feature that caused Settings to crash

## 0.2.5

* Fix issue where Tor Browser Launcher failed to launch if currently installed version of Tor Browser was too old
* If Tor Browser download isn't available in your language, fallback to English
* Avoid re-downloading tarball if it's already present
* Verify GnuPG importing keys using status-fd rather than exit codes
* Various AppArmor improvements
* Removed unused dependency

## 0.2.4

* Fix signature verification bypass attack, reported by Jann Horn (CVE-2016-3180)

## 0.2.3

* Removed certificate pinning to https://www.torproject.org to avoid issues with upcoming certificate change, and hard-coded minimum Tor Browser version in the release
* Fix issue with detecting language
* Make Tor SOCKS5 proxy configurable, for users not running on 9050
* Improved AppArmor profiles
* Added translations
* Switched from xpm icons to png icons
* Changed "Exit" button to "Cancel" button
* New package description

## 0.2.2

* Tor Browser Launcher no longer attempts to auto-update, now that Tor Browser has this feature
* System Tor is now an optional dependency
* Fix issue where downloads fail because of unicode URLs
* Removed window management code that stopped working many releases ago, and removed wmctrl dependency
* Removed test code that caused signature verification to happen at the wrong time

## 0.2.1

* Stop using RecommendedTBBVersions and start using more reliable "release" channel XML
* Converted settings file from pickle format to JSON
* Download tarball signatures to verify, rather than SHA256SUMS and signature
* Implemented IPolicyForHTTPS to prevent twisted-related crashes in Debian
* Some AppArmor fixes

## 0.2.0

* Fix critical bug with new location of start-tor-browser
* Silenced some AppArmor denied events from logs
* Print less console output
* Remove support for accepting links
* Added better support for updating over Tor in Fedora

## 0.1.9

* Added option to disable accepting links, to workaround Firefox/Tor Browser issue

## 0.1.8

* Added new Tor Browser signing key
* Fixed removing alpha/beta code due to change in RecommendedTBBVersions syntax
* Fixed opening links in TBB if you originally opened TBB without clicking a link


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
