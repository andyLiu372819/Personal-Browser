import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from search_engine import Document, WebSearchResult, personal_search
from search_engine.hybrid_search import HISTORY_VISIT_BONUS, normalize_result_limit


class HybridSearchTests(unittest.TestCase):
    def test_personal_search_combines_local_and_web_results(self):
        local_document = Document(
            "Local Python Notes",
            "https://example.com/local-python",
            "crawl",
            False,
            None,
        )
        web_result = WebSearchResult(
            "Python Docs",
            "https://docs.python.org/3/",
            "Official Python documentation.",
        )

        results = personal_search(
            "python",
            local_search_function=lambda query, documents=None: [(7, local_document)],
            web_search_function=lambda query, provider, max_results: [web_result],
            history_entries=[],
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (7, local_document))
        self.assertEqual(results[1][1].source, "web")
        self.assertEqual(results[1][1].title, "Python Docs")
        self.assertEqual(results[1][1].content, "Official Python documentation.")

    def test_personal_search_deduplicates_web_results_against_local_urls(self):
        local_document = Document(
            "Python Docs",
            "https://docs.python.org/3/",
            "crawl",
            False,
            None,
        )
        web_result = WebSearchResult(
            "Python Docs",
            "https://docs.python.org/3/",
            "Official Python documentation.",
        )

        results = personal_search(
            "python",
            local_search_function=lambda query, documents=None: [(7, local_document)],
            web_search_function=lambda query, provider, max_results: [web_result],
            history_entries=[],
        )

        self.assertEqual(results, [(7, local_document)])

    def test_personal_search_keeps_local_results_when_web_fails(self):
        local_document = Document(
            "Local Python Notes",
            "https://example.com/local-python",
            "crawl",
            False,
            None,
        )

        def failing_web_search(query, provider, max_results):
            raise OSError("network unavailable")

        results = personal_search(
            "python",
            local_search_function=lambda query, documents=None: [(7, local_document)],
            web_search_function=failing_web_search,
            history_entries=[],
        )

        self.assertEqual(results, [(7, local_document)])

    def test_personal_search_limits_total_results(self):
        local_documents = [
            Document(f"Local {index}", f"https://example.com/{index}", "crawl", False, None)
            for index in range(5)
        ]
        web_calls = []

        results = personal_search(
            "local",
            max_results=3,
            local_search_function=lambda query, documents=None: [
                (10 - index, document)
                for index, document in enumerate(local_documents)
            ],
            web_search_function=lambda query, provider, max_results: web_calls.append(
                max_results
            )
            or [],
            history_entries=[],
        )

        self.assertEqual(len(results), 3)
        self.assertEqual(web_calls, [3])

    def test_personal_search_requests_full_web_result_limit(self):
        local_document = Document("Local", "https://example.com/local", "crawl", False, None)

        def fake_web_search(query, provider, max_results):
            self.assertEqual(max_results, 5)
            return [
                WebSearchResult(
                    f"Web {index}",
                    f"https://example.com/web-{index}",
                    "",
                )
                for index in range(4)
            ]

        results = personal_search(
            "query",
            max_results=5,
            local_search_function=lambda query, documents=None: [(10, local_document)],
            web_search_function=fake_web_search,
            history_entries=[],
        )

        self.assertEqual(len(results), 5)

    def test_personal_search_boosts_results_from_history(self):
        unvisited_result = WebSearchResult(
            "Unvisited Python Result",
            "https://example.com/python",
            "",
        )
        visited_result = WebSearchResult(
            "Visited Python Result",
            "https://docs.python.org/3/",
            "",
        )
        history_entries = [
            {
                "title": "Python Tutorial",
                "url": "https://docs.python.org/3/tutorial/",
                "visited_at": "2026-07-20T10:00:00",
            }
        ]

        results = personal_search(
            "python",
            local_search_function=lambda query, documents=None: [],
            web_search_function=lambda query, provider, max_results: [
                unvisited_result,
                visited_result,
            ],
            history_entries=history_entries,
        )

        self.assertEqual(results[0][1].url, "https://docs.python.org/3/")
        self.assertEqual(results[0][0], 1 + HISTORY_VISIT_BONUS)
        self.assertEqual(results[0][1].visited_at, "2026-07-20T10:00:00")
        self.assertEqual(results[1][0], 1)
        self.assertIsNone(results[1][1].visited_at)

    def test_personal_search_does_not_use_history_as_search_result(self):
        results = personal_search(
            "python",
            local_search_function=lambda query, documents=None: [],
            web_search_function=lambda query, provider, max_results: [],
            history_entries=[
                {
                    "title": "Python Documentation",
                    "url": "https://docs.python.org/3/",
                    "visited_at": "2026-07-20T10:00:00",
                }
            ],
        )

        self.assertEqual(results, [])

    def test_personal_search_boosts_crawled_result_from_same_history_site(self):
        crawled_document = Document(
            "Python Docs",
            "https://docs.python.org/3/",
            "crawl",
            False,
            None,
        )

        results = personal_search(
            "python",
            local_search_function=lambda query, documents=None: [(8, crawled_document)],
            web_search_function=lambda query, provider, max_results: [],
            history_entries=[
                {
                    "title": "Python Tutorial",
                    "url": "https://docs.python.org/3/tutorial/",
                    "visited_at": "2026-07-20T10:00:00",
                }
            ],
        )

        self.assertEqual(results, [(8 + HISTORY_VISIT_BONUS, crawled_document)])
        self.assertEqual(crawled_document.visited_at, "2026-07-20T10:00:00")

    def test_history_boost_can_lift_web_result_into_limited_results(self):
        local_documents = [
            Document(f"Local {index}", f"https://example.com/{index}", "crawl", False, None)
            for index in range(3)
        ]
        visited_web_result = WebSearchResult(
            "Visited Web Result",
            "https://docs.python.org/3/",
            "",
        )

        results = personal_search(
            "python",
            max_results=3,
            local_search_function=lambda query, documents=None: [
                (2, document) for document in local_documents
            ],
            web_search_function=lambda query, provider, max_results: [visited_web_result],
            history_entries=[
                {
                    "title": "Python Tutorial",
                    "url": "https://docs.python.org/3/tutorial/",
                    "visited_at": "2026-07-20T10:00:00",
                }
            ],
        )

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][1].url, "https://docs.python.org/3/")
        self.assertEqual(results[0][0], 1 + HISTORY_VISIT_BONUS)

    def test_normalize_result_limit_clamps_to_one_hundred(self):
        self.assertEqual(normalize_result_limit(500), 100)
        self.assertEqual(normalize_result_limit("50"), 50)
        self.assertEqual(normalize_result_limit("bad"), 10)


if __name__ == "__main__":
    unittest.main()
