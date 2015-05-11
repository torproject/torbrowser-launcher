"""
Tor Browser Launcher
https://github.com/micahflee/torbrowser-launcher/

Copyright (c) 2013-2014 Micah Lee <micah@micahflee.com>

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

import subprocess, time

import pygtk
pygtk.require('2.0')
import gtk

class Settings:
    def __init__(self, common):
        self.common = common

        # set up the window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(_("Tor Browser Launcher Settings"))
        self.window.set_icon_from_file(self.common.paths['icon_file'])
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_border_width(10)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)

        # build the rest of the UI
        self.box = gtk.VBox(False, 10)
        self.window.add(self.box)
        self.box.show()

        self.hbox = gtk.HBox(False, 10)
        self.box.pack_start(self.hbox, True, True, 0)
        self.hbox.show()

        self.settings_box = gtk.VBox(False, 10)
        self.hbox.pack_start(self.settings_box, True, True, 0)
        self.settings_box.show()

        self.labels_box = gtk.VBox(False, 10)
        self.hbox.pack_start(self.labels_box, True, True, 0)
        self.labels_box.show()

        # download over tor
        try:
            import txsocksx
            self.txsocks_found = True
        except ImportError:
            self.txsocks_found = False
        self.tor_update_checkbox = gtk.CheckButton(_("Download updates over Tor (recommended)"))
        if self.txsocks_found:
            self.tor_update_checkbox.set_tooltip_text(_("This option is only available when using a system wide Tor installation."))
        else:
            self.tor_update_checkbox.set_tooltip_text(_("This option requires the python-txsocksx package."))

        self.settings_box.pack_start(self.tor_update_checkbox, True, True, 0)
        if self.common.settings['update_over_tor'] and self.txsocks_found:
            self.tor_update_checkbox.set_active(True)
        else:
            self.tor_update_checkbox.set_active(False)

        if self.txsocks_found == False:
            self.tor_update_checkbox.set_sensitive(False)

        self.tor_update_checkbox.show()

        # check for updates
        self.update_checkbox = gtk.CheckButton(_("Check for updates next launch"))
        self.settings_box.pack_start(self.update_checkbox, True, True, 0)
        if self.common.settings['check_for_updates']:
            self.update_checkbox.set_active(True)
        else:
            self.update_checkbox.set_active(False)
        self.update_checkbox.show()

        # modem sound
        self.modem_checkbox = gtk.CheckButton(_("Play modem sound, because Tor is slow :]"))
        self.settings_box.pack_start(self.modem_checkbox, True, True, 0)

        try:
            import pygame
            if self.common.settings['modem_sound']:
                self.modem_checkbox.set_active(True)
            else:
                self.modem_checkbox.set_active(False)
        except ImportError:
            self.modem_checkbox.set_active(False)
            self.modem_checkbox.set_sensitive(False)
            self.modem_checkbox.set_tooltip_text(_("This option requires python-pygame to be installed"))
        self.modem_checkbox.show()

        # labels
        if(self.common.settings['installed_version']):
            self.label1 = gtk.Label(_('Installed version:\n{0}').format(self.common.settings['installed_version']))
        else:
            self.label1 = gtk.Label(_('Not installed'))
        self.label1.set_line_wrap(True)
        self.labels_box.pack_start(self.label1, True, True, 0)
        self.label1.show()

        if(self.common.settings['last_update_check_timestamp'] > 0):
            self.label1 = gtk.Label(_('Last checked for updates:\n{0}').format(time.strftime("%B %d, %Y %I:%M %P", time.gmtime(self.common.settings['last_update_check_timestamp']))))
        else:
            self.label1 = gtk.Label(_('Never checked for updates'))
        self.label1.set_line_wrap(True)
        self.labels_box.pack_start(self.label1, True, True, 0)
        self.label1.show()

        # mirrors
        self.mirrors_box = gtk.HBox(False, 10)
        self.box.pack_start(self.mirrors_box, True, True, 0)
        self.mirrors_box.show()

        self.mirrors_label = gtk.Label(_('Mirror'))
        self.mirrors_label.set_line_wrap(True)
        self.mirrors_box.pack_start(self.mirrors_label, True, True, 0)
        self.mirrors_label.show()

        self.mirrors = gtk.combo_box_new_text()
        for mirror in self.common.mirrors:
            self.mirrors.append_text(mirror)
        if self.common.settings['mirror'] in self.common.mirrors:
            self.mirrors.set_active(self.common.mirrors.index(self.common.settings['mirror']))
        else:
            self.mirrors.set_active(0)
        self.mirrors_box.pack_start(self.mirrors, True, True, 0)
        self.mirrors.show()

        # button box
        self.button_box = gtk.HButtonBox()
        self.button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        self.box.pack_start(self.button_box, True, True, 0)
        self.button_box.show()

        # save and launch button
        save_launch_image = gtk.Image()
        save_launch_image.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
        self.save_launch_button = gtk.Button(_("Launch Tor Browser"))
        self.save_launch_button.set_image(save_launch_image)
        self.save_launch_button.connect("clicked", self.save_launch, None)
        self.button_box.add(self.save_launch_button)
        self.save_launch_button.show()

        # save and exit button
        save_exit_image = gtk.Image()
        save_exit_image.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
        self.save_exit_button = gtk.Button(_("Save & Exit"))
        self.save_exit_button.set_image(save_exit_image)
        self.save_exit_button.connect("clicked", self.save_exit, None)
        self.button_box.add(self.save_exit_button)
        self.save_exit_button.show()

        # cancel button
        cancel_image = gtk.Image()
        cancel_image.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
        self.cancel_button = gtk.Button(_("Cancel"))
        self.cancel_button.set_image(cancel_image)
        self.cancel_button.connect("clicked", self.destroy, None)
        self.button_box.add(self.cancel_button)
        self.cancel_button.show()

        # show the window
        self.window.show()

        # start gtk
        gtk.main()

    # UI Callback for update over tor/use system tor
    def on_system_tor_clicked(self, event):
        if self.txsocks_found:
            value = self.system_tor_checkbox.get_active()
        else:
            value = False

        self.tor_update_checkbox.set_active(value)
        self.tor_update_checkbox.set_sensitive(value)

    # save and launch
    def save_launch(self, widget, data=None):
        self.save()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.destroy(False)

    # save and exit
    def save_exit(self, widget, data=None):
        self.save()
        self.destroy(False)

    # save settings
    def save(self):
        # checkbox options
        self.common.settings['update_over_tor'] = self.tor_update_checkbox.get_active()
        self.common.settings['check_for_updates'] = self.update_checkbox.get_active()
        self.common.settings['modem_sound'] = self.modem_checkbox.get_active()

        # figure out the selected mirror
        self.common.settings['mirror'] = self.common.mirrors[self.mirrors.get_active()]

        # save them
        self.common.save_settings()

    # exit
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()
