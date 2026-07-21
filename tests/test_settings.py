import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from settings import DEFAULT_SETTINGS, normalize_settings, save_settings
from browser.internal_pages import INTERNAL_HOME_URL


class SettingsTests(unittest.TestCase):
    def test_personal_search_is_default(self):
        self.assertEqual(DEFAULT_SETTINGS["homepage"], INTERNAL_HOME_URL)
        self.assertEqual(DEFAULT_SETTINGS["default_search_engine"], "personal")
        self.assertEqual(DEFAULT_SETTINGS["fallback_search_engine"], "duckduckgo")
        self.assertEqual(DEFAULT_SETTINGS["search_results_limit"], 10)
        self.assertEqual(DEFAULT_SETTINGS["crawler_max_pages"], 75)
        self.assertEqual(DEFAULT_SETTINGS["crawler_max_depth"], 2)
        self.assertEqual(DEFAULT_SETTINGS["theme_mode"], "dark")
        self.assertEqual(DEFAULT_SETTINGS["theme_accent"], "cyber")

    def test_normalize_settings_clamps_numbers_and_theme_values(self):
        settings = normalize_settings(
            {
                "homepage": "   ",
                "default_search_engine": "bad",
                "fallback_search_engine": "bad",
                "search_results_limit": "500",
                "crawler_max_pages": "500",
                "crawler_max_depth": "99",
                "theme_mode": "bright",
                "theme_accent": "unknown",
                "custom_accent_color": "not-a-color",
            }
        )

        self.assertEqual(settings["homepage"], INTERNAL_HOME_URL)
        self.assertEqual(settings["default_search_engine"], "personal")
        self.assertEqual(settings["fallback_search_engine"], "duckduckgo")
        self.assertEqual(settings["search_results_limit"], 100)
        self.assertEqual(settings["crawler_max_pages"], 100)
        self.assertEqual(settings["crawler_max_depth"], 4)
        self.assertEqual(settings["theme_mode"], "dark")
        self.assertEqual(settings["theme"], "dark")
        self.assertEqual(settings["theme_accent"], "cyber")
        self.assertEqual(settings["custom_accent_color"], "#38BDF8")

    def test_save_settings_writes_normalized_json(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            settings_file = Path(temporary_directory) / "settings.json"

            saved_settings = save_settings(
                {
                    "theme_mode": "light",
                    "theme_accent": "custom",
                    "custom_accent_color": "#ff00aa",
                },
                file_path=settings_file,
            )

            self.assertEqual(saved_settings["theme_mode"], "light")
            self.assertEqual(saved_settings["theme_accent"], "custom")
            self.assertEqual(saved_settings["custom_accent_color"], "#FF00AA")
            self.assertIn('"theme_mode": "light"', settings_file.read_text())


if __name__ == "__main__":
    unittest.main()
