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

import os, sys, platform, subprocess, locale, pickle, json, psutil

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
            self.paths['sig_url'] = '{0}torbrowser/'+tbb_version+'/'+tarball_filename+'.asc'
            self.paths['sig_file'] = tbb_cache+'/download/'+tarball_filename+'.asc'
            self.paths['sig_filename'] = tarball_filename+'.asc'
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
                'signing_keys': [os.path.join(SHARE, 'tor-browser-developers.asc')],
                'mirrors_txt': [os.path.join(SHARE, 'mirrors.txt'),
                                tbb_config+'/mirrors.txt'],
                'modem_sound': os.path.join(SHARE, 'modem.ogg'),
                'download_dir': tbb_cache+'/download',
                'gnupg_homedir': tbb_local+'/gnupg_homedir',
                'settings_file': tbb_config+'/settings.json',
                'settings_file_pickle': tbb_config+'/settings',
                'version_check_url': 'https://dist.torproject.org/torbrowser/update_2/release/Linux_x86_64-gcc3/x/en-US',
                'version_check_file': tbb_cache+'/download/release.xml',
                'tbb': {
                    'dir': tbb_local+'/tbb/'+self.architecture,
                    'dir_tbb': tbb_local+'/tbb/'+self.architecture+'/tor-browser_'+self.language,
                    'start': tbb_local+'/tbb/'+self.architecture+'/tor-browser_'+self.language+'/start-tor-browser.desktop',
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
        for key in self.paths['signing_keys']:
            subprocess.Popen(['/usr/bin/gpg', '--quiet', '--homedir', self.paths['gnupg_homedir'], '--import', key]).wait()

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
            'installed': False,
            'download_over_tor': False,
            'modem_sound': False,
            'mirror': self.default_mirror
        }

        if os.path.isfile(self.paths['settings_file']):
            settings = json.load(open(self.paths['settings_file']))
            resave = False

            # detect installed
            settings['installed'] = os.path.isfile(self.paths['tbb']['start'])

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

        # if settings file is still using old pickle format, convert to json
        elif os.path.isfile(self.paths['settings_file_pickle']):
            self.settings = pickle.load(open(self.paths['settings_file_pickle']))
            self.save_settings()
            os.remove(self.paths['settings_file_pickle'])
            self.load_settings()

        else:
            self.settings = default_settings
            self.save_settings()

    # save settings
    def save_settings(self):
        json.dump(self.settings, open(self.paths['settings_file'], 'w'))
        return True

