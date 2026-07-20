import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from search_engine import (
    DEFAULT_EXTERNAL_SEARCH_ENGINE,
    PERSONAL_SEARCH_ENGINE,
    build_url_from_input,
    looks_like_url,
    uses_personal_search,
)


class SearchRoutingTests(unittest.TestCase):
    def test_keeps_complete_http_url(self):
        url = build_url_from_input("https://example.com/page")

        self.assertEqual(url, "https://example.com/page")

    def test_adds_https_to_domain(self):
        url = build_url_from_input("example.com")

        self.assertTrue(looks_like_url("example.com"))
        self.assertEqual(url, "https://example.com")

    def test_builds_search_engine_query(self):
        url = build_url_from_input("personal search engine")

        self.assertFalse(looks_like_url("personal search engine"))
        self.assertEqual(
            url,
            "https://duckduckgo.com/?q=personal+search+engine",
        )

    def test_unknown_external_engine_falls_back_to_duckduckgo(self):
        url = build_url_from_input("personal search engine", "unknown")

        self.assertEqual(
            url,
            "https://duckduckgo.com/?q=personal+search+engine",
        )

    def test_personal_search_engine_is_named(self):
        self.assertEqual(PERSONAL_SEARCH_ENGINE, "personal")
        self.assertEqual(DEFAULT_EXTERNAL_SEARCH_ENGINE, "duckduckgo")
        self.assertTrue(uses_personal_search("personal"))
        self.assertFalse(uses_personal_search("duckduckgo"))


if __name__ == "__main__":
    unittest.main()
