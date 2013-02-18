#!/bin/sh
# usage: verify.sh [temporary gpg directory] [tor-browser-gnu-linux-xxx.tar.gz.asc]

GPG_TMP_DIR=$1
TBB_SIG=$2

# clean the temp gpg dir
rm -rf $GPG_TMP_DIR
mkdir -p $GPG_TMP_DIR
chmod 700 $GPG_TMP_DIR

# import erinn's public key
gpg --homedir $GPG_TMP_DIR --import /usr/share/torbrowser-launcher/erinn.asc
gpg --homedir $GPG_TMP_DIR --import /usr/share/torbrowser-launcher/sebastian.asc

# verify the signature
gpg --homedir $GPG_TMP_DIR --verify $TBB_SIG
