import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from browser.home_page import render_home_page
from browser.internal_pages import INTERNAL_SEARCH_URL


class HomePageTests(unittest.TestCase):
    def test_renders_internal_search_form(self):
        html = render_home_page()

        self.assertIn(f'action="{INTERNAL_SEARCH_URL}"', html)
        self.assertIn('method="get"', html)
        self.assertIn('name="q"', html)
        self.assertIn('name="limit"', html)
        self.assertIn("Search crawled pages and the wider web", html)
        self.assertIn("History boost", html)

    def test_renders_selected_result_limit(self):
        html = render_home_page(result_limit=75)

        self.assertIn('<option value="75" selected>', html)
        self.assertIn('<option value="100"', html)

    def test_escapes_app_name(self):
        html = render_home_page("<Browser>")

        self.assertIn("&lt;Browser&gt;", html)
        self.assertNotIn("<h1><Browser></h1>", html)


if __name__ == "__main__":
    unittest.main()
