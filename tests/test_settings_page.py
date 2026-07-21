import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from browser.settings_page import render_settings_page


class SettingsPageTests(unittest.TestCase):
    def test_renders_settings_form(self):
        html = render_settings_page({})

        self.assertIn("Nexus Control", html)
        self.assertIn('action="personal-browser://settings/save"', html)
        self.assertIn('name="default_search_engine"', html)
        self.assertIn('name="theme_mode"', html)
        self.assertIn('name="theme_accent"', html)
        self.assertIn('name="custom_accent_color"', html)

    def test_renders_saved_message(self):
        html = render_settings_page({}, "Settings saved")

        self.assertIn("Settings saved", html)
        self.assertIn('role="status"', html)


if __name__ == "__main__":
    unittest.main()
