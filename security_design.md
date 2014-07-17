# Tor Browser Launcher Security Design

This document could be improved. At the moment it's copy/pasted verbatum from a post to the [debian bug tracker](http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=752275).

## TLS/x.509 security

torbrowser-launcher doesn't rely on the CA infrastructure. The only TLS it does is make HTTPS requests to check.torproject.org and (if you haven't set a mirror) www.torproject.org. When it connects to these hostnames, it uses a hardcoded certificate. So none of the TLS PKI issues apply at all here.

(And I took extra measures to make sure the .pem included with torbrowser-launcher is valid. I downloaded the cert from several different internet connections/ISPs and compared, and when I had one I thought was correct I sought out Tor devs to verify I was including the right one and not a malicious one.)

## Downgrade attacks

Downgrade attacks shouldn't be possible, unless they're committed by Tor devs themselves. If an attacker captures a valid old request to https://check.torproject.org/RecommendedTBBVersions that claims that the current version is an older version than what's currently installed, torbrowser-launcher prevents it from installing. (And by "installing" I mean extracting to the user's home dir.)

However, there is the scenereo where the user has set a third-party mirror to download from instead of the default. The third-party mirror could serve a tarball and sig that have filenames of the latest version, but are actually an older version. This attack is mitigated by the fact that all mirror options use HTTPS -- though none of the mirror certs are pinned, so in this case it would rely on CA infrastructure. This is an edge case, and would only work against users who are using a non-default mirror, and who also have access to a trusted CA signing key.

## Installing Tor Browser system-wide

You cannot install Tor Browser system-wide. It's released by the Tor Project as a bundle. There's a lot of code in there that specifically prevents it from touching any other files outside of it's own directory. All files need to be owned by current user, and it's designed to be runnable off of a USB stick. A long time ago I put a bunch of work into tearing apart the "bundle"-ness of TBB to make it installable systemwide, and concluded it wasn't practical without the Tor devs releasing it as such. If you could install it systemwide, there would be no reason for torbrowser-launcher -- it could then just be a normal debian package.

## What secret keys/access attackers need to succeed

Yes, attackers that 1) have access to the trusted keys included with torbrowser-launcher and 2) have access to modify files on https://www.torproject.org/ or have access to its TLS key are able to get arbitrary code exec as the current user when they open Tor Browser.  This may or may not include any of the Tor devs whose keys are included.

But like Holger said above, this is a feature, not a bug. This is the whole purpose of torbrowser-launcher, so users can automatically install TBB updates that are signed by Tor devs.
