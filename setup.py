from distutils.core import setup

setup(name='torbrowser-launcher',
      description='A program to help you download, keep updated, and run the Tor Browser Bundle',
      author='Micah Lee',
      author_email='micahflee@riseup.net',
      url='https://www.github.com/micahflee/torbrowser-launcher',
      version='2.3.25-2-0.1',
      scripts=['torbrowser-launcher'],
      data_files=[('/usr/share/applications', ['misc/torbrowser.desktop']),
                  ('/usr/share/pixmaps', ['misc/*.xpm'])]
      )
