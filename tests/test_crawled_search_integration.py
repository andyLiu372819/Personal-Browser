import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from search_engine import build_documents, render_results_page, search


class CrawledSearchIntegrationTests(unittest.TestCase):
    def test_build_documents_adds_crawled_pages(self):
        documents = build_documents(
            [],
            [],
            [
                {
                    "title": "Crawler Guide",
                    "url": "https://example.com/crawler",
                    "content": "spider indexing guide",
                    "crawled_at": "2026-07-19T10:00:00",
                }
            ],
        )

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].source, "crawl")
        self.assertEqual(documents[0].content, "spider indexing guide")
        self.assertEqual(documents[0].crawled_at, "2026-07-19T10:00:00")

    def test_crawled_content_is_searchable(self):
        documents = build_documents(
            [],
            [],
            [
                {
                    "title": "Crawler Guide",
                    "url": "https://example.com/crawler",
                    "content": "unique indexing phrase",
                    "crawled_at": "2026-07-19T10:00:00",
                }
            ],
        )

        results = search("unique", documents)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1].title, "Crawler Guide")

    def test_crawled_content_does_not_merge_with_history_document(self):
        documents = build_documents(
            [
                {
                    "title": "Visited Page",
                    "url": "https://example.com/page",
                    "visited_at": "2026-07-19T09:00:00",
                }
            ],
            [],
            [
                {
                    "title": "Crawled Page",
                    "url": "https://example.com/page",
                    "content": "merged crawl content",
                    "crawled_at": "2026-07-19T10:00:00",
                }
            ],
        )

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].source, "crawl")
        self.assertEqual(documents[0].title, "Crawled Page")
        self.assertEqual(documents[0].content, "merged crawl content")
        self.assertEqual(documents[0].crawled_at, "2026-07-19T10:00:00")
        self.assertIsNone(documents[0].visited_at)

    def test_results_page_includes_crawled_content_snippet(self):
        documents = build_documents(
            [],
            [],
            [
                {
                    "title": "Crawler Guide",
                    "url": "https://example.com/crawler",
                    "content": "This snippet came from a crawled page.",
                    "crawled_at": "2026-07-19T10:00:00",
                }
            ],
        )

        html = render_results_page("snippet", search("snippet", documents))

        self.assertIn("This snippet came from a crawled page.", html)


if __name__ == "__main__":
    unittest.main()
