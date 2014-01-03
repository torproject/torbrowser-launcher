"""
Tor Browser Launcher
https://github.com/micahflee/torbrowser-launcher/

Copyright (c) 2013 Micah Lee <micah@micahflee.com>

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
import os

def file_list(path):
    files = []
    for filename in os.listdir(path):
        if os.path.isfile(path+'/'+filename):
            files.append(path+'/'+filename)
    return files

version = open('version').read().strip()

setup(name='torbrowser-launcher',
      version=version,
      author='Micah Lee',
      author_email='micah@micahflee.com',
      url='https://www.github.com/micahflee/torbrowser-launcher',
      platforms=['GNU/Linux'],
      license='BSD',

      description='A program to help you download, keep updated, and run the Tor Browser Bundle',
      long_description="""
Tor Browser Launcher is intended to make the Tor Browser Bundle (TBB) easier to maintain and use for GNU/Linux users. You install torbrowser-launcher from your distribution's package manager and it handles downloading the most recent version of TBB for you, in your language and for your architecture. It also adds a "Tor Browser" application launcher to your operating system's menu.

When you first launch Tor Browser Launcher, it will download TBB from https://www.torproject.org/ and extract it in ~/.torproject, and then execute it. When you run it after that it will just execute TBB.

Tor Browser Launcher will get updated each time a new version of TBB is released. When you open Tor Browser after an update, it will download the newer version of TBB for you and extract it over your old TBB directory in ~/.torproject, so you will maintain your TBB bookmarks. 
""",

      scripts=['torbrowser-launcher'],
      data_files=[('/usr/share/applications', ['torbrowser.desktop', 'torbrowser-settings.desktop']),
                  ('/usr/share/pixmaps', ['img/torbrowser32.xpm', 'img/torbrowser80.xpm']),
                  ('/usr/share/torbrowser-launcher', ['keys/erinn.asc', 'keys/sebastian.asc', 'keys/alexandre.asc', 'keys/mike.asc', 'keys/mike-2013-09.asc', 'torproject.pem', 'mirrors.txt', 'modem.ogg', 'version']),
                  ('/usr/share/torbrowser-launcher/locale/en', ['locale/en/messages.pot']),
                  ('/etc/apparmor.d/', ['apparmor/torbrowser.Browser.firefox', 'apparmor/torbrowser.start-tor-browser', 'apparmor/torbrowser.Tor.tor', 'apparmor/usr.bin.torbrowser-launcher']),

                  # unpackaged third party libraries
                  ('/usr/share/torbrowser-launcher/lib/txsocksx', file_list('lib/txsocksx-0.0.2/txsocksx')),
                  ('/usr/share/torbrowser-launcher/lib', ['lib/Parsley-1.1/parsley.py']),
                  ('/usr/share/torbrowser-launcher/lib/ometa', file_list('lib/Parsley-1.1/ometa')),
                  ('/usr/share/torbrowser-launcher/lib/ometa/_generated', file_list('lib/Parsley-1.1/ometa/_generated')),
                  ('/usr/share/torbrowser-launcher/lib/ometa/test', file_list('lib/Parsley-1.1/ometa/test')),
                  ('/usr/share/torbrowser-launcher/lib/terml', file_list('lib/Parsley-1.1/terml')),
                  ('/usr/share/torbrowser-launcher/lib/terml/_generated', file_list('lib/Parsley-1.1/terml/_generated')),
                  ('/usr/share/torbrowser-launcher/lib/terml/test', file_list('lib/Parsley-1.1/terml/test'))]
      )
