import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from torbrowser_launcher.launcher import Launcher


class _Signal:
    def connect(self, callback):
        self.callback = callback

    def emit(self, *arguments):
        self.callback(*arguments)


class UpdateBeforeLaunchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.changelog = os.path.join(
            self.temporary_directory.name, "ChangeLog.txt"
        )
        with open(self.changelog, "wb") as changelog:
            changelog.write(b"Tor Browser 14.5.4\n")

        self.common = mock.Mock()
        self.common.settings = {
            "installed": True,
            "download_over_tor": False,
            "mirror": "https://dist.torproject.org/",
        }
        self.common.paths = {
            "icon_file": "",
            "version_check_url": "https://aus1.torproject.org/stable",
            "version_check_file": os.path.join(
                self.temporary_directory.name, "release.xml"
            ),
            "tbb": {
                "changelog": self.changelog,
                "start": "/tor-browser/start",
                "dir_tbb": "/tor-browser",
            },
        }

    def make_launcher(self, update_before_launch):
        with mock.patch.object(Launcher, "update"):
            return Launcher(self.common, self.app, [], update_before_launch)

    def write_metadata(self, advertised_version):
        with open(self.common.paths["version_check_file"], "w") as metadata:
            metadata.write(
                '<updates><update appVersion="{}" /></updates>'.format(
                    advertised_version
                )
            )

    def test_flagged_acceptable_installation_checks_fresh_metadata_before_run(self):
        launcher = self.make_launcher(update_before_launch=True)

        self.assertEqual(
            launcher.gui_tasks,
            ["download_version_check", "check_stable_version"],
        )
        with mock.patch.object(launcher, "download") as download:
            launcher.run_task()

        download.assert_called_once_with(
            "version check",
            self.common.paths["version_check_url"],
            self.common.paths["version_check_file"],
        )
        self.assertNotIn("run", launcher.gui_tasks[: launcher.gui_task_i])

    def test_unflagged_acceptable_installation_selects_run_without_metadata(self):
        launcher = self.make_launcher(update_before_launch=False)

        self.assertEqual(launcher.gui_tasks, ["run"])
        self.assertFalse(os.path.exists(self.common.paths["version_check_file"]))

    def test_equal_fresh_version_selects_run_without_installation(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.write_metadata("14.5.4")
        launcher.gui_task_i = 1

        with mock.patch.object(launcher, "update"):
            launcher.run_task()

        self.assertEqual(launcher.gui_tasks, ["run"])
        self.common.build_paths.assert_not_called()

    def test_newer_installed_version_logs_and_selects_run_without_downgrade(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.write_metadata("14.5.3")
        launcher.gui_task_i = 1
        output = StringIO()

        with mock.patch.object(launcher, "update"), redirect_stdout(output):
            launcher.run_task()

        self.assertEqual(launcher.gui_tasks, ["run"])
        self.assertIn("older than the installed version", output.getvalue())
        self.common.build_paths.assert_not_called()

    def test_advertised_version_below_minimum_does_not_trigger_downgrade(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.write_metadata("12.0")
        launcher.gui_task_i = 1

        with mock.patch.object(launcher, "update"):
            launcher.run_task()

        self.assertEqual(launcher.gui_tasks, ["run"])
        self.common.build_paths.assert_not_called()

    def test_failed_fresh_download_does_not_fall_back_to_cached_metadata(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.write_metadata("14.5.4")
        thread = mock.Mock(
            progress_update=_Signal(),
            download_complete=_Signal(),
            download_error=_Signal(),
        )

        with (
            mock.patch(
                "torbrowser_launcher.launcher.DownloadThread", return_value=thread
            ),
            mock.patch("torbrowser_launcher.launcher.time.sleep"),
        ):
            launcher.run_task()
        with mock.patch.object(launcher, "update"):
            thread.download_error.emit(
                "error_try_default_mirror", "Metadata download failed."
            )

        self.assertEqual(launcher.gui, "error")
        self.assertEqual(launcher.gui_tasks, [])
        self.common.build_paths.assert_not_called()

    def test_malformed_fresh_metadata_stops_before_run_or_installation(self):
        launcher = self.make_launcher(update_before_launch=True)
        with open(self.common.paths["version_check_file"], "w") as metadata:
            metadata.write("<updates>")
        launcher.gui_task_i = 1

        with mock.patch.object(launcher, "update"):
            launcher.run_task()

        self.assertEqual(launcher.gui, "error")
        self.assertEqual(launcher.gui_tasks, [])
        self.common.build_paths.assert_not_called()

    def test_malformed_installed_version_stops_flagged_invocation(self):
        with open(self.changelog, "wb") as changelog:
            changelog.write(b"Tor Browser definitely-not-a-version\n")

        launcher = self.make_launcher(update_before_launch=True)

        self.assertEqual(launcher.gui, "error")
        self.assertEqual(launcher.gui_tasks, [])
        self.common.build_paths.assert_not_called()

    def test_unreadable_installed_version_stops_after_fresh_check(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.write_metadata("14.5.4")
        launcher.gui_task_i = 1
        os.remove(self.changelog)

        with mock.patch.object(launcher, "update"):
            launcher.run_task()

        self.assertEqual(launcher.gui, "error")
        self.assertEqual(launcher.gui_tasks, [])
        self.common.build_paths.assert_not_called()


if __name__ == "__main__":
    unittest.main()
