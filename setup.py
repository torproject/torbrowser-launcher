"""
Tor Browser Launcher
https://github.com/micahflee/torbrowser-launcher/

Copyright (c) 2013 Micah Lee
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of the University nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
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
                  ('/usr/share/torbrowser-launcher', ['keys/erinn.asc', 'keys/sebastian.asc', 'torproject.pem']),
                  ('/usr/share/torbrowser-launcher/locale/en', ['locale/en/messages.pot'])]
      )
