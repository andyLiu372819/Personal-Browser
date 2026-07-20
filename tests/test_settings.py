import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from settings import DEFAULT_SETTINGS
from browser.internal_pages import INTERNAL_HOME_URL


class SettingsTests(unittest.TestCase):
    def test_personal_search_is_default(self):
        self.assertEqual(DEFAULT_SETTINGS["homepage"], INTERNAL_HOME_URL)
        self.assertEqual(DEFAULT_SETTINGS["default_search_engine"], "personal")
        self.assertEqual(DEFAULT_SETTINGS["fallback_search_engine"], "duckduckgo")
        self.assertEqual(DEFAULT_SETTINGS["search_results_limit"], 10)
        self.assertEqual(DEFAULT_SETTINGS["crawler_max_pages"], 75)
        self.assertEqual(DEFAULT_SETTINGS["crawler_max_depth"], 2)


if __name__ == "__main__":
    unittest.main()
