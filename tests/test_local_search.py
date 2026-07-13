import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from search_engine import Document, build_documents, score, search


class LocalSearchTests(unittest.TestCase):
    def test_build_documents_merges_history_and_bookmark_data(self):
        histories = [
            {
                "title": "Python Documentation",
                "url": "https://docs.python.org/3/",
                "visited_at": "2026-07-12T10:00:00",
            },
            {
                "title": "Qt for Python",
                "url": "https://doc.qt.io/qtforpython/",
                "visited_at": "2026-07-12T10:05:00",
            },
        ]
        bookmarks = [
            {
                "title": "Python Docs Bookmark",
                "url": "https://docs.python.org/3/",
                "added_at": "2026-07-12T10:10:00",
            },
            {
                "title": "Search Engine Notes",
                "url": "https://example.com/search-engine-notes",
                "added_at": "2026-07-12T10:15:00",
            },
        ]

        documents = build_documents(histories, bookmarks)
        documents_by_url = {document.url: document for document in documents}

        self.assertEqual(len(documents), 3)
        self.assertTrue(documents_by_url["https://docs.python.org/3/"].bookmarked)
        self.assertEqual(
            documents_by_url["https://docs.python.org/3/"].source,
            "history",
        )
        self.assertEqual(
            documents_by_url["https://example.com/search-engine-notes"].source,
            "bookmark",
        )
        self.assertIsNone(
            documents_by_url["https://example.com/search-engine-notes"].visited_at
        )

    def test_score_is_case_insensitive(self):
        document = Document(
            "Python Documentation",
            "https://docs.python.org/3/",
            "history",
            False,
            "2026-07-12T10:00:00",
        )

        self.assertEqual(score("PYTHON", document), score("python", document))
        self.assertGreater(score("PYTHON", document), 0)

    def test_bookmark_bonus_is_added_once_per_document(self):
        document = Document(
            "Python Docs",
            "https://example.com/python",
            "history",
            True,
            "2026-07-12T10:00:00",
        )

        self.assertEqual(score("python docs", document), 21)

    def test_search_sorts_results_by_score(self):
        documents = [
            Document("Python", "https://example.com", "history", False, None),
            Document(
                "Python Bookmark",
                "https://docs.python.org/3/",
                "bookmark",
                True,
                None,
            ),
            Document("Unrelated", "https://example.com/other", "history", False, None),
        ]

        results = search("python", documents)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][1].title, "Python Bookmark")
        self.assertGreater(results[0][0], results[1][0])

    def test_blank_query_returns_no_results(self):
        documents = [
            Document("Python", "https://docs.python.org/3/", "history", True, None)
        ]

        self.assertEqual(search("   ", documents), [])


if __name__ == "__main__":
    unittest.main()
