#!/bin/sh
# Make a signed git tag for the current commit, for a new release
set -e
VERSION=$(cat share/torbrowser-launcher/version)
git tag -s --message="torbrowser-launcher version $VERSION" v$VERSION
echo "Created git tag v$VERSION"
