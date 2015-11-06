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

import os, subprocess, time, json, tarfile, hashlib, lzma, threading, re
from twisted.internet import reactor
from twisted.web.client import Agent, RedirectAgent, ResponseDone, ResponseFailed
from twisted.web.http_headers import Headers
from twisted.web.iweb import IPolicyForHTTPS
from twisted.internet.protocol import Protocol
from twisted.internet.ssl import CertificateOptions
from twisted.internet._sslverify import ClientTLSOptions
from twisted.internet.error import DNSLookupError
from zope.interface import implementer

import xml.etree.ElementTree as ET

import OpenSSL

import pygtk
pygtk.require('2.0')
import gtk

class TryStableException(Exception):
    pass

class TryDefaultMirrorException(Exception):
    pass

class DownloadErrorException(Exception):
    pass

class TorProjectCertificateOptions(CertificateOptions):
    def __init__(self, torproject_pem):
        CertificateOptions.__init__(self)
        self.torproject_ca = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(torproject_pem, 'r').read())

    def getContext(self, host, port):
        ctx = CertificateOptions.getContext(self)
        ctx.set_verify_depth(0)
        ctx.set_verify(OpenSSL.SSL.VERIFY_PEER | OpenSSL.SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verifyHostname)
        return ctx

    def verifyHostname(self, connection, cert, errno, depth, preverifyOK):
        return cert.digest('sha256') == self.torproject_ca.digest('sha256')

@implementer(IPolicyForHTTPS)
class TorProjectPolicyForHTTPS:
    def __init__(self, torproject_pem):
        self.torproject_pem = torproject_pem

    def creatorForNetloc(self, hostname, port):
        certificateOptions = TorProjectCertificateOptions(self.torproject_pem)
        return ClientTLSOptions(hostname.decode('utf-8'),
                                certificateOptions.getContext(hostname, port))

class Launcher:
    def __init__(self, common, url_list):
        self.common = common
        self.url_list = url_list

        # init launcher
        self.set_gui(None, '', [])
        self.launch_gui = True
        self.common.build_paths(self.common.settings['latest_version'])

        if self.common.settings['update_over_tor']:
            try:
                import txsocksx
                print _('Updating over Tor')
            except ImportError:
                md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, _("The python-txsocksx package is missing, downloads will not happen over tor"))
                md.set_position(gtk.WIN_POS_CENTER)
                md.run()
                md.destroy()
                self.common.settings['update_over_tor'] = False
                self.common.save_settings()

        # is firefox already running?
        if self.common.settings['installed_version']:
            firefox_pid = self.common.get_pid('./Browser/firefox')
            if firefox_pid:
                print _('Firefox is open, bringing to focus')
                # bring firefox to front
                self.common.bring_window_to_front(firefox_pid)
                return

        # check for updates?
        check_for_updates = False
        if self.common.settings['check_for_updates']:
            check_for_updates = True

        if not check_for_updates:
            # how long was it since the last update check?
            # 86400 seconds = 24 hours
            current_timestamp = int(time.time())
            if current_timestamp - self.common.settings['last_update_check_timestamp'] >= 86400:
                check_for_updates = True

        if check_for_updates:
            # check for update
            print 'Checking for update'
            self.set_gui('task', _("Checking for Tor Browser update."),
                         ['download_update_check',
                          'attempt_update'])
        else:
            # no need to check for update
            print _('Checked for update within 24 hours, skipping')
            self.start_launcher()

        if self.launch_gui:
            # set up the window
            self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.window.set_title(_("Tor Browser"))
            self.window.set_icon_from_file(self.common.paths['icon_file'])
            self.window.set_position(gtk.WIN_POS_CENTER)
            self.window.set_border_width(10)
            self.window.connect("delete_event", self.delete_event)
            self.window.connect("destroy", self.destroy)

            # build the rest of the UI
            self.build_ui()

    # download or run TBB
    def start_launcher(self):
        # is TBB already installed?
        latest_version = self.common.settings['latest_version']
        installed_version = self.common.settings['installed_version']

        # verify installed version for newer versions of TBB (#58)
        if installed_version >= '3.0':
            versions_filename = self.common.paths['tbb']['versions']
            if os.path.exists(versions_filename):
                for line in open(versions_filename):
                    if 'TORBROWSER_VERSION' in line:
                        installed_version = line.lstrip('TORBROWSER_VERSION=').strip()

        start = self.common.paths['tbb']['start']
        if os.path.isfile(start) and os.access(start, os.X_OK):
            self.set_gui('task', _("testing verify"),
                         ['verify',
                          'extract',
                          'run'])
            return

            if installed_version == latest_version:
                print _('Latest version of TBB is installed, launching')
                # current version of tbb is installed, launch it
                self.run(False)
                self.launch_gui = False
            elif installed_version < latest_version:
                print _('TBB is out of date, attempting to upgrade to {0}'.format(latest_version))
                # there is a tbb upgrade available
                self.set_gui('task', _("Your Tor Browser is out of date. Upgrading from {0} to {1}.".format(installed_version, latest_version)),
                             ['download_sig',
                              'download_tarball',
                              'verify',
                              'extract',
                              'run'])
            else:
                # for some reason the installed tbb is newer than the current version?
                self.set_gui('error', _("Something is wrong. The version of Tor Browser Bundle you have installed is newer than the current version?"), [])

        # not installed
        else:
            print _('TBB is not installed, attempting to install {0}'.format(latest_version))
            self.set_gui('task', _("Downloading and installing Tor Browser for the first time."),
                         ['download_sig',
                          'download_tarball',
                          'verify',
                          'extract',
                          'run'])

    # there are different GUIs that might appear, this sets which one we want
    def set_gui(self, gui, message, tasks, autostart=True):
        self.gui = gui
        self.gui_message = message
        self.gui_tasks = tasks
        self.gui_task_i = 0
        self.gui_autostart = autostart

    # set all gtk variables to False
    def clear_ui(self):
        if hasattr(self, 'box') and hasattr(self.box, 'destroy'):
            self.box.destroy()
        self.box = False

        self.label = False
        self.progressbar = False
        self.button_box = False
        self.start_button = False
        self.exit_button = False

    # build the application's UI
    def build_ui(self):
        self.clear_ui()

        self.box = gtk.VBox(False, 20)
        self.window.add(self.box)

        if 'error' in self.gui:
            # labels
            self.label = gtk.Label(self.gui_message)
            self.label.set_line_wrap(True)
            self.box.pack_start(self.label, True, True, 0)
            self.label.show()

            # button box
            self.button_box = gtk.HButtonBox()
            self.button_box.set_layout(gtk.BUTTONBOX_SPREAD)
            self.box.pack_start(self.button_box, True, True, 0)
            self.button_box.show()

            if self.gui != 'error':
                # yes button
                yes_image = gtk.Image()
                yes_image.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
                self.yes_button = gtk.Button("Yes")
                self.yes_button.set_image(yes_image)
                if self.gui == 'error_try_stable':
                    self.yes_button.connect("clicked", self.try_stable, None)
                elif self.gui == 'error_try_default_mirror':
                    self.yes_button.connect("clicked", self.try_default_mirror, None)
                elif self.gui == 'error_try_tor':
                    self.yes_button.connect("clicked", self.try_tor, None)
                self.button_box.add(self.yes_button)
                self.yes_button.show()

            # exit button
            exit_image = gtk.Image()
            exit_image.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
            self.exit_button = gtk.Button("Exit")
            self.exit_button.set_image(exit_image)
            self.exit_button.connect("clicked", self.destroy, None)
            self.button_box.add(self.exit_button)
            self.exit_button.show()

        elif self.gui == 'task':
            # label
            self.label = gtk.Label(self.gui_message)
            self.label.set_line_wrap(True)
            self.box.pack_start(self.label, True, True, 0)
            self.label.show()

            # progress bar
            self.progressbar = gtk.ProgressBar(adjustment=None)
            self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
            self.progressbar.set_pulse_step(0.01)
            self.box.pack_start(self.progressbar, True, True, 0)

            # button box
            self.button_box = gtk.HButtonBox()
            self.button_box.set_layout(gtk.BUTTONBOX_SPREAD)
            self.box.pack_start(self.button_box, True, True, 0)
            self.button_box.show()

            # start button
            start_image = gtk.Image()
            start_image.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)
            self.start_button = gtk.Button(_("Start"))
            self.start_button.set_image(start_image)
            self.start_button.connect("clicked", self.start, None)
            self.button_box.add(self.start_button)
            if not self.gui_autostart:
                self.start_button.show()

            # exit button
            exit_image = gtk.Image()
            exit_image.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
            self.exit_button = gtk.Button(_("Exit"))
            self.exit_button.set_image(exit_image)
            self.exit_button.connect("clicked", self.destroy, None)
            self.button_box.add(self.exit_button)
            self.exit_button.show()

        self.box.show()
        self.window.show()

        if self.gui_autostart:
            self.start(None)

    # start button clicked, begin tasks
    def start(self, widget, data=None):
        # disable the start button
        if self.start_button:
            self.start_button.set_sensitive(False)

        # start running tasks
        self.run_task()

    # run the next task in the task list
    def run_task(self):
        self.refresh_gtk()

        if self.gui_task_i >= len(self.gui_tasks):
            self.destroy(False)
            return

        task = self.gui_tasks[self.gui_task_i]

        # get ready for the next task
        self.gui_task_i += 1

        if task == 'download_update_check':
            print _('Downloading'), self.common.paths['update_check_url']
            self.download('update check', self.common.paths['update_check_url'], self.common.paths['update_check_file'])

        if task == 'attempt_update':
            print _('Checking to see if update is needed')
            self.attempt_update()

        elif task == 'download_sig':
            print _('Downloading'), self.common.paths['sig_url'].format(self.common.settings['mirror'])
            self.download('signature', self.common.paths['sig_url'], self.common.paths['sig_file'])

        elif task == 'download_tarball':
            print _('Downloading'), self.common.paths['tarball_url'].format(self.common.settings['mirror'])
            self.download('tarball', self.common.paths['tarball_url'], self.common.paths['tarball_file'])

        elif task == 'verify':
            print _('Verifying signature')
            self.verify()

        elif task == 'extract':
            print _('Extracting'), self.common.paths['tarball_filename']
            self.extract()

        elif task == 'run':
            print _('Running'), self.common.paths['tbb']['start']
            self.run()

        elif task == 'start_over':
            print _('Starting download over again')
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
                        raise TryDefaultMirrorException(_("Download Error: {0} {1}\n\nYou are currently using a non-default mirror:\n{2}\n\nWould you like to switch back to the default?").format(response.code, response.phrase, common.settings['mirror']))
                    else:
                        raise DownloadErrorException(_("Download Error: {0} {1}").format(response.code, response.phrase))

            def dataReceived(self, bytes):
                self.file.write(bytes)
                self.so_far += len(bytes)
                percent = float(self.so_far) / float(self.total)
                self.progress.set_fraction(percent)
                amount = float(self.so_far)
                units = "bytes"
                for (size, unit) in [(1024 * 1024, "MiB"), (1024, "KiB")]:
                    if amount > size:
                        units = unit
                        amount = amount / float(size)
                        break

                self.progress.set_text(_('Downloaded')+(' %2.1f%% (%2.1f %s)' % ((percent * 100.0), amount, units)))

            def connectionLost(self, reason):
                self.all_done(reason)

        if hasattr(self, 'current_download_url'):
            url = self.current_download_url
        else:
            url = None

        dl = FileDownloader(self.common, self.file_download, url, response.length, self.progressbar, self.response_finished)
        response.deliverBody(dl)

    def response_finished(self, msg):
        if msg.check(ResponseDone):
            self.file_download.close()
            delattr(self, 'current_download_path')
            delattr(self, 'current_download_url')

            # next task!
            self.run_task()

        else:
            print "FINISHED", msg
            ## FIXME handle errors

    def download_error(self, f):
        print _("Download error:"), f.value, type(f.value)

        if isinstance(f.value, TryStableException):
            f.trap(TryStableException)
            self.set_gui('error_try_stable', str(f.value), [], False)

        elif isinstance(f.value, TryDefaultMirrorException):
            f.trap(TryDefaultMirrorException)
            self.set_gui('error_try_default_mirror', str(f.value), [], False)

        elif isinstance(f.value, DownloadErrorException):
            f.trap(DownloadErrorException)
            self.set_gui('error', str(f.value), [], False)

        elif isinstance(f.value, DNSLookupError):
            f.trap(DNSLookupError)
            if common.settings['mirror'] != common.default_mirror:
                self.set_gui('error_try_default_mirror', _("DNS Lookup Error\n\nYou are currently using a non-default mirror:\n{0}\n\nWould you like to switch back to the default?").format(common.settings['mirror']), [], False)
            else:
                self.set_gui('error', str(f.value), [], False)

        elif isinstance(f.value, ResponseFailed):
            for reason in f.value.reasons:
                if isinstance(reason.value, OpenSSL.SSL.Error):
                    # TODO: add the ability to report attack by posting bug to trac.torproject.org
                    if not self.common.settings['update_over_tor']:
                        self.set_gui('error_try_tor', _('The SSL certificate served by https://www.torproject.org is invalid! You may be under attack. Try the download again using Tor?'), [], False)
                    else:
                        self.set_gui('error', _('The SSL certificate served by https://www.torproject.org is invalid! You may be under attack.'), [], False)

        else:
            self.set_gui('error', _("Error starting download:\n\n{0}\n\nAre you connected to the internet?").format(f.value), [], False)

        self.build_ui()

    def download(self, name, url, path):
        # keep track of current download
        self.current_download_path = path
        self.current_download_url = url

        # initialize the progress bar
        mirror_url = url.format(self.common.settings['mirror'])
        self.progressbar.set_fraction(0)
        self.progressbar.set_text(_('Downloading {0}').format(name))
        self.progressbar.show()
        self.refresh_gtk()

        if self.common.settings['update_over_tor']:
            from twisted.internet.endpoints import TCP4ClientEndpoint
            from txsocksx.http import SOCKS5Agent

            torEndpoint = TCP4ClientEndpoint(reactor, '127.0.0.1', 9050)

            # default mirror gets certificate pinning, only for requests that use the mirror
            if self.common.settings['mirror'] == self.common.default_mirror and '{0}' in url:
                agent = SOCKS5Agent(reactor, TorProjectPolicyForHTTPS(self.common.paths['torproject_pem']), proxyEndpoint=torEndpoint)
            else:
                agent = SOCKS5Agent(reactor, proxyEndpoint=torEndpoint)
        else:
            if self.common.settings['mirror'] == self.common.default_mirror and '{0}' in url:
                agent = Agent(reactor, TorProjectPolicyForHTTPS(self.common.paths['torproject_pem']))
            else:
                agent = Agent(reactor)

        # actually, agent needs to follow redirect
        agent = RedirectAgent(agent)

        # start the request
        d = agent.request('GET', mirror_url,
                          Headers({'User-Agent': ['torbrowser-launcher']}),
                          None)

        self.file_download = open(path, 'w')
        d.addCallback(self.response_received).addErrback(self.download_error)

        if not reactor.running:
            reactor.run()

    def try_default_mirror(self, widget, data=None):
        # change mirror to default and relaunch TBL
        self.common.settings['mirror'] = self.common.default_mirror
        self.common.save_settings()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.destroy(False)

    def try_tor(self, widget, data=None):
        # set update_over_tor to true and relaunch TBL
        self.common.settings['update_over_tor'] = True
        self.common.save_settings()
        subprocess.Popen([self.common.paths['tbl_bin']])
        self.destroy(False)

    def get_stable_version(self):
        tree = ET.parse(self.common.paths['update_check_file'])
        for up in tree.getroot():
            if up.tag == 'update' and up.attrib['appVersion']:
                return up.attrib['appVersion']
        return None

    def attempt_update(self):
        # load the update check file
        try:
            latest = self.get_stable_version()
            if latest:
                latest = str(latest)

                self.common.settings['latest_version'] = latest
                self.common.settings['last_update_check_timestamp'] = int(time.time())
                self.common.settings['check_for_updates'] = False
                self.common.save_settings()
                self.common.build_paths(self.common.settings['latest_version'])
                self.start_launcher()

            else:
                # failed to find the latest version
                self.set_gui('error', _("Error checking for updates."), [], False)

        except:
            # not a valid JSON object
            self.set_gui('error', _("Error checking for updates."), [], False)

        # now start over
        self.clear_ui()
        self.build_ui()

    def verify(self):
        # initialize the progress bar
        self.progressbar.set_fraction(0)
        self.progressbar.set_text(_('Verifying Signature'))
        self.progressbar.show()

        # verify the PGP signature
        verified = False
        FNULL = open(os.devnull, 'w')
        p = subprocess.Popen(['/usr/bin/gpg', '--homedir', self.common.paths['gnupg_homedir'], '--verify', self.common.paths['sig_file']], stdout=FNULL, stderr=subprocess.STDOUT)
        self.pulse_until_process_exits(p)
        if p.returncode == 0:
            verified = True

        if verified:
            self.run_task()
        else:
            # TODO: add the ability to report attack by posting bug to trac.torproject.org
            self.set_gui('task', _("SIGNATURE VERIFICATION FAILED!\n\nYou might be under attack, or there might just be a networking problem. Click Start try the download again."), ['start_over'], False)
            self.clear_ui()
            self.build_ui()

            if not reactor.running:
                reactor.run()

    def extract(self):
        # initialize the progress bar
        self.progressbar.set_fraction(0)
        self.progressbar.set_text(_('Installing'))
        self.progressbar.show()
        self.refresh_gtk()

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
            self.set_gui('task', _("Tor Browser Launcher doesn't understand the file format of {0}".format(self.common.paths['tarball_file'])), ['start_over'], False)
            self.clear_ui()
            self.build_ui()
            return

        # installation is finished, so save installed_version
        self.common.settings['installed_version'] = self.common.settings['latest_version']
        self.common.save_settings()

        self.run_task()

    def run(self, run_next_task=True):
        # play modem sound?
        if self.common.settings['modem_sound']:
            def play_modem_sound():
                try:
                    import pygame
                    pygame.mixer.init()
                    sound = pygame.mixer.Sound(self.common.paths['modem_sound'])
                    sound.play()
                    time.sleep(10)
                except ImportError:
                    md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, _("The python-pygame package is missing, the modem sound is unavailable."))
                    md.set_position(gtk.WIN_POS_CENTER)
                    md.run()
                    md.destroy()

            t = threading.Thread(target=play_modem_sound)
            t.start()

        # hide the TBL window (#151)
        if hasattr(self, 'window'):
            self.window.hide()
            while gtk.events_pending():
                gtk.main_iteration_do(True)

        # run Tor Browser
        subprocess.call([self.common.paths['tbb']['start']], cwd=self.common.paths['tbb']['dir_tbb'])

        if run_next_task:
            self.run_task()

    # make the progress bar pulse until process p (a Popen object) finishes
    def pulse_until_process_exits(self, p):
        while p.poll() is None:
            time.sleep(0.01)
            self.progressbar.pulse()
            self.refresh_gtk()

    # start over and download TBB again
    def start_over(self):
        self.label.set_text(_("Downloading Tor Browser Bundle over again."))
        self.gui_tasks = ['download_tarball', 'verify', 'extract', 'run']
        self.gui_task_i = 0
        self.start(None)

    # refresh gtk
    def refresh_gtk(self):
        while gtk.events_pending():
            gtk.main_iteration(False)

    # exit
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        if hasattr(self, 'file_download'):
            self.file_download.close()
        if hasattr(self, 'current_download_path'):
            os.remove(self.current_download_path)
            delattr(self, 'current_download_path')
            delattr(self, 'current_download_url')
        if reactor.running:
            reactor.stop()
