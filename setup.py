"""
Tor Browser Launcher
https://github.com/micahflee/torbrowser-launcher/

Copyright (c) 2013-2017 Micah Lee <micah@micahflee.com>

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

import os
import sys
import platform
import subprocess
from distutils.core import setup

SHARE = 'share'

# detect linux distribution
distro = platform.dist()[0]


def file_list(path):
    files = []
    for filename in os.listdir(path):
        if os.path.isfile(path+'/'+filename):
            files.append(path+'/'+filename)
    return files


def create_mo_files():
    po_dir = 'po/'
    if not os.path.exists(po_dir):
        return []
    domain = 'torbrowser-launcher'
    mo_files = []
    po_files = [f
                for f in next(os.walk(po_dir))[2]
                if os.path.splitext(f)[1] == '.po']
    for po_file in po_files:
        filename, extension = os.path.splitext(po_file)
        mo_file = domain + '.mo'
        mo_dir = 'share/locale/' + filename + '/LC_MESSAGES/'
        subprocess.call('mkdir -p ' + mo_dir, shell=True)
        msgfmt_cmd = 'msgfmt {} -o {}'.format(po_dir + po_file, mo_dir + mo_file)
        subprocess.call(msgfmt_cmd, shell=True)
        mo_files.append(mo_dir + mo_file)
    return mo_files


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
        datafiles += [
            ('/etc/apparmor.d/', [
                'apparmor/torbrowser.Browser.firefox',
                'apparmor/torbrowser.Browser.plugin-container',
                'apparmor/torbrowser.Tor.tor']),
            ('/etc/apparmor.d/local/', [
                'apparmor/local/torbrowser.Browser.firefox',
                'apparmor/local/torbrowser.Browser.plugin-container',
                'apparmor/local/torbrowser.Tor.tor']),
            ('/etc/apparmor.d/tunables/', ['apparmor/tunables/torbrowser'])
        ]

datafiles += [('/usr/share/locale/', create_mo_files())]

setup(
    name='torbrowser-launcher',
    version=version,
    author='Micah Lee',
    author_email='micah@micahflee.com',
    url='https://www.github.com/micahflee/torbrowser-launcher',
    platforms=['GNU/Linux'],
    license='MIT',
    description='A program to help you securely download and run Tor Browser',
    long_description="""
Tor Browser Launcher is intended to make Tor Browser easier to install and use
for GNU/Linux users. You install torbrowser-launcher from your distribution's
package manager and it handles securely downloading the most recent version of
Tor Browser for you, in your language and for your architecture. It also adds a
"Tor Browser" application launcher to your operating system's menu. When you
first launch Tor Browser Launcher, it will download Tor Browser from
https://www.torproject.org/, verify the PGP signature, extract it in your home
directory, and launch it. When you run it after that it will just launch Tor
Browser.
""",
    packages=['torbrowser_launcher'],
    scripts=['torbrowser-launcher'],
    data_files=datafiles
)
