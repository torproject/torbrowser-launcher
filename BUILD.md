# Building Tor Browser Launcher

First, clone the repository:

```sh
git clone https://github.com/micahflee/torbrowser-launcher.git
cd torbrowser-launcher
```

Then install dependencies, build a package, and install:

### Debian, Ubuntu, Linux Mint, etc.

```sh
sudo apt-get install build-essential dh-python python-all python-stdeb python-gtk2 python-twisted python-lzma python-txsocksx gnupg fakeroot xz-utils tor
# If you're running an OS that has python-gpg like Ubuntu 17.04+ or Debian 9+, install that too
sudo apt install python-gpg
./build_deb.sh
sudo dpkg -i deb_dist/torbrowser-launcher_*.deb
```

Optionally you can install `python-pygame` if you want to play a modem sound while Tor Browser is launching.

### Red Hat, Fedora, CentOS, etc.

```sh
sudo dnf install python-psutil python-twisted gnupg fakeroot rpm-build python-txsocksx tor pygtk2 python2-gpg
./build_rpm.sh
sudo yum install dist/torbrowser-launcher-*.rpm
```

Optionally you can install `pygame` if you want to play a modem sound while Tor Browser is launching.

### Run without installing

Install the dependencies: sadly, not all of them are available in virtualenv, so you will need to install (some of) them system-wide.
Then, you can run: `TBL_SHARE=share ./torbrowser-launcher`
