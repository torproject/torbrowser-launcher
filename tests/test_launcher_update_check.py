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
    install_tasks = [
        "set_version",
        "download_sig",
        "download_tarball",
        "verify",
        "extract",
        "run",
    ]
    first_install_tasks = ["download_version_check", *install_tasks]

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
            "sig_file": os.path.join(self.temporary_directory.name, "browser.asc"),
            "tarball_file": os.path.join(
                self.temporary_directory.name, "browser.tar.xz"
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

    def fail_version_check(self, launcher):
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

    def select_required_update(self, launcher):
        self.write_metadata("14.5.5")
        launcher.gui_task_i = 1
        with mock.patch.object(launcher, "update"):
            launcher.run_task()

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

    def test_missing_installation_selects_first_install_tasks_with_or_without_flag(self):
        self.common.settings["installed"] = False

        for update_before_launch in (False, True):
            with self.subTest(update_before_launch=update_before_launch):
                launcher = self.make_launcher(update_before_launch)

                self.assertEqual(launcher.gui_tasks, self.first_install_tasks)

    def test_below_minimum_installation_selects_repair_tasks_with_or_without_flag(self):
        with open(self.changelog, "wb") as changelog:
            changelog.write(b"Tor Browser 12.0\n")

        for update_before_launch in (False, True):
            with self.subTest(update_before_launch=update_before_launch):
                launcher = self.make_launcher(update_before_launch)

                self.assertEqual(launcher.gui_tasks, self.first_install_tasks)

    def test_flagged_first_install_retains_version_check_recovery(self):
        self.common.settings["installed"] = False
        launcher = self.make_launcher(update_before_launch=True)

        self.fail_version_check(launcher)

        self.assertEqual(launcher.gui, "error_try_default_mirror")

    def test_equal_fresh_version_selects_run_without_installation(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.write_metadata("14.5.4")
        launcher.gui_task_i = 1

        with mock.patch.object(launcher, "update"):
            launcher.run_task()

        self.assertEqual(launcher.gui_tasks, ["run"])
        self.common.build_paths.assert_not_called()

    def test_older_acceptable_installation_selects_existing_installer_tasks(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.write_metadata("14.5.5")
        launcher.gui_task_i = 1

        with mock.patch.object(launcher, "update"):
            launcher.run_task()

        self.assertEqual(
            launcher.gui_tasks,
            self.install_tasks,
        )

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

        self.fail_version_check(launcher)

        self.assertEqual(launcher.gui, "error")
        self.assertEqual(launcher.gui_tasks, [])
        self.common.build_paths.assert_not_called()

    def test_flagged_required_update_download_failures_are_terminal(self):
        for name in ("signature", "tarball"):
            with self.subTest(name=name):
                launcher = self.make_launcher(update_before_launch=True)
                self.select_required_update(launcher)
                thread = mock.Mock(
                    progress_update=_Signal(),
                    download_complete=_Signal(),
                    download_error=_Signal(),
                )

                with (
                    mock.patch(
                        "torbrowser_launcher.launcher.DownloadThread",
                        return_value=thread,
                    ),
                    mock.patch("torbrowser_launcher.launcher.time.sleep"),
                    mock.patch.object(launcher, "update"),
                ):
                    launcher.download(name, "{}/download", "/tmp/download")
                    thread.download_error.emit(
                        "error_try_default_mirror", f"{name} download failed."
                    )

                self.assertEqual(launcher.gui, "error")
                self.assertEqual(launcher.gui_tasks, [])

    def test_flagged_required_update_verification_failure_is_terminal(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.select_required_update(launcher)
        thread = mock.Mock(error=_Signal(), success=_Signal())

        with (
            mock.patch(
                "torbrowser_launcher.launcher.VerifyThread", return_value=thread
            ),
            mock.patch("torbrowser_launcher.launcher.shutil.copyfile"),
            mock.patch("torbrowser_launcher.launcher.time.sleep"),
            mock.patch.object(launcher, "update"),
        ):
            launcher.verify()
            thread.error.emit("bad signature")

        self.assertEqual(launcher.gui, "error")
        self.assertEqual(launcher.gui_tasks, [])
        self.assertNotIn("Click Start", launcher.gui_message)

    def test_flagged_required_update_extraction_failure_is_terminal(self):
        launcher = self.make_launcher(update_before_launch=True)
        self.select_required_update(launcher)
        thread = mock.Mock(error=_Signal(), success=_Signal())

        with (
            mock.patch(
                "torbrowser_launcher.launcher.ExtractThread", return_value=thread
            ),
            mock.patch("torbrowser_launcher.launcher.time.sleep"),
            mock.patch.object(launcher, "update"),
        ):
            launcher.extract()
            thread.error.emit("bad archive")

        self.assertEqual(launcher.gui, "error")
        self.assertEqual(launcher.gui_tasks, [])

    def test_unflagged_verification_failure_retains_start_over(self):
        launcher = self.make_launcher(update_before_launch=False)
        thread = mock.Mock(error=_Signal(), success=_Signal())

        with (
            mock.patch(
                "torbrowser_launcher.launcher.VerifyThread", return_value=thread
            ),
            mock.patch("torbrowser_launcher.launcher.shutil.copyfile"),
            mock.patch("torbrowser_launcher.launcher.time.sleep"),
            mock.patch.object(launcher, "update"),
        ):
            launcher.verify()
            thread.error.emit("bad signature")

        self.assertEqual(launcher.gui, "task")
        self.assertEqual(launcher.gui_tasks, ["start_over"])
        self.assertIn("Click Start", launcher.gui_message)

    def test_unflagged_extraction_failure_retains_start_over(self):
        launcher = self.make_launcher(update_before_launch=False)
        thread = mock.Mock(error=_Signal(), success=_Signal())

        with (
            mock.patch(
                "torbrowser_launcher.launcher.ExtractThread", return_value=thread
            ),
            mock.patch("torbrowser_launcher.launcher.time.sleep"),
            mock.patch.object(launcher, "update"),
        ):
            launcher.extract()
            thread.error.emit("bad archive")

        self.assertEqual(launcher.gui, "task")
        self.assertEqual(launcher.gui_tasks, ["start_over"])

    def test_flagged_first_install_download_failure_retains_mirror_relaunch(self):
        self.common.settings["installed"] = False
        launcher = self.make_launcher(update_before_launch=True)
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
            mock.patch.object(launcher, "update"),
        ):
            launcher.download("signature", "{}/signature", "/tmp/signature")
            thread.download_error.emit(
                "error_try_default_mirror", "Signature download failed."
            )

        self.assertEqual(launcher.gui, "error_try_default_mirror")

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
