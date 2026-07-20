import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import browser.window as browser_window


class FakeUrl:
    def __init__(self, url):
        self.url = url

    def toString(self):
        return self.url


class FakeWebView:
    def __init__(self, url):
        self._url = FakeUrl(url)

    def url(self):
        return self._url


class FakeStatusBar:
    def __init__(self):
        self.messages = []

    def showMessage(self, message, timeout=0):
        self.messages.append((message, timeout))


class FakeBrowserWindow:
    def __init__(self, url):
        self.web_view = FakeWebView(url)
        self.status_bar = FakeStatusBar()
        self.settings = {
            "crawler_max_pages": 75,
            "crawler_max_depth": 2,
        }

    def current_web_view(self):
        return self.web_view

    def statusBar(self):
        return self.status_bar


class BrowserWindowCrawlerTests(unittest.TestCase):
    def setUp(self):
        self.original_crawl_and_store = browser_window.crawl_and_store

    def tearDown(self):
        browser_window.crawl_and_store = self.original_crawl_and_store

    def test_crawl_current_site_indexes_current_url(self):
        fake_window = FakeBrowserWindow("https://example.com/start")

        def fake_crawl_and_store(url, max_pages, max_depth):
            self.assertEqual(url, "https://example.com/start")
            self.assertEqual(max_pages, 75)
            self.assertEqual(max_depth, 2)
            return [{"url": "https://example.com/start"}]

        browser_window.crawl_and_store = fake_crawl_and_store

        browser_window.BrowserWindow.crawl_current_site(fake_window)

        self.assertIn(
            ("Indexed 1 page(s) from this site.", 8000),
            fake_window.status_bar.messages,
        )

    def test_crawl_current_site_requires_web_url(self):
        fake_window = FakeBrowserWindow("about:blank")

        def fail_crawl_and_store(url, max_pages, max_depth):
            self.fail("Crawler should not run for non-web URLs")

        browser_window.crawl_and_store = fail_crawl_and_store

        browser_window.BrowserWindow.crawl_current_site(fake_window)

        self.assertIn(
            ("Open a website before crawling.", 5000),
            fake_window.status_bar.messages,
        )


if __name__ == "__main__":
    unittest.main()
