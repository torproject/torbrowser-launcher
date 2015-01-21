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

import os, sys, platform, subprocess, locale, pickle, psutil

import pygtk
pygtk.require('2.0')
import gtk

SHARE = os.getenv('TBL_SHARE', sys.prefix+'/share/torbrowser-launcher')

import gettext
gettext.install('torbrowser-launcher', os.path.join(SHARE, 'locale'))

from twisted.internet import gtk2reactor
gtk2reactor.install()

class Common:

    def __init__(self, tbl_version):
        print _('Initializing Tor Browser Launcher')
        self.tbl_version = tbl_version

        # initialize the app
        self.default_mirror = 'https://dist.torproject.org/'
        self.discover_arch_lang()
        self.build_paths()
        for d in self.paths['dirs']:
            self.mkdir(self.paths['dirs'][d])
        self.load_mirrors()
        self.load_settings()
        self.mkdir(self.paths['download_dir'])
        self.mkdir(self.paths['tbb']['dir'])
        self.init_gnupg()

        # allow buttons to have icons
        try:
            gtk_settings = gtk.settings_get_default()
            gtk_settings.props.gtk_button_images = True
        except:
            pass

    # discover the architecture and language
    def discover_arch_lang(self):
        # figure out the architecture
        self.architecture = 'x86_64' if '64' in platform.architecture()[0] else 'i686'

        # figure out the language
        available_languages = ['en-US', 'ar', 'de', 'es-ES', 'fa', 'fr', 'it', 'ko', 'nl', 'pl', 'pt-PT', 'ru', 'vi', 'zh-CN']
        default_locale = locale.getdefaultlocale()[0]
        if default_locale is None:
            self.language = 'en-US'
        else:
            self.language = default_locale.replace('_', '-')
            if self.language not in available_languages:
                self.language = self.language.split('-')[0]
                if self.language not in available_languages:
                    for l in available_languages:
                        if l[0:2] == self.language:
                            self.language = l
            # if language isn't available, default to english
            if self.language not in available_languages:
                self.language = 'en-US'

    # build all relevant paths
    def build_paths(self, tbb_version=None):
        homedir = os.getenv('HOME')
        if not homedir:
            homedir = '/tmp/.torbrowser-'+os.getenv('USER')
            if not os.path.exists(homedir):
                try:
                    os.mkdir(homedir, 0700)
                except:
                    self.set_gui('error', _("Error creating {0}").format(homedir), [], False)
        if not os.access(homedir, os.W_OK):
            self.set_gui('error', _("{0} is not writable").format(homedir), [], False)

        tbb_config = '{0}/.config/torbrowser'.format(homedir)
        tbb_cache = '{0}/.cache/torbrowser'.format(homedir)
        tbb_local = '{0}/.local/share/torbrowser'.format(homedir)
        old_tbb_data = '{0}/.torbrowser'.format(homedir)

        if tbb_version:
            # tarball filename
            if self.architecture == 'x86_64':
                arch = 'linux64'
            else:
                arch = 'linux32'
            tarball_filename = 'tor-browser-'+arch+'-'+tbb_version+'_'+self.language+'.tar.xz'

            # tarball
            self.paths['tarball_url'] = '{0}torbrowser/'+tbb_version+'/'+tarball_filename
            self.paths['tarball_file'] = tbb_cache+'/download/'+tarball_filename
            self.paths['tarball_filename'] = tarball_filename

            # sig
            self.paths['sha256_file'] = tbb_cache+'/download/sha256sums.txt'
            self.paths['sha256_sig_file'] = tbb_cache+'/download/sha256sums.txt.asc'
            self.paths['sha256_url'] = '{0}torbrowser/'+tbb_version+'/sha256sums.txt'
            self.paths['sha256_sig_url'] = '{0}torbrowser/'+tbb_version+'/sha256sums.txt.asc'
        else:
            self.paths = {
                'dirs': {
                    'config': tbb_config,
                    'cache': tbb_cache,
                    'local': tbb_local,
                },
                'old_data_dir': old_tbb_data,
                'tbl_bin': sys.argv[0],
                'icon_file': os.path.join(os.path.dirname(SHARE), 'pixmaps/torbrowser80.xpm'),
                'torproject_pem': os.path.join(SHARE, 'torproject.pem'),
                'signing_keys': [os.path.join(SHARE, 'erinn.asc'), os.path.join(SHARE, 'tor-browser-developers.asc')],
                'mirrors_txt': [os.path.join(SHARE, 'mirrors.txt'),
                                tbb_config+'/mirrors.txt'],
                'modem_sound': os.path.join(SHARE, 'modem.ogg'),
                'download_dir': tbb_cache+'/download',
                'gnupg_homedir': tbb_local+'/gnupg_homedir',
                'settings_file': tbb_config+'/settings',
                'update_check_url': 'https://www.torproject.org/projects/torbrowser/RecommendedTBBVersions',
                'update_check_file': tbb_cache+'/download/RecommendedTBBVersions',
                'tbb': {
                    'dir': tbb_local+'/tbb/'+self.architecture,
                    'start': tbb_local+'/tbb/'+self.architecture+'/tor-browser_'+self.language+'/start-tor-browser',
                    'versions': tbb_local+'/tbb/'+self.architecture+'/tor-browser_'+self.language+'/Browser/TorBrowser/Docs/sources/versions',
                },
            }

    # create a directory
    @staticmethod
    def mkdir(path):
        try:
            if not os.path.exists(path):
                os.makedirs(path, 0700)
                return True
        except:
            print _("Cannot create directory {0}").format(path)
            return False
        if not os.access(path, os.W_OK):
            print _("{0} is not writable").format(path)
            return False
        return True

    # if gnupg_homedir isn't set up, set it up
    def init_gnupg(self):
        if not os.path.exists(self.paths['gnupg_homedir']):
            print _('Creating GnuPG homedir'), self.paths['gnupg_homedir']
            self.mkdir(self.paths['gnupg_homedir'])
        self.import_keys()

    # import gpg keys
    def import_keys(self):
        print _('Importing keys')
        for key in self.paths['signing_keys']:
            subprocess.Popen(['/usr/bin/gpg', '--homedir', self.paths['gnupg_homedir'], '--import', key]).wait()

    # load mirrors
    def load_mirrors(self):
        self.mirrors = []
        for srcfile in self.paths['mirrors_txt']:
            if not os.path.exists(srcfile):
                continue
            for mirror in open(srcfile, 'r').readlines():
                if mirror.strip() not in self.mirrors:
                    self.mirrors.append(mirror.strip())

    # load settings
    def load_settings(self):
        default_settings = {
            'tbl_version': self.tbl_version,
            'installed_version': False,
            'latest_version': '0',
            'update_over_tor': True,
            'check_for_updates': False,
            'modem_sound': False,
            'last_update_check_timestamp': 0,
            'mirror': self.default_mirror,
            'accept_links': False
        }

        if os.path.isfile(self.paths['settings_file']):
            settings = pickle.load(open(self.paths['settings_file']))
            resave = False

            # settings migrations
            if settings['tbl_version'] <= '0.1.0':
                print '0.1.0 migration'
                settings['installed_version'] = settings['installed_version']['stable']
                settings['latest_version'] = settings['latest_version']['stable']
                resave = True

                # make new tbb folder
                self.mkdir(self.paths['tbb']['dir'])
                old_tbb_dir = self.paths['old_data_dir']+'/tbb/stable/'+self.architecture+'/tor-browser_'+self.language
                new_tbb_dir = self.paths['tbb']['dir']+'/tor-browser_'+self.language
                if os.path.isdir(old_tbb_dir):
                    os.rename(old_tbb_dir, new_tbb_dir)

            # make sure settings file is up-to-date
            for setting in default_settings:
                if setting not in settings:
                    settings[setting] = default_settings[setting]
                    resave = True

            # make sure the version is current
            if settings['tbl_version'] != self.tbl_version:
                settings['tbl_version'] = self.tbl_version
                resave = True

            self.settings = settings
            if resave:
                self.save_settings()

        else:
            self.settings = default_settings
            self.save_settings()

    # save settings
    def save_settings(self):
        pickle.dump(self.settings, open(self.paths['settings_file'], 'w'))
        return True

    # get the process id of a program
    @staticmethod
    def get_pid(bin_path, python=False):
        pid = None

        for p in psutil.process_iter():
            try:
                if p.pid != os.getpid():
                    exe = None
                    if python:
                        if len(p.cmdline) > 1:
                            if 'python' in p.cmdline[0]:
                                exe = p.cmdline[1]
                    else:
                        if len(p.cmdline) > 0:
                            exe = p.cmdline[0]

                    if exe == bin_path:
                        pid = p.pid

            except:
                pass

        return pid

    # bring program's x window to front
    @staticmethod
    def bring_window_to_front(pid):
        # figure out the window id
        win_id = None
        p = subprocess.Popen(['wmctrl', '-l', '-p'], stdout=subprocess.PIPE)
        for line in p.stdout.readlines():
            line_split = line.split()
            cur_win_id = line_split[0]
            cur_win_pid = int(line_split[2])
            if cur_win_pid == pid:
                win_id = cur_win_id

        # bring to front
        if win_id:
            subprocess.call(['wmctrl', '-i', '-a', win_id])
