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
import subprocess
import time
import json
import tarfile
import hashlib
import lzma
import threading
import re
import unicodedata
import requests
import gpg
import OpenSSL
import xml.etree.ElementTree as ET

from PyQt5 import QtCore, QtWidgets, QtGui


class TryStableException(Exception):
    pass


class TryDefaultMirrorException(Exception):
    pass


class TryForcingEnglishException(Exception):
    pass


class DownloadErrorException(Exception):
    pass


class Launcher(QtWidgets.QMainWindow):
    """
    Launcher window.
    """
    def __init__(self, common, app, url_list):
        super(Launcher, self).__init__()
        self.common = common
        self.app = app

        self.url_list = url_list
        self.force_redownload = False

        # This is the current version of Tor Browser, which should get updated with every release
        self.min_version = '7.5.2'

        # Init launcher
        self.set_state(None, '', [])
        self.launch_gui = True

        # If Tor Browser is not installed, detect latest version, download, and install
        if not self.common.settings['installed'] or not self.check_min_version():
            # If downloading over Tor, include txsocksx
            if self.common.settings['download_over_tor']:
                try:
                    import txsocksx
                    print(_('Downloading over Tor'))
                except ImportError:
                    Alert(self.common, _("The python-txsocksx package is missing, downloads will not happen over tor"))
                    self.common.settings['download_over_tor'] = False
                    self.common.save_settings()

            # Different message if downloading for the first time, or because your installed version is too low
            download_message = ""
            if not self.common.settings['installed']:
                download_message = _("Downloading and installing Tor Browser for the first time.")
            elif not self.check_min_version():
                download_message = _("Your version of Tor Browser is out-of-date. Downloading and installing the newest version.")

            # Download and install
            print(download_message)
            self.set_state('task', download_message,
                         ['download_version_check',
                          'set_version',
                          'download_sig',
                          'download_tarball',
                          'verify',
                          'extract',
                          'run'])

        else:
            # Tor Browser is already installed, so run
            self.run(False)
            self.launch_gui = False

        if self.launch_gui:
            # Build the rest of the UI

            # Set up the window
            self.setWindowTitle(_("Tor Browser"))
            self.setWindowIcon(QtGui.QIcon(self.common.paths['icon_file']))

            # Label
            self.label = QtWidgets.QLabel()

            # Progress bar
            self.progress_bar = QtWidgets.QProgressBar()
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
            self.progress_bar.setValue(0)

            # Buttons
            self.yes_button = QtWidgets.QPushButton()
            self.yes_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
            self.yes_button.clicked.connect(self.yes_clicked)
            self.start_button = QtWidgets.QPushButton()
            self.start_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
            self.start_button.clicked.connect(self.start)
            self.cancel_button = QtWidgets.QPushButton()
            self.start_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))
            self.cancel_button.clicked.connect(self.close)
            buttons_layout = QtWidgets.QHBoxLayout()
            buttons_layout.addWidget(self.start_button)
            buttons_layout.addWidget(self.cancel_button)

            # Layout
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.label)
            layout.addWidget(self.progress_bar)
            layout.addLayout(buttons_layout)

            central_widget = QtWidgets.QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)
            self.show()

            self.update()

    # Set the current state of Tor Browser Launcher
    def set_state(self, gui, message, tasks, autostart=True):
        self.gui = gui
        self.gui_message = message
        self.gui_tasks = tasks
        self.gui_task_i = 0
        self.gui_autostart = autostart

    # Show and hide parts of the UI based on the current state
    def update(self):
        # Hide widgets
        self.progress_bar.hide()
        self.yes_button.hide()
        self.start_button.hide()

        if 'error' in self.gui:
            # Label
            self.label.setText(self.gui_message)

            # Yes button
            if self.gui != 'error':
                self.yes_button.setText(_('Yes'))
                self.yes_button.show()

            # Exit button
            self.cancel_button.setText(_('Exit'))

        elif self.gui == 'task':
            # Label
            self.label.setText(self.gui_message)

            # Progress bar
            self.progress_bar.show()

            # Start button
            if not self.gui_autostart:
                self.start_button.show()

            # Cancel button
            self.cancel_button.setText(_('Cancel'))

        if self.gui_autostart:
            self.start(None)

    # Yes button clicked, based on the state decide what to do
    def yes_clicked(self):
        if self.gui == 'error_try_stable':
            self.try_stable()
        elif self.gui == 'error_try_default_mirror':
            self.try_default_mirror()
        elif self.gui == 'error_try_forcing_english':
            self.try_forcing_english()
        elif self.gui == 'error_try_tor':
            self.try_tor()

    # Start button clicked, begin tasks
    def start(self, widget, data=None):
        # Hide the start button
        self.start_button.hide()

        # Start running tasks
        self.run_task()

    # Run the next task in the task list
    def run_task(self):
        if self.gui_task_i >= len(self.gui_tasks):
            self.close()
            return

        task = self.gui_tasks[self.gui_task_i]

        # Get ready for the next task
        self.gui_task_i += 1

        if task == 'download_version_check':
            print(_('Downloading'), self.common.paths['version_check_url'])
            self.download('version check', self.common.paths['version_check_url'], self.common.paths['version_check_file'])

        if task == 'set_version':
            version = self.get_stable_version()
            if version:
                self.common.build_paths(self.get_stable_version())
                print(_('Latest version: {}').format(version))
                self.run_task()
            else:
                self.set_state('error', _("Error detecting Tor Browser version."), [], False)
                self.update()

        elif task == 'download_sig':
            print(_('Downloading'), self.common.paths['sig_url'].format(self.common.settings['mirror']))
            self.download('signature', self.common.paths['sig_url'], self.common.paths['sig_file'])

        elif task == 'download_tarball':
            print(_('Downloading'), self.common.paths['tarball_url'].format(self.common.settings['mirror']))
            if not self.force_redownload and os.path.exists(self.common.paths['tarball_file']):
                self.run_task()
            else:
                self.download('tarball', self.common.paths['tarball_url'], self.common.paths['tarball_file'])

        elif task == 'verify':
            print(_('Verifying Signature'))
            self.verify()

        elif task == 'extract':
            print(_('Extracting'), self.common.paths['tarball_filename'])
            self.extract()

        elif task == 'run':
            print(_('Running'), self.common.paths['tbb']['start'])
            self.run()

        elif task == 'start_over':
            print(_('Starting download over again'))
            self.start_over()

    def response_received(self, response):
        class FileDownloader(Protocol):
            def __init__(self, common, file, url, total, progress, done_cb):
                self.file = file
                self.total = total
                self.so_far = 0
                self.progress = progress
                self.all_done = done_cb

                if response.code != 200:
                    if common.settings['mirror'] != common.default_mirror:
                        raise TryDefaultMirrorException(
                            (_("Download Error:") + " {0} {1}\n\n" + _("You are currently using a non-default mirror")
                             + ":\n{2}\n\n" + _("Would you like to switch back to the default?")).format(
                                response.code, response.phrase, common.settings['mirror']
                            )
                        )
                    elif common.language != 'en-US' and not common.settings['force_en-US']:
                        raise TryForcingEnglishException(
                            (_("Download Error:") + " {0} {1}\n\n"
                             + _("Would you like to try the English version of Tor Browser instead?")).format(
                                response.code, response.phrase
                            )
                        )
                    else:
                        raise DownloadErrorException(
                            (_("Download Error:") + " {0} {1}").format(response.code, response.phrase)
                        )

            def dataReceived(self, bytes):
                self.file.write(bytes)
                self.so_far += len(bytes)
                percent = float(self.so_far) / float(self.total)
                self.progress.setValue(percent)
                amount = float(self.so_far)
                units = "bytes"
                for (size, unit) in [(1024 * 1024, "MiB"), (1024, "KiB")]:
                    if amount > size:
                        units = unit
                        amount /= float(size)
                        break

                self.progress.setFormat(_('Downloaded')+(' %2.1f%% (%2.1f %s)' % ((percent * 100.0), amount, units)))

            def connectionLost(self, reason):
                self.all_done(reason)

        if hasattr(self, 'current_download_url'):
            url = self.current_download_url
        else:
            url = None

        dl = FileDownloader(
            self.common, self.file_download, url, response.length, self.progress_bar, self.response_finished
        )
        response.deliverBody(dl)

    def response_finished(self, msg):
        if msg.check(ResponseDone):
            self.file_download.close()
            delattr(self, 'current_download_path')
            delattr(self, 'current_download_url')

            # next task!
            self.run_task()

        else:
            print("FINISHED", msg)
            ## FIXME handle errors

    def download_error(self, f):
        print(_("Download Error:"), f.value, type(f.value))

        if isinstance(f.value, TryStableException):
            f.trap(TryStableException)
            self.set_state('error_try_stable', str(f.value), [], False)

        elif isinstance(f.value, TryDefaultMirrorException):
            f.trap(TryDefaultMirrorException)
            self.set_state('error_try_default_mirror', str(f.value), [], False)

        elif isinstance(f.value, TryForcingEnglishException):
            f.trap(TryForcingEnglishException)
            self.set_state('error_try_forcing_english', str(f.value), [], False)

        elif isinstance(f.value, DownloadErrorException):
            f.trap(DownloadErrorException)
            self.set_state('error', str(f.value), [], False)

        elif isinstance(f.value, DNSLookupError):
            f.trap(DNSLookupError)
            if common.settings['mirror'] != common.default_mirror:
                self.set_state('error_try_default_mirror', (_("DNS Lookup Error") + "\n\n" +
                                                          _("You are currently using a non-default mirror")
                                                          + ":\n{0}\n\n"
                                                          + _("Would you like to switch back to the default?")
                                                          ).format(common.settings['mirror']), [], False)
            else:
                self.set_state('error', str(f.value), [], False)

        elif isinstance(f.value, ResponseFailed):
            for reason in f.value.reasons:
                if isinstance(reason.value, OpenSSL.SSL.Error):
                    # TODO: add the ability to report attack by posting bug to trac.torproject.org
                    if not self.common.settings['download_over_tor']:
                        self.set_state('error_try_tor',
                                     _('The SSL certificate served by https://www.torproject.org is invalid! You may '
                                       'be under attack.') + " " + _('Try the download again using Tor?'), [], False)
                    else:
                        self.set_state('error', _('The SSL certificate served by https://www.torproject.org is invalid! '
                                                'You may be under attack.'), [], False)

        elif isinstance(f.value, ConnectionRefusedError) and self.common.settings['download_over_tor']:
            # If we're using Tor, we'll only get this error when we fail to
            # connect to the SOCKS server.  If the connection fails at the
            # remote end, we'll get txsocksx.errors.ConnectionRefused.
            addr = self.common.settings['tor_socks_address']
            self.set_state('error', _("Error connecting to Tor at {0}").format(addr), [], False)

        else:
            self.set_state('error', _("Error starting download:\n\n{0}\n\nAre you connected to the internet?").format(f.value), [], False)

        self.update()

    def download(self, name, url, path):
        # Keep track of current download
        self.current_download_path = path
        self.current_download_url = url.encode()

        mirror_url = url.format(self.common.settings['mirror'])
        mirror_url = mirror_url.encode()

        # Initialize the progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFormat(_('Downloading') + ' {0}, %p%'.format(name))

        if self.common.settings['download_over_tor']:
            # TODO: make requests work over SOCKS5 proxy
            # this is the proxy to use: self.common.settings['tor_socks_address']
            pass

        with open(self.current_download_path, "wb") as f:
            # Start the request
            r = requests.get(mirror_url, headers={'User-Agent': 'torbrowser-launcher'}, stream=True)
            total_length = r.headers.get('content-length')

            if total_length is None: # no content length header
                f.write(r.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in r.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    print('{} / {}'.format(dl, total_length), end='\r')

        # Download complete, next task
        self.run_task()

    def try_default_mirror(self, widget, data=None):
        # change mirror to default and relaunch TBL
        self.common.settings['mirror'] = self.common.default_mirror
        self.common.save_settings()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.close()

    def try_forcing_english(self, widget, data=None):
        # change force english to true and relaunch TBL
        self.common.settings['force_en-US'] = True
        self.common.save_settings()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.close()

    def try_tor(self, widget, data=None):
        # set download_over_tor to true and relaunch TBL
        self.common.settings['download_over_tor'] = True
        self.common.save_settings()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.close()

    def get_stable_version(self):
        tree = ET.parse(self.common.paths['version_check_file'])
        for up in tree.getroot():
            if up.tag == 'update' and up.attrib['appVersion']:
                version = str(up.attrib['appVersion'])

                # make sure the version does not contain directory traversal attempts
                # e.g. "5.5.3", "6.0a", "6.0a-hardened" are valid but "../../../../.." is invalid
                if not re.match(r'^[a-z0-9\.\-]+$', version):
                    return None

                return version
        return None

    def verify(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setFormat(_('Verifying Signature'))
        self.progress_bar.show()

        def gui_raise_sigerror(self, sigerror='MissingErr'):
            """
            :type sigerror: str
            """
            sigerror = 'SIGNATURE VERIFICATION FAILED!\n\nError Code: {0}\n\nYou might be under attack, there might' \
                       ' be a network\nproblem, or you may be missing a recently added\nTor Browser verification key.' \
                       '\nClick Start to refresh the keyring and try again. If the message persists report the above' \
                       ' error code here:\nhttps://github.com/micahflee/torbrowser-launcher/issues'.format(sigerror)

            self.set_state('task', sigerror, ['start_over'], False)
            self.update()

        with gpg.Context() as c:
            c.set_engine_info(gpg.constants.protocol.OpenPGP, home_dir=self.common.paths['gnupg_homedir'])

            sig = gpg.Data(file=self.common.paths['sig_file'])
            signed = gpg.Data(file=self.common.paths['tarball_file'])

            try:
                c.verify(signature=sig, signed_data=signed)
            except gpg.errors.BadSignatures as e:
                result = str(e).split(": ")
                if result[1] == 'Bad signature':
                    gui_raise_sigerror(self, str(e))
                elif result[1] == 'No public key':
                    self.common.refresh_keyring(result[0])
                    gui_raise_sigerror(self, str(e))
            else:
                self.run_task()

    def extract(self):
        # initialize the progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setFormat(_('Installing'))
        self.progress_bar.show()

        extracted = False
        try:
            if self.common.paths['tarball_file'][-2:] == 'xz':
                # if tarball is .tar.xz
                xz = lzma.LZMAFile(self.common.paths['tarball_file'])
                tf = tarfile.open(fileobj=xz)
                tf.extractall(self.common.paths['tbb']['dir'])
                extracted = True
            else:
                # if tarball is .tar.gz
                if tarfile.is_tarfile(self.common.paths['tarball_file']):
                    tf = tarfile.open(self.common.paths['tarball_file'])
                    tf.extractall(self.common.paths['tbb']['dir'])
                    extracted = True
        except:
            pass

        if not extracted:
            self.set_state('task', _("Tor Browser Launcher doesn't understand the file format of {0}".format(self.common.paths['tarball_file'])), ['start_over'], False)
            self.update()
            return

        self.run_task()

    def check_min_version(self):
        installed_version = None
        for line in open(self.common.paths['tbb']['changelog']).readlines():
            if line.startswith('Tor Browser '):
                installed_version = line.split()[2]
                break

        if self.min_version <= installed_version:
            return True

        return False

    def run(self, run_next_task=True):
        # Don't run if it isn't at least the minimum version
        if not self.check_min_version():
            message = _("The version of Tor Browser you have installed is earlier than it should be, which could be a "
                        "sign of an attack!")
            print(message)

            Alert(self.common, message)
            return

        # Hide the TBL window (#151)
        self.hide()

        # Run Tor Browser
        subprocess.call([self.common.paths['tbb']['start']], cwd=self.common.paths['tbb']['dir_tbb'])

        if run_next_task:
            self.run_task()

    # Start over and download TBB again
    def start_over(self):
        self.force_redownload = True  # Overwrite any existing file
        self.label.setText(_("Downloading Tor Browser Bundle over again."))
        self.gui_tasks = ['download_tarball', 'verify', 'extract', 'run']
        self.gui_task_i = 0
        self.start(None)

    def closeEvent(self, event):
        if hasattr(self, 'file_download'):
            self.file_download.close()
        if hasattr(self, 'current_download_path'):
            os.remove(self.current_download_path)
            delattr(self, 'current_download_path')
            delattr(self, 'current_download_url')

        super(Launcher, self).closeEvent(event)


class Alert(QtWidgets.QMessageBox):
    """
    An alert box dialog.
    """
    def __init__(self, common, message, icon=QtWidgets.QMessageBox.NoIcon, buttons=QtWidgets.QMessageBox.Ok, autostart=True):
        super(Alert, self).__init__(None)

        self.setWindowTitle(_("Tor Browser Launcher"))
        self.setWindowIcon(QtGui.QIcon(common.paths['icon_file']))
        self.setText(message)
        self.setIcon(icon)
        self.setStandardButtons(buttons)

        if autostart:
            self.exec_()
