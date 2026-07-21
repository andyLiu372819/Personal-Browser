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


class FakeUrl:
    def __init__(self, url):
        self.url = url

    def toString(self):
        return self.url


class FakeHistoryWebView:
    def __init__(self, url, title="Internal Page"):
        self._url = FakeUrl(url)
        self._title = title

    def url(self):
        return self._url

    def title(self):
        return self._title


class FakeBrowserWindow:
    def __init__(self, web_view):
        self.web_view = web_view
        self.internal_pages = []

    def current_web_view(self):
        return self.web_view

    def load_internal_html_page(self, web_view, page_name, html):
        self.internal_pages.append((web_view, page_name, html))


class BrowserWindowHistoryPageTests(unittest.TestCase):
    def setUp(self):
        self.original_add_history_entry = browser_window.add_history_entry
        self.original_load_history = browser_window.load_history
        self.original_render_history_page = browser_window.render_history_page

    def tearDown(self):
        browser_window.add_history_entry = self.original_add_history_entry
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

        def fake_render(entries, settings=None):
            self.assertEqual(entries, history_entries)
            return "<html>history page</html>"

        browser_window.render_history_page = fake_render

        browser_window.BrowserWindow.open_history_page(fake_window)

        self.assertEqual(
            fake_window.internal_pages,
            [(web_view, "history", "<html>history page</html>")],
        )

    def test_open_history_page_does_nothing_without_current_tab(self):
        fake_window = FakeBrowserWindow(None)

        def fail_load_history():
            self.fail("History should not load without a current tab")

        browser_window.load_history = fail_load_history

        browser_window.BrowserWindow.open_history_page(fake_window)

    def test_record_history_skips_generated_internal_pages(self):
        web_view = FakeHistoryWebView(
            "file:///C:/Users/Slsna/OneDrive/Desktop/proj/Personal%20Browser/"
            "data/internal_pages/history.html"
        )

        def fail_add_history_entry(title, url):
            self.fail("Generated internal pages should not be saved to history")

        browser_window.add_history_entry = fail_add_history_entry

        browser_window.BrowserWindow.record_history(object(), web_view, True)


if __name__ == "__main__":
    unittest.main()
