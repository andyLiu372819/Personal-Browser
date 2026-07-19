import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import browser.window as browser_window


class FakeWebView:
    def __init__(self):
        self.loaded_html = None

    def setHtml(self, html):
        self.loaded_html = html


class FakeBrowserWindow:
    def __init__(self, web_view):
        self.web_view = web_view

    def current_web_view(self):
        return self.web_view


class BrowserWindowHistoryPageTests(unittest.TestCase):
    def setUp(self):
        self.original_load_history = browser_window.load_history
        self.original_render_history_page = browser_window.render_history_page

    def tearDown(self):
        browser_window.load_history = self.original_load_history
        browser_window.render_history_page = self.original_render_history_page

    def test_open_history_page_renders_history_into_current_tab(self):
        web_view = FakeWebView()
        fake_window = FakeBrowserWindow(web_view)
        history_entries = [
            {
                "title": "Python Documentation",
                "url": "https://docs.python.org/3/",
                "visited_at": "2026-07-18T10:00:00",
            }
        ]

        browser_window.load_history = lambda: history_entries

        def fake_render(entries):
            self.assertEqual(entries, history_entries)
            return "<html>history page</html>"

        browser_window.render_history_page = fake_render

        browser_window.BrowserWindow.open_history_page(fake_window)

        self.assertEqual(web_view.loaded_html, "<html>history page</html>")

    def test_open_history_page_does_nothing_without_current_tab(self):
        fake_window = FakeBrowserWindow(None)

        def fail_load_history():
            self.fail("History should not load without a current tab")

        browser_window.load_history = fail_load_history

        browser_window.BrowserWindow.open_history_page(fake_window)


if __name__ == "__main__":
    unittest.main()
