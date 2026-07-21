import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import browser.window as browser_window
from browser.address_bar import AddressBarAction
from browser.internal_pages import INTERNAL_HOME_URL


class FakeAddressBar:
    def __init__(self):
        self.text_value = None

    def setText(self, text):
        self.text_value = text


class FakeWebView:
    def __init__(self):
        self.loaded_url = None

    def load(self, url):
        self.loaded_url = url.toString()


class FakeBrowserWindow:
    def __init__(self, homepage=INTERNAL_HOME_URL):
        self.address_bar = FakeAddressBar()
        self.settings = {
            "homepage": homepage,
            "default_search_engine": "personal",
            "fallback_search_engine": "duckduckgo",
            "search_results_limit": 50,
        }
        self.web_view = FakeWebView()
        self.internal_pages = []

    def current_web_view(self):
        return self.web_view

    def search_result_limit(self, value=None):
        return browser_window.BrowserWindow.search_result_limit(self, value)

    def load_internal_html_page(self, web_view, page_name, html, address_text=""):
        self.internal_pages.append((web_view, page_name, html))

    def load_home_page(self, web_view):
        browser_window.BrowserWindow.load_home_page(self, web_view)

    def load_address_bar_action(self, web_view, action, address_text=""):
        browser_window.BrowserWindow.load_address_bar_action(
            self,
            web_view,
            action,
            address_text=address_text,
        )


class BrowserWindowHomePageTests(unittest.TestCase):
    def setUp(self):
        self.original_resolver = browser_window.resolve_address_bar_input

    def tearDown(self):
        browser_window.resolve_address_bar_input = self.original_resolver

    def test_go_home_renders_personal_homepage(self):
        fake_window = FakeBrowserWindow()

        browser_window.BrowserWindow.go_home(fake_window)

        self.assertEqual(fake_window.internal_pages[0][0], fake_window.web_view)
        self.assertEqual(fake_window.internal_pages[0][1], "home")
        self.assertIn("Nexus Browser", fake_window.internal_pages[0][2])
        self.assertIn("personal-browser://search", fake_window.internal_pages[0][2])
        self.assertIn('<option value="50" selected>', fake_window.internal_pages[0][2])
        self.assertIsNone(fake_window.web_view.loaded_url)

    def test_go_home_supports_external_homepage_setting(self):
        fake_window = FakeBrowserWindow(homepage="https://example.com")

        browser_window.BrowserWindow.go_home(fake_window)

        self.assertEqual(fake_window.web_view.loaded_url, "https://example.com")
        self.assertEqual(fake_window.internal_pages, [])

    def test_homepage_search_uses_address_bar_resolution(self):
        fake_window = FakeBrowserWindow()

        def fake_resolver(
            text,
            search_engine_name,
            fallback_search_engine_name,
            result_limit,
            render_function=None,
        ):
            self.assertEqual(text, "python docs")
            self.assertEqual(search_engine_name, "personal")
            self.assertEqual(fallback_search_engine_name, "duckduckgo")
            self.assertEqual(result_limit, 75)
            return AddressBarAction("html", "<html>results</html>")

        browser_window.resolve_address_bar_input = fake_resolver

        browser_window.BrowserWindow.load_search_query(
            fake_window,
            fake_window.web_view,
            "python docs",
            75,
        )

        self.assertEqual(fake_window.address_bar.text_value, "python docs")
        self.assertEqual(
            fake_window.internal_pages,
            [(fake_window.web_view, "search-results", "<html>results</html>")],
        )


if __name__ == "__main__":
    unittest.main()
