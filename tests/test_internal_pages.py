import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import browser.internal_pages as internal_pages


class InternalPagesTests(unittest.TestCase):
    def setUp(self):
        self.original_internal_pages_dir = internal_pages.INTERNAL_PAGES_DIR

    def tearDown(self):
        internal_pages.INTERNAL_PAGES_DIR = self.original_internal_pages_dir

    def test_write_internal_page_saves_html_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            internal_pages.INTERNAL_PAGES_DIR = Path(temporary_directory)

            page_path = internal_pages.write_internal_page(
                "history",
                "<html>history</html>",
            )

            self.assertEqual(page_path.name, "history.html")
            self.assertEqual(page_path.read_text(encoding="utf-8"), "<html>history</html>")

    def test_identifies_generated_internal_page_url(self):
        self.assertTrue(
            internal_pages.is_internal_page_url(
                "file:///C:/Project/Personal%20Browser/data/internal_pages/history.html"
            )
        )
        self.assertFalse(internal_pages.is_internal_page_url("https://example.com"))

    def test_identifies_specific_generated_internal_page_url(self):
        self.assertTrue(
            internal_pages.is_internal_page_url(
                "file:///C:/Project/Personal%20Browser/data/internal_pages/home.html",
                "home",
            )
        )
        self.assertFalse(
            internal_pages.is_internal_page_url(
                "file:///C:/Project/Personal%20Browser/data/internal_pages/history.html",
                "home",
            )
        )

    def test_extracts_internal_search_query(self):
        self.assertEqual(
            internal_pages.extract_internal_search_query(
                "personal-browser://search?q=python+docs&limit=50"
            ),
            "python docs",
        )

    def test_extracts_internal_search_request_with_limit(self):
        request = internal_pages.extract_internal_search_request(
            "personal-browser://search?q=python+docs&limit=50"
        )

        self.assertEqual(request.query, "python docs")
        self.assertEqual(request.result_limit, 50)

    def test_internal_search_request_clamps_limit(self):
        request = internal_pages.extract_internal_search_request(
            "personal-browser://search?q=python+docs&limit=500"
        )

        self.assertEqual(request.result_limit, 100)

    def test_ignores_non_search_internal_urls(self):
        self.assertIsNone(
            internal_pages.extract_internal_search_query("personal-browser://home")
        )
        self.assertIsNone(
            internal_pages.extract_internal_search_query("https://example.com")
        )


if __name__ == "__main__":
    unittest.main()
