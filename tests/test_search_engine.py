import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from search_engine import build_url_from_input, looks_like_url


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


if __name__ == "__main__":
    unittest.main()
