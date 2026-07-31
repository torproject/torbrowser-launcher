import sys
import unittest
from unittest import mock

import torbrowser_launcher


class _Size:
    def width(self):
        return 1024

    def height(self):
        return 768


class _Screen:
    def size(self):
        return _Size()


class _Application:
    def primaryScreen(self):
        return _Screen()

    def exec_(self):
        return 0

    def setDesktopFileName(self, name):
        pass


class _Window:
    def size(self):
        return _Size()

    def move(self, x, y):
        pass

    def show(self):
        pass


class CommandLineTest(unittest.TestCase):
    def run_main(self, arguments):
        common = mock.Mock()
        common.settings = {"existing": "preference"}
        app = _Application()
        window = _Window()

        with (
            mock.patch.object(sys, "argv", ["torbrowser-launcher", *arguments]),
            mock.patch("builtins.open", mock.mock_open(read_data="1.0")),
            mock.patch.object(torbrowser_launcher, "Common", return_value=common),
            mock.patch.object(torbrowser_launcher, "Application", return_value=app),
            mock.patch.object(
                torbrowser_launcher, "Launcher", return_value=window
            ) as launcher,
            mock.patch.object(
                torbrowser_launcher, "Settings", return_value=window
            ) as settings,
            self.assertRaises(SystemExit) as exit_context,
        ):
            torbrowser_launcher.main()

        self.assertEqual(exit_context.exception.code, 0)
        return common, app, launcher, settings

    def test_update_before_launch_defaults_to_false_and_preserves_url(self):
        common, app, launcher, settings = self.run_main(["https://example.com/"])

        launcher.assert_called_once_with(
            common, app, ["https://example.com/"], False
        )
        settings.assert_not_called()

    def test_update_before_launch_is_passed_to_launcher_with_urls(self):
        common, app, launcher, settings = self.run_main(
            ["--update-before-launch", "https://example.com/", "about:blank"]
        )

        launcher.assert_called_once_with(
            common,
            app,
            ["https://example.com/", "about:blank"],
            True,
        )
        settings.assert_not_called()
        self.assertEqual(common.settings, {"existing": "preference"})

    def test_update_before_launch_cannot_be_combined_with_settings(self):
        with (
            mock.patch.object(
                sys,
                "argv",
                [
                    "torbrowser-launcher",
                    "--settings",
                    "--update-before-launch",
                ],
            ),
            mock.patch.object(torbrowser_launcher, "Launcher") as launcher,
            mock.patch.object(torbrowser_launcher, "Settings") as settings,
            self.assertRaises(SystemExit) as exit_context,
        ):
            torbrowser_launcher.main()

        self.assertEqual(exit_context.exception.code, 2)
        launcher.assert_not_called()
        settings.assert_not_called()

    def test_settings_mode_is_unchanged(self):
        common, app, launcher, settings = self.run_main(["--settings"])

        settings.assert_called_once_with(common, app)
        launcher.assert_not_called()


if __name__ == "__main__":
    unittest.main()
