from distutils.core import setup

setup(name='torbrowser-launcher',
      version='0.1',
      author='Micah Lee',
      author_email='micahflee@riseup.net',
      url='https://www.github.com/micahflee/torbrowser-launcher',
      platforms=['GNU/Linux'],
      license='GPLv3',

      description='A program to help you download, keep updated, and run the Tor Browser Bundle',
      long_description="""
Tor Browser Launcher is intended to make the Tor Browser Bundle (TBB) easier to maintain and use for GNU/Linux users. You install torbrowser-launcher from your distribution's package manager and it handles downloading the most recent version of TBB for you, in your language and for your architecture. It also adds a "Tor Browser" application launcher to your operating system's menu.

When you first launch Tor Browser Launcher, it will download TBB from https://www.torproject.org/ and extract it in ~/.torproject, and then execute it. When you run it after that it will just execute TBB.

Tor Browser Launcher will get updated each time a new version of TBB is released. When you open Tor Browser after an update, it will download the newer version of TBB for you and extract it over your old TBB directory in ~/.torproject, so you will maintain your TBB bookmarks. 
""",

      scripts=['torbrowser-launcher'],
      data_files=[('/usr/share/applications', ['torbrowser.desktop']),
                  ('/usr/share/pixmaps', ['torbrowser32.xpm', 'torbrowser80.xpm']),
                  ('/usr/share/torbrowser-launcher', ['keys/erinn.asc', 'keys/sebastian.asc', 'verify.sh'])]
      )
