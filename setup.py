"""
Tor Browser Launcher
https://github.com/micahflee/torbrowser-launcher/

Copyright (c) 2013-2014 Micah Lee <micah@micahflee.com>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

from distutils.core import setup
import os, sys, platform
SHARE = 'share'

# detect linux distribution
distro = platform.dist()[0]

def file_list(path):
    files = []
    for filename in os.listdir(path):
        if os.path.isfile(path+'/'+filename):
            files.append(path+'/'+filename)
    return files

with open(os.path.join(SHARE, 'torbrowser-launcher/version')) as buf:
    version = buf.read().strip()

datafiles = []
for root, dirs, files in os.walk(SHARE):
    datafiles.append((os.path.join(sys.prefix, root),
                      [os.path.join(root, f) for f in files]))

# disable shipping apparmor profiles until they work in ubuntu (#128)
if distro != 'Ubuntu':
    if not hasattr(sys, 'real_prefix'):
        # we're not in a virtualenv, so we can probably write to /etc
        datafiles += [('/etc/apparmor.d/', [
            'apparmor/torbrowser.Browser.firefox',
            'apparmor/torbrowser.start-tor-browser',
            'apparmor/torbrowser.Tor.tor',
            'apparmor/usr.bin.torbrowser-launcher'])]

setup(
    name='torbrowser-launcher',
    version=version,
    author='Micah Lee',
    author_email='micah@micahflee.com',
    url='https://www.github.com/micahflee/torbrowser-launcher',
    platforms=['GNU/Linux'],
    license='MIT',
    description='A program to help you download, keep updated, and run the Tor Browser Bundle',
    long_description="""
Tor Browser Launcher is intended to make the Tor Browser Bundle (TBB) easier to maintain and use for GNU/Linux users. You install torbrowser-launcher from your distribution's package manager and it handles downloading the most recent version of TBB for you, in your language and for your architecture. It also adds a "Tor Browser" application launcher to your operating system's menu, and lets you set Tor Browser as your default web browser.

When you first launch Tor Browser Launcher, it will download TBB from https://www.torproject.org/, extract it in your home directory, and execute it. When you run it after that it will just execute TBB. When you open Tor Browser after an update, it will download the newer version of TBB for you and extract it over your old TBB directory, so you will maintain your TBB bookmarks and always be running the latest version.
""",
    packages=['torbrowser_launcher'],
    scripts=['torbrowser-launcher'],
    data_files=datafiles
)

