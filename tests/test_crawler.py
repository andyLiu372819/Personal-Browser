import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from search_engine import (
    FetchedPage,
    crawl_site,
    extract_page_data,
    load_crawled_pages,
    merge_crawled_pages,
    normalize_url,
    save_crawled_pages,
)


class CrawlerTests(unittest.TestCase):
    def test_normalize_url_resolves_relative_links_and_removes_fragments(self):
        self.assertEqual(
            normalize_url("/docs#install", "https://example.com/start"),
            "https://example.com/docs",
        )
        self.assertIsNone(normalize_url("mailto:test@example.com"))

    def test_extract_page_data_reads_title_text_and_links(self):
        html = """
        <html>
            <head>
                <title>Example Page</title>
                <style>.hidden { color: red; }</style>
            </head>
            <body>
                <h1>Hello crawler</h1>
                <script>alert("skip me")</script>
                <a href="/next">Next</a>
            </body>
        </html>
        """

        page_data = extract_page_data(html)

        self.assertEqual(page_data["title"], "Example Page")
        self.assertIn("Hello crawler", page_data["content"])
        self.assertNotIn("skip me", page_data["content"])
        self.assertEqual(page_data["links"], ["/next"])

    def test_crawl_site_follows_same_site_links(self):
        pages = {
            "https://example.com/": """
                <title>Home</title>
                <p>Home text</p>
                <a href="/about#team">About</a>
                <a href="https://other.example.com/">Offsite</a>
            """,
            "https://example.com/about": """
                <title>About</title>
                <p>About text</p>
            """,
        }

        def fake_fetcher(url):
            return FetchedPage(url, pages[url])

        crawled_pages = crawl_site(
            "https://example.com",
            max_pages=10,
            max_depth=1,
            fetcher=fake_fetcher,
        )

        self.assertEqual(
            [page["url"] for page in crawled_pages],
            ["https://example.com/", "https://example.com/about"],
        )
        self.assertEqual(crawled_pages[0]["title"], "Home")
        self.assertIn("About text", crawled_pages[1]["content"])

    def test_crawl_site_respects_max_depth(self):
        pages = {
            "https://example.com/": "<title>Home</title><a href='/about'>About</a>",
            "https://example.com/about": "<title>About</title>",
        }

        def fake_fetcher(url):
            return FetchedPage(url, pages[url])

        crawled_pages = crawl_site(
            "https://example.com",
            max_pages=10,
            max_depth=0,
            fetcher=fake_fetcher,
        )

        self.assertEqual(len(crawled_pages), 1)
        self.assertEqual(crawled_pages[0]["url"], "https://example.com/")

    def test_merge_crawled_pages_replaces_existing_url(self):
        existing_pages = [
            {
                "title": "Old",
                "url": "https://example.com/",
                "content": "old content",
                "crawled_at": "old-time",
            }
        ]
        new_pages = [
            {
                "title": "New",
                "url": "https://example.com/",
                "content": "new content",
                "crawled_at": "new-time",
            }
        ]

        merged_pages = merge_crawled_pages(existing_pages, new_pages)

        self.assertEqual(len(merged_pages), 1)
        self.assertEqual(merged_pages[0]["title"], "New")
        self.assertEqual(merged_pages[0]["content"], "new content")

    def test_save_and_load_crawled_pages(self):
        pages = [
            {
                "title": "Example",
                "url": "https://example.com/",
                "content": "example content",
                "crawled_at": "2026-07-19T10:00:00",
            }
        ]

        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "crawled_pages.json"
            save_crawled_pages(pages, file_path)

            self.assertEqual(load_crawled_pages(file_path), pages)


if __name__ == "__main__":
    unittest.main()
