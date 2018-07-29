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

import subprocess
import shutil

from PyQt5 import QtCore, QtWidgets, QtGui


class Settings(QtWidgets.QMainWindow):
    """
    Settings window.
    """
    def __init__(self, common, app):
        super(Settings, self).__init__()

        self.common = common
        self.app = app

        # Set up the window
        self.setWindowTitle(_("Tor Browser Launcher Settings"))
        self.setWindowIcon(QtGui.QIcon(self.common.paths['icon_file']))

        # Download over system tor
        self.tor_download_checkbox = QtWidgets.QCheckBox(_("Download over system Tor"))
        if self.common.settings['download_over_tor']:
            self.tor_download_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.tor_download_checkbox.setCheckState(QtCore.Qt.Unchecked)

        # Force en-US, only display if language isn't already en-US
        self.force_en_checkbox = QtWidgets.QCheckBox(_("Force downloading English version of Tor Browser"))
        if self.common.settings['force_en-US']:
            self.force_en_checkbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.force_en_checkbox.setCheckState(QtCore.Qt.Unchecked)
        if self.common.language == 'en-US':
            self.force_en_checkbox.hide()

        # Tor SOCKS address
        tor_addr_label = QtWidgets.QLabel(_('Tor server'))
        self.tor_addr = QtWidgets.QLineEdit()
        self.tor_addr.setText(self.common.settings['tor_socks_address'])
        tor_addr_layout = QtWidgets.QHBoxLayout()
        tor_addr_layout.addWidget(tor_addr_label)
        tor_addr_layout.addWidget(self.tor_addr)

        # Settings layout
        settings_layout = QtWidgets.QVBoxLayout()
        settings_layout.addWidget(self.tor_download_checkbox)
        settings_layout.addWidget(self.force_en_checkbox)
        settings_layout.addLayout(tor_addr_layout)

        # Status
        status_label = QtWidgets.QLabel()
        if(self.common.settings['installed']):
            status_label.setText(_('Status: Installed'))
        else:
            status_label.setText(_('Status: Not Installed'))

        # Install button
        install_button = QtWidgets.QPushButton(_("Install Tor Browser"))
        install_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        install_button.clicked.connect(self.install)

        # Reinstall buttons
        reinstall_button = QtWidgets.QPushButton(_("Reinstall Tor Browser"))
        reinstall_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        reinstall_button.clicked.connect(self.reinstall)

        if(self.common.settings['installed']):
            install_button.hide()
            reinstall_button.show()
        else:
            install_button.show()
            reinstall_button.hide()

        # Status layout
        status_layout = QtWidgets.QVBoxLayout()
        status_layout.addWidget(status_label)
        status_layout.addWidget(install_button)
        status_layout.addWidget(reinstall_button)

        # Top layout
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addLayout(settings_layout)
        top_layout.addLayout(status_layout)

        # Mirror
        mirror_label = QtWidgets.QLabel(_('Mirror'))

        self.mirror = QtWidgets.QComboBox()
        for mirror in self.common.mirrors:
            self.mirror.addItem(mirror)

        if self.common.settings['mirror'] in self.common.mirrors:
            self.mirror.setCurrentIndex(self.mirror.findText(self.common.settings['mirror']))
        else:
            self.mirror.setCurrentIndex(0)

        mirror_layout = QtWidgets.QHBoxLayout()
        mirror_layout.addWidget(mirror_label)
        mirror_layout.addWidget(self.mirror)

        # Save & Exit button
        self.save_exit_button = QtWidgets.QPushButton(_("Save && Exit"))
        self.save_exit_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton))
        self.save_exit_button.clicked.connect(self.save_exit)

        # Cancel button
        self.cancel_button = QtWidgets.QPushButton(_("Cancel"))
        self.cancel_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))
        self.cancel_button.clicked.connect(self.close)

        # Buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.save_exit_button)
        buttons_layout.addWidget(self.cancel_button)

        # Main layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(mirror_layout)
        layout.addLayout(buttons_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # Install
    def install(self):
        self.save()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.close()

    # Reinstall
    def reinstall(self):
        self.save()
        shutil.rmtree(self.common.paths['tbb']['dir'])
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.close()

    # Save & Exit
    def save_exit(self):
        self.save()
        self.close()

    # Save settings
    def save(self):
        # Checkbox options
        self.common.settings['download_over_tor'] = self.tor_download_checkbox.isChecked()
        self.common.settings['force_en-US'] = self.force_en_checkbox.isChecked()
        self.common.settings['tor_socks_address'] = self.tor_addr.text()

        # Figure out the selected mirror
        self.common.settings['mirror'] = self.mirror.currentText()

        # Save them
        self.common.save_settings()
