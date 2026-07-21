import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import browser.window as browser_window
from browser.address_bar import AddressBarAction


class FakeAddressBar:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class FakeWebView:
    def __init__(self):
        self.loaded_url = None
        self.loaded_html = None

    def load(self, url):
        self.loaded_url = url.toString()

    def setHtml(self, html):
        self.loaded_html = html


class FakeBrowserWindow:
    def __init__(self, text):
        self.address_bar = FakeAddressBar(text)
        self.settings = {
            "default_search_engine": "personal",
            "fallback_search_engine": "duckduckgo",
            "search_results_limit": 25,
        }
        self.web_view = FakeWebView()
        self.internal_pages = []

    def current_web_view(self):
        return self.web_view

    def search_result_limit(self, value=None):
        return browser_window.BrowserWindow.search_result_limit(self, value)

    def load_address_bar_action(self, web_view, action, address_text=""):
        browser_window.BrowserWindow.load_address_bar_action(
            self,
            web_view,
            action,
            address_text=address_text,
        )

    def load_internal_html_page(self, web_view, page_name, html, address_text=""):
        self.internal_pages.append((web_view, page_name, html))


class BrowserWindowAddressBarTests(unittest.TestCase):
    def setUp(self):
        self.original_resolver = browser_window.resolve_address_bar_input

    def tearDown(self):
        browser_window.resolve_address_bar_input = self.original_resolver

    def test_load_address_bar_url_loads_url_action(self):
        fake_window = FakeBrowserWindow("example.com")

        def fake_resolver(
            text,
            search_engine_name,
            fallback_search_engine_name,
            result_limit,
            render_function=None,
        ):
            self.assertEqual(text, "example.com")
            self.assertEqual(search_engine_name, "personal")
            self.assertEqual(fallback_search_engine_name, "duckduckgo")
            self.assertEqual(result_limit, 25)
            return AddressBarAction("url", "https://example.com")

        browser_window.resolve_address_bar_input = fake_resolver

        browser_window.BrowserWindow.load_address_bar_url(fake_window)

        self.assertEqual(fake_window.web_view.loaded_url, "https://example.com")
        self.assertIsNone(fake_window.web_view.loaded_html)

    def test_load_address_bar_url_sets_html_action(self):
        fake_window = FakeBrowserWindow("python docs")

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
            self.assertEqual(result_limit, 25)
            return AddressBarAction("html", "<html>local results</html>")

        browser_window.resolve_address_bar_input = fake_resolver

        browser_window.BrowserWindow.load_address_bar_url(fake_window)

        self.assertEqual(
            fake_window.internal_pages,
            [(fake_window.web_view, "search-results", "<html>local results</html>")],
        )
        self.assertIsNone(fake_window.web_view.loaded_url)

    def test_load_address_bar_url_ignores_blank_input(self):
        fake_window = FakeBrowserWindow("   ")

        def fail_resolver(
            text,
            search_engine_name,
            fallback_search_engine_name,
            result_limit,
            render_function=None,
        ):
            self.fail("Blank address bar input should return before resolving")

        browser_window.resolve_address_bar_input = fail_resolver

        browser_window.BrowserWindow.load_address_bar_url(fake_window)

        self.assertIsNone(fake_window.web_view.loaded_url)
        self.assertIsNone(fake_window.web_view.loaded_html)


if __name__ == "__main__":
    unittest.main()
