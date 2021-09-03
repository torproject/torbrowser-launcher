"""
Tor Browser Launcher
https://github.com/micahflee/torbrowser-launcher/

Copyright (c) 2013-2021 Micah Lee <micah@micahflee.com>

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
import argparse
import signal

from PyQt5 import QtCore, QtWidgets

from .common import Common, SHARE
from .settings import Settings
from .launcher import Launcher


class Application(QtWidgets.QApplication):
    """
    Qt's QApplication class. It has been overridden to support threads.
    """

    def __init__(self):
        self.setAttribute(QtCore.Qt.AA_X11InitThreads, True)
        QtWidgets.QApplication.__init__(self, sys.argv)
        self.installEventFilter(self)


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--settings",
        action="store_true",
        dest="settings",
        help="Open Tor Browser Launcher settings",
    )
    parser.add_argument("url", nargs="*", help="URL to load")
    args = parser.parse_args()

    settings = bool(args.settings)
    url_list = args.url

    # Load the version and print the banner
    with open(os.path.join(SHARE, "version")) as buf:
        tor_browser_launcher_version = buf.read().strip()

    print(_("Tor Browser Launcher"))
    print(_("By Micah Lee, licensed under MIT"))
    print(_("version {0}").format(tor_browser_launcher_version))
    print("https://github.com/micahflee/torbrowser-launcher")

    common = Common(tor_browser_launcher_version)
    app = Application()

    # Open the window
    gui = None

    if settings:
        # Settings mode
        gui = Settings(common, app)
    else:
        # Launcher mode
        gui = Launcher(common, app, url_list)

    # Center the window
    desktop = app.desktop()
    window_size = gui.size()
    gui.move(
        int((desktop.width() - window_size.width()) / 2),
        int((desktop.height() - window_size.height()) / 2),
    )
    gui.show()

    # Allow ctrl-c to work
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
