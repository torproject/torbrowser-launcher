"""
Tor Browser Launcher
https://github.com/micahflee/torbrowser-launcher/

Copyright (c) 2013 Micah Lee <micahflee@riseup.net>

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

setup(name='torbrowser-launcher',
      version='0.0.1',
      author='Micah Lee',
      author_email='micahflee@riseup.net',
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
      data_files=[('/usr/share/applications', ['torbrowser.desktop']),
                  ('/usr/share/pixmaps', ['img/torbrowser32.xpm', 'img/torbrowser80.xpm']),
                  ('/usr/share/torbrowser-launcher', ['keys/erinn.asc', 'keys/sebastian.asc', 'keys/alexandre.asc', 'torproject.pem']),
                  ('/usr/share/torbrowser-launcher/locale/en', ['locale/en/messages.pot'])]
      )
