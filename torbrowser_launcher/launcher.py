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
import subprocess
import time
import tarfile
import lzma
import re
import requests
import gpg
import shutil
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
            # Different message if downloading for the first time, or because your installed version is too low
            download_message = ""
            if not self.common.settings['installed']:
                download_message = _("Downloading Tor Browser for the first time.")
            elif not self.check_min_version():
                download_message = _("Your version of Tor Browser is out-of-date. "
                                     "Downloading the newest version.")

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

            if self.common.settings['download_over_tor']:
                print(_('Downloading over Tor'))

        else:
            # Tor Browser is already installed, so run
            launch_message = "Launching Tor Browser."
            print(launch_message)
            self.set_state('task', launch_message, ['run'])

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
        self.start_button = QtWidgets.QPushButton(_('Start'))
        self.start_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        self.start_button.clicked.connect(self.start)
        self.cancel_button = QtWidgets.QPushButton()
        self.cancel_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))
        self.cancel_button.clicked.connect(self.close)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.yes_button)
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(buttons_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

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

        # Resize the window
        self.adjustSize()

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

    def download(self, name, url, path):
        # Download from the selected mirror
        mirror_url = url.format(self.common.settings['mirror']).encode()

        # Initialize the progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        if self.common.settings['download_over_tor']:
            self.progress_bar.setFormat(_('Downloading') + ' {0} '.format(name) + _('(over Tor)') + ', %p%')
        else:
            self.progress_bar.setFormat(_('Downloading') + ' {0}, %p%'.format(name))

        def progress_update(total_bytes, bytes_so_far):
            percent = float(bytes_so_far) / float(total_bytes)
            amount = float(bytes_so_far)
            units = "bytes"
            for (size, unit) in [(1024 * 1024, "MiB"), (1024, "KiB")]:
                if amount > size:
                    units = unit
                    amount /= float(size)
                    break

            message = _('Downloaded') + (' %2.1f%% (%2.1f %s)' % ((percent * 100.0), amount, units))
            if self.common.settings['download_over_tor']:
                message += ' ' + _('(over Tor)')

            self.progress_bar.setMaximum(total_bytes)
            self.progress_bar.setValue(bytes_so_far)
            self.progress_bar.setFormat(message)

        def download_complete():
            # Download complete, next task
            self.run_task()

        def download_error(gui, message):
            print(message)
            self.set_state(gui, message, [], False)
            self.update()

        t = DownloadThread(self.common, mirror_url, path)
        t.progress_update.connect(progress_update)
        t.download_complete.connect(download_complete)
        t.download_error.connect(download_error)
        t.start()
        time.sleep(0.2)

    def try_default_mirror(self):
        # change mirror to default and relaunch TBL
        self.common.settings['mirror'] = self.common.default_mirror
        self.common.save_settings()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.close()

    def try_forcing_english(self):
        # change force english to true and relaunch TBL
        self.common.settings['force_en-US'] = True
        self.common.save_settings()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.close()

    def try_tor(self):
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
        self.progress_bar.show()

        self.label.setText(_('Verifying Signature'))

        def success():
            self.run_task()

        def error(message):
            # Make backup of tarball and sig
            backup_tarball_filename = self.common.paths['tarball_file'] + '.verification_failed'
            backup_sig_filename = self.common.paths['sig_file'] + '.verification_failed'
            shutil.copyfile(self.common.paths['tarball_file'], backup_tarball_filename)
            shutil.copyfile(self.common.paths['sig_file'], backup_sig_filename)

            sigerror = 'SIGNATURE VERIFICATION FAILED!\n\n' \
                       'Error Code: {0}\n\n' \
                       'You might be under attack, there might be a network problem, or you may be missing a ' \
                       'recently added Tor Browser verification key.\n\n' \
                       'A copy of the Tor Browser files you downloaded have been saved here:\n' \
                       '{1}\n{2}\n\n' \
                       'Click Start to refresh the keyring and try again. If the message persists report the above ' \
                       'error code here:\nhttps://github.com/micahflee/torbrowser-launcher/issues'
            sigerror = sigerror.format(message, backup_tarball_filename, backup_sig_filename)

            self.set_state('task', sigerror, ['start_over'], False)
            self.update()

        t = VerifyThread(self.common)
        t.error.connect(error)
        t.success.connect(success)
        t.start()
        time.sleep(0.2)

    def extract(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.show()

        self.label.setText(_('Installing'))

        def success():
            self.run_task()

        def error(message):
            self.set_state(
                'task',
                _("Tor Browser Launcher doesn't understand the file format of {0}".format(self.common.paths['tarball_file'])),
                ['start_over'], False
            )
            self.update()

        t = ExtractThread(self.common)
        t.error.connect(error)
        t.success.connect(success)
        t.start()
        time.sleep(0.2)

    def check_min_version(self):
        installed_version = None
        for line in open(self.common.paths['tbb']['changelog'],'rb').readlines():
            if line.startswith(b'Tor Browser '):
                installed_version = line.split()[2].decode()
                break

        def version_tuple(v):
            return tuple(map(int, v.split(".")))

        if version_tuple(self.min_version) <= version_tuple(installed_version):
            return True

        return False

    def run(self):
        # Don't run if it isn't at least the minimum version
        if not self.check_min_version():
            message = _("The version of Tor Browser you have installed is earlier than it should be, which could be a "
                        "sign of an attack!")
            print(message)

            Alert(self.common, message)
            return

        # Run Tor Browser
        subprocess.call([self.common.paths['tbb']['start']], cwd=self.common.paths['tbb']['dir_tbb'])
        sys.exit(0)

    # Start over and download TBB again
    def start_over(self):
        self.force_redownload = True  # Overwrite any existing file
        self.label.setText(_("Downloading Tor Browser over again."))
        self.gui_tasks = ['download_tarball', 'verify', 'extract', 'run']
        self.gui_task_i = 0
        self.start(None)

    def closeEvent(self, event):
        # Clear the download cache
        try:
            os.remove(self.common.paths['version_check_file'])
            os.remove(self.common.paths['sig_file'])
            os.remove(self.common.paths['tarball_file'])
        except:
            pass

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


class DownloadThread(QtCore.QThread):
    """
    Download a file in a separate thread.
    """
    progress_update = QtCore.pyqtSignal(int, int)
    download_complete = QtCore.pyqtSignal()
    download_error = QtCore.pyqtSignal(str, str)

    def __init__(self, common, url, path):
        super(DownloadThread, self).__init__()
        self.common = common
        self.url = url
        self.path = path

        # Use tor socks5 proxy, if enabled
        if self.common.settings['download_over_tor']:
            socks5_address = 'socks5://{}'.format(self.common.settings['tor_socks_address'])
            self.proxies = {
                'https': socks5_address,
                'http': socks5_address
            }
        else:
            self.proxies = None

    def run(self):
        with open(self.path, "wb") as f:
            try:
                # Start the request
                r = requests.get(self.url,
                                 headers={'User-Agent': 'torbrowser-launcher'},
                                 stream=True, proxies=self.proxies)

                # If status code isn't 200, something went wrong
                if r.status_code != 200:
                    # Should we use the default mirror?
                    if self.common.settings['mirror'] != self.common.default_mirror:
                        message = (_("Download Error:") +
                                   " {0}\n\n" + _("You are currently using a non-default mirror") +
                                   ":\n{1}\n\n" + _("Would you like to switch back to the default?")).format(
                                       r.status_code, self.common.settings['mirror']
                                   )
                        self.download_error.emit('error_try_default_mirror', message)

                    # Should we switch to English?
                    elif self.common.language != 'en-US' and not self.common.settings['force_en-US']:
                        message = (_("Download Error:") +
                                   " {0}\n\n" +
                                   _("Would you like to try the English version of Tor Browser instead?")).format(
                                       r.status_code
                                   )
                        self.download_error.emit('error_try_forcing_english', message)

                    else:
                        message = (_("Download Error:") + " {0}").format(r.status_code)
                        self.download_error.emit('error', message)

                    r.close()
                    return

                # Start streaming the download
                total_bytes = int(r.headers.get('content-length'))
                bytes_so_far = 0
                for data in r.iter_content(chunk_size=4096):
                    bytes_so_far += len(data)
                    f.write(data)
                    self.progress_update.emit(total_bytes, bytes_so_far)

            except requests.exceptions.SSLError:
                message = _('Invalid SSL certificate for:\n{0}\n\nYou may be under attack.').format(self.url.decode())
                if not self.common.settings['download_over_tor']:
                    message += "\n\n" + _('Try the download again using Tor?')
                    self.download_error.emit('error_try_tor', message)
                else:
                    self.download_error.emit('error', message)
                return

            except requests.exceptions.ConnectionError:
                # Connection error
                if self.common.settings['download_over_tor']:
                    message = _("Error starting download:\n\n{0}\n\nTrying to download over Tor. "
                                "Are you sure Tor is configured correctly and running?").format(self.url.decode())
                    self.download_error.emit('error', message)
                else:
                    message = _("Error starting download:\n\n{0}\n\nAre you connected to the internet?").format(
                        self.url.decode()
                    )
                    self.download_error.emit('error', message)

                return

        self.download_complete.emit()


class VerifyThread(QtCore.QThread):
    """
    Verify the signature in a separate thread
    """
    success = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)

    def __init__(self, common):
        super(VerifyThread, self).__init__()
        self.common = common

    def run(self):
        def verify(second_try=False):
            with gpg.Context() as c:
                c.set_engine_info(gpg.constants.protocol.OpenPGP, home_dir=self.common.paths['gnupg_homedir'])

                sig = gpg.Data(file=self.common.paths['sig_file'])
                signed = gpg.Data(file=self.common.paths['tarball_file'])

                try:
                    c.verify(signature=sig, signed_data=signed)
                except gpg.errors.BadSignatures as e:
                    if second_try:
                        self.error.emit(str(e))
                    else:
                        raise Exception
                else:
                    self.success.emit()

        try:
            # Try verifying
            verify()
        except:
            # If it fails, refresh the keyring and try again
            self.common.refresh_keyring()
            verify(True)


class ExtractThread(QtCore.QThread):
    """
    Extract the tarball in a separate thread
    """
    success = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal()

    def __init__(self, common):
        super(ExtractThread, self).__init__()
        self.common = common

    def run(self):
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

        if extracted:
            self.success.emit()
        else:
            self.error.emit()
