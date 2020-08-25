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


class TryStableException(Exception):
    pass


class TryDefaultMirrorException(Exception):
    pass


class TryForcingEnglishException(Exception):
    pass


class DownloadErrorException(Exception):
    pass


class LauncherCLI(object):
    """
    Launcher CLI.
    """
    def __init__(self, common, url_list):
        self.common = common

        self.url_list = url_list
        self.force_redownload = False

        # This is the current version of Tor Browser, which should get updated with every release
        self.min_version = '7.5.2'

        # Init launcher
        self.set_state(None, '', [])
        self.launch_cli = True

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
                            'extract'])

            if self.common.settings['download_over_tor']:
                print(_('Downloading over Tor'))

        else:
            # Tor Browser is already installed, but can't launch in CLI mode
            launch_message = "Tor Browser installed, run in GUI mode to launch."
            print(launch_message)

    # Set the current state of Tor Browser Launcher
    def set_state(self, cli, message, tasks):
        self.cli = cli
        self.cli_message = message
        self.cli_tasks = tasks
        self.cli_task_i = 0

    # Yes button clicked, based on the state decide what to do
    def yes_clicked(self):
        if self.cli == 'error_try_stable':
            self.try_stable()
        elif self.cli == 'error_try_default_mirror':
            self.try_default_mirror()
        elif self.cli == 'error_try_forcing_english':
            self.try_forcing_english()
        elif self.cli == 'error_try_tor':
            self.try_tor()

    # Start button clicked, begin tasks
    def start(self):
        # Start running tasks
        self.run_task()

    # Run the next task in the task list
    def run_task(self):
        if self.cli_task_i >= len(self.cli_tasks):
            self.close()
            return

        task = self.cli_tasks[self.cli_task_i]

        # Get ready for the next task
        self.cli_task_i += 1

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
                self.set_state('error', _("Error detecting Tor Browser version."), [])

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

        elif task == 'start_over':
            print(_('Starting download over again'))
            self.start_over()

    def download(self, name, url, path):
        # Download from the selected mirror
        mirror_url = url.format(self.common.settings['mirror']).encode()

        def download_complete():
            # Download complete, next task
            self.run_task()

        def download_error(cli, message):
            print(message)
            self.set_state(cli, message, [])

        show_progress = True

        # don't show progress for version check
        if name == 'version check':
            show_progress = False

        t = Download(self.common, mirror_url, path, show_progress)
        if t.run():
            download_complete()
        else:
            download_error('error_downloading', 'Error downloading: try again over Tor, or with English version')

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
        def success():
            print('Tor Browser tarball successfully verified')
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

            self.set_state('task', sigerror, ['start_over'])

        t = Verify(self.common)
        if t.run():
            success()
        else:
            error('')

    def extract(self):
        def success():
            print('Tor Browser successfully installed')
            self.run_task()

        def error():
            self.set_state(
                'task',
                _("Tor Browser Launcher doesn't understand the file format of {0}".format(self.common.paths['tarball_file'])),
                ['start_over']
            )

        t = Extract(self.common)
        if t.run():
            success()
        else:
            error()

    def check_min_version(self):
        installed_version = None
        for line in open(self.common.paths['tbb']['changelog'],'rb').readlines():
            if line.startswith(b'Tor Browser '):
                installed_version = line.split()[2].decode()
                break

        if self.min_version <= installed_version:
            return True

        return False

    # Start over and download TBB again
    def start_over(self):
        self.force_redownload = True  # Overwrite any existing file
        self.label.setText(_("Downloading Tor Browser over again."))
        self.cli_tasks = ['download_tarball', 'verify', 'extract', 'run']
        self.cli_task_i = 0
        self.start(None)

    def close(self):
        # Clear the download cache
        try:
            print('closing')
            os.remove(self.common.paths['version_check_file'])
            os.remove(self.common.paths['sig_file'])
            os.remove(self.common.paths['tarball_file'])
        except:
            pass


class Download(object):
    """
    Download a file in a separate thread.
    """
    def __init__(self, common, url, path, show_progress=True):
        self.common = common
        self.url = url
        self.path = path
        self.show_progress = show_progress

        # Use tor socks5 proxy, if enabled
        if self.common.settings['download_over_tor']:
            socks5_address = 'socks5h://{}'.format(self.common.settings['tor_socks_address'])
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
                        print(message)
                        return False

                    # Should we switch to English?
                    elif self.common.language != 'en-US' and not self.common.settings['force_en-US']:
                        message = (_("Download Error:") +
                                   " {0}\n\n" +
                                   _("Would you like to try the English version of Tor Browser instead?")).format(
                                       r.status_code
                                   )
                        print(message)
                        return False

                    else:
                        message = (_("Download Error:") + " {0}").format(r.status_code)
                        print(message)
                        return False

                    r.close()
                    return False

                # Start streaming the download
                total_bytes = int(r.headers.get('content-length'))
                bytes_so_far = 0

                suffix = ''
                if self.common.settings['download_over_tor']:
                    suffix = '(over Tor)'

                for data in r.iter_content(chunk_size=4096):
                    bytes_so_far += len(data)

                    # hack for misreported content-length header
                    if bytes_so_far > total_bytes:
                        total_bytes = bytes_so_far

                    f.write(data)
                    if self.show_progress:
                        self.print_progress_bar(bytes_so_far, total_bytes, suffix=suffix)

            except requests.exceptions.SSLError:
                message = _('Invalid SSL certificate for:\n{0}\n\nYou may be under attack.').format(self.url.decode())
                if not self.common.settings['download_over_tor']:
                    message += "\n\n" + _('Try the download again using Tor?')
                    print(message)
                else:
                    print(message)

                return False

            except requests.exceptions.ConnectionError:
                # Connection error
                if self.common.settings['download_over_tor']:
                    message = _("Error starting download:\n\n{0}\n\nTrying to download over Tor. "
                                "Are you sure Tor is configured correctly and running?").format(self.url.decode())
                    print(message)
                else:
                    message = _("Error starting download:\n\n{0}\n\nAre you connected to the internet?").format(
                        self.url.decode()
                    )
                    print(message)

                return False

        return True

    # from Greenstick's stackoverflow answer: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console#answer-34325723
    def print_progress_bar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()

class Verify(object):
    """
    Verify the signature
    """
    def __init__(self, common):
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
                        print(str(e))
                        return False
                    else:
                        raise Exception
                else:
                    return True

        try:
            # Try verifying
            return verify()
        except:
            # If it fails, refresh the keyring and try again
            self.common.refresh_keyring()
            return verify(True)


class Extract(object):
    """
    Extract the tarball in a separate thread
    """
    def __init__(self, common):
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

        return extracted
