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
import platform
import subprocess
import locale
import pickle
import json
import re
import gettext
import gpg

SHARE = os.getenv('TBL_SHARE', sys.prefix + '/share') + '/torbrowser-launcher'

gettext.install('torbrowser-launcher')

# We're looking for output which:
#
#  1. The first portion must be `[GNUPG:] IMPORT_OK`
#  2. The second must be an integer between [0, 15], inclusive
#  3. The third must be an uppercased hex-encoded 160-bit fingerprint
gnupg_import_ok_pattern = re.compile(
    b"(\[GNUPG\:\]) (IMPORT_OK) ([0-9]|[1]?[0-5]) ([A-F0-9]{40})")


class Common(object):
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

    # discover the architecture and language
    def discover_arch_lang(self):
        # figure out the architecture
        self.architecture = 'x86_64' if '64' in platform.architecture()[0] else 'i686'

        # figure out the language
        available_languages = ['ar', 'ca', 'da', 'de', 'en-US', 'es-ES', 'fa', 'fr', 'ga-IE', 'he', 'id', 'is', 'it', 'ja', 'ko', 'nb-NO', 'nl', 'pl', 'pt-BR', 'ru', 'sv-SE', 'tr', 'vi', 'zh-CN', 'zh-TW']
        default_locale = locale.getlocale()[0]
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
                    os.mkdir(homedir, 0o700)
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

            if hasattr(self, 'settings') and self.settings['force_en-US']:
                language = 'en-US'
            else:
                language = self.language
            tarball_filename = 'tor-browser-' + arch + '-' + tbb_version + '_' + language + '.tar.xz'

            # tarball
            self.paths['tarball_url'] = '{0}torbrowser/' + tbb_version + '/' + tarball_filename
            self.paths['tarball_file'] = tbb_cache + '/download/' + tarball_filename
            self.paths['tarball_filename'] = tarball_filename

            # sig
            self.paths['sig_url'] = '{0}torbrowser/' + tbb_version + '/' + tarball_filename + '.asc'
            self.paths['sig_file'] = tbb_cache + '/download/' + tarball_filename + '.asc'
            self.paths['sig_filename'] = tarball_filename + '.asc'
        else:
            self.paths = {
                'dirs': {
                    'config': tbb_config,
                    'cache': tbb_cache,
                    'local': tbb_local,
                },
                'old_data_dir': old_tbb_data,
                'tbl_bin': sys.argv[0],
                'icon_file': os.path.join(os.path.dirname(SHARE), 'pixmaps/torbrowser.png'),
                'torproject_pem': os.path.join(SHARE, 'torproject.pem'),
                'keyserver_ca': os.path.join(SHARE, 'sks-keyservers.netCA.pem'),
                'signing_keys': {
                    'tor_browser_developers': os.path.join(SHARE, 'tor-browser-developers.asc')
                },
                'mirrors_txt': [os.path.join(SHARE, 'mirrors.txt'),
                                tbb_config + '/mirrors.txt'],
                'download_dir': tbb_cache + '/download',
                'gnupg_homedir': tbb_local + '/gnupg_homedir',
                'settings_file': tbb_config + '/settings.json',
                'settings_file_pickle': tbb_config + '/settings',
                'version_check_url': 'https://aus1.torproject.org/torbrowser/update_3/release/Linux_x86_64-gcc3/x/en-US',
                'version_check_file': tbb_cache + '/download/release.xml',
                'tbb': {
                    'changelog': tbb_local + '/tbb/' + self.architecture + '/tor-browser_' +
                                 self.language + '/Browser/TorBrowser/Docs/ChangeLog.txt',
                    'dir': tbb_local + '/tbb/' + self.architecture,
                    'dir_tbb': tbb_local + '/tbb/' + self.architecture + '/tor-browser_' + self.language,
                    'start': tbb_local + '/tbb/' + self.architecture + '/tor-browser_' +
                             self.language + '/start-tor-browser.desktop'
                },
            }

        # Add the expected fingerprint for imported keys:
        self.fingerprints = {
            'tor_browser_developers': 'EF6E286DDA85EA2A4BA7DE684E2C6E8793298290'
        }

    # create a directory
    @staticmethod
    def mkdir(path):
        try:
            if not os.path.exists(path):
                os.makedirs(path, 0o700)
                return True
        except:
            print(_("Cannot create directory {0}").format(path))
            return False
        if not os.access(path, os.W_OK):
            print(_("{0} is not writable").format(path))
            return False
        return True

    # if gnupg_homedir isn't set up, set it up
    def init_gnupg(self):
        if not os.path.exists(self.paths['gnupg_homedir']):
            print(_('Creating GnuPG homedir'), self.paths['gnupg_homedir'])
            self.mkdir(self.paths['gnupg_homedir'])
        self.import_keys()

    def refresh_keyring(self, fingerprint=None):
        if fingerprint is not None:
            print('Refreshing local keyring... Missing key: ' + fingerprint)
        else:
            print('Refreshing local keyring...')

        p = subprocess.Popen(['/usr/bin/gpg2', '--status-fd', '2',
                              '--homedir', self.paths['gnupg_homedir'],
                              '--keyserver', 'hkps://hkps.pool.sks-keyservers.net',
                              '--keyserver-options', 'ca-cert-file=' + self.paths['keyserver_ca']
                              + ',include-revoked,no-honor-keyserver-url,no-honor-pka-record',
                              '--refresh-keys'], stderr=subprocess.PIPE)
        p.wait()

        for output in p.stderr.readlines():
            match = gnupg_import_ok_pattern.match(output)
            if match and match.group(2) == 'IMPORT_OK':
                fingerprint = str(match.group(4))
                if match.group(3) == '0':
                    print('Keyring refreshed successfully...')
                    print('  No key updates for key: ' + fingerprint)
                elif match.group(3) == '4':
                    print('Keyring refreshed successfully...')
                    print('  New signatures for key: ' + fingerprint)
                else:
                    print('Keyring refreshed successfully...')

    def import_key_and_check_status(self, key):
        """Import a GnuPG key and check that the operation was successful.
        :param str key: A string specifying the key's filepath from
            ``Common.paths``
        :rtype: bool
        :returns: ``True`` if the key is now within the keyring (or was
            previously and hasn't changed). ``False`` otherwise.
        """
        with gpg.Context() as c:
            c.set_engine_info(gpg.constants.protocol.OpenPGP, home_dir=self.paths['gnupg_homedir'])

            impkey = self.paths['signing_keys'][key]
            try:
                c.op_import(gpg.Data(file=impkey))
            except:
                return False
            else:
                result = c.op_import_result()
                if result and self.fingerprints[key] in result.imports[0].fpr:
                    return True
                else:
                    return False

    # import gpg keys
    def import_keys(self):
        """Import all GnuPG keys.
        :rtype: bool
        :returns: ``True`` if all keys were successfully imported; ``False``
            otherwise.
        """
        keys = ['tor_browser_developers', ]
        all_imports_succeeded = True

        for key in keys:
            imported = self.import_key_and_check_status(key)
            if not imported:
                print(_('Could not import key with fingerprint: %s.'
                        % self.fingerprints[key]))
                all_imports_succeeded = False

        if not all_imports_succeeded:
            print(_('Not all keys were imported successfully!'))

        return all_imports_succeeded

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
            'tor_socks_address': '127.0.0.1:9050',
            'mirror': self.default_mirror,
            'force_en-US': False,
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

            # make sure tor_socks_address doesn't start with 'tcp:'
            if settings['tor_socks_address'].startswith('tcp:'):
                settings['tor_socks_address'] = settings['tor_socks_address'][4:]
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
