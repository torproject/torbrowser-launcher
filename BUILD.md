# Building Tor Browser Launcher

First, clone the repository:

```sh
git clone https://github.com/micahflee/torbrowser-launcher.git
cd torbrowser-launcher
```

Then install dependencies, build a package, and install:

### Debian, Ubuntu, Linux Mint, etc.

```sh
sudo apt install build-essential dh-python python3-all python3-stdeb python3-pyqt5 python3-gpg python3-requests python3-socks gnupg2 tor
./build_deb.sh
sudo dpkg -i deb_dist/torbrowser-launcher_*.deb
```

### Red Hat, Fedora, CentOS, etc.

```sh
sudo dnf install rpm-build python3-qt5 python3-gpg python3-requests python3-pysocks gnupg2 tor
./build_rpm.sh
sudo yum install dist/torbrowser-launcher-*.rpm
```

### Run without installing

Install the dependencies: sadly, not all of them are available in virtualenv, so you will need to install (some of) them system-wide.
Then, you can run: `TBL_SHARE=share ./torbrowser-launcher`
