import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from browser.address_bar import resolve_address_bar_input
from search_engine import Document


class AddressBarInputTests(unittest.TestCase):
    def test_url_input_returns_url_action(self):
        action = resolve_address_bar_input("example.com")

        self.assertEqual(action.kind, "url")
        self.assertEqual(action.content, "https://example.com")

    def test_complete_url_is_preserved(self):
        action = resolve_address_bar_input("https://example.com/page")

        self.assertEqual(action.kind, "url")
        self.assertEqual(action.content, "https://example.com/page")

    def test_search_input_returns_local_search_page(self):
        document = Document(
            "Python Documentation",
            "https://docs.python.org/3/",
            "crawl",
            False,
            None,
        )

        def fake_search(query, max_results):
            self.assertEqual(query, "python docs")
            self.assertEqual(max_results, 10)
            return [(8, document)]

        def fake_render(query, results, result_limit):
            self.assertEqual(query, "python docs")
            self.assertEqual(results, [(8, document)])
            self.assertEqual(result_limit, 10)
            return "<html>local search results</html>"

        action = resolve_address_bar_input(
            "python docs",
            search_function=fake_search,
            render_function=fake_render,
        )

        self.assertEqual(action.kind, "html")
        self.assertEqual(action.content, "<html>local search results</html>")

    def test_search_input_renders_results_page_without_any_results(self):
        def fake_search(query, max_results):
            self.assertEqual(query, "unknown thing")
            self.assertEqual(max_results, 10)
            return []

        def fake_render(query, results, result_limit):
            self.assertEqual(query, "unknown thing")
            self.assertEqual(results, [])
            self.assertEqual(result_limit, 10)
            return "<html>no results page</html>"

        action = resolve_address_bar_input(
            "unknown thing",
            search_function=fake_search,
            render_function=fake_render,
        )

        self.assertEqual(action.kind, "html")
        self.assertEqual(action.content, "<html>no results page</html>")

    def test_search_input_renders_web_results_from_personal_search(self):
        document = Document(
            "Python Docs",
            "https://docs.python.org/3/",
            "web",
            False,
            None,
            "Official Python documentation.",
        )

        def fake_search(query, max_results):
            self.assertEqual(query, "python docs")
            self.assertEqual(max_results, 10)
            return [(1, document)]

        def fake_render(query, results, result_limit):
            self.assertEqual(query, "python docs")
            self.assertEqual(results, [(1, document)])
            self.assertEqual(result_limit, 10)
            return "<html>web search results</html>"

        action = resolve_address_bar_input(
            "python docs",
            search_function=fake_search,
            render_function=fake_render,
        )

        self.assertEqual(action.kind, "html")
        self.assertEqual(action.content, "<html>web search results</html>")

    def test_personal_search_uses_internal_page_even_with_selected_fallback_engine(self):
        action = resolve_address_bar_input(
            "unknown thing",
            fallback_search_engine_name="google",
            search_function=lambda query, max_results: [],
            render_function=lambda query, results, result_limit: (
                "<html>no results page</html>"
            ),
        )

        self.assertEqual(action.kind, "html")
        self.assertEqual(action.content, "<html>no results page</html>")

    def test_external_search_engine_skips_local_search(self):
        def fail_search(query, max_results):
            self.fail("External search engines should not run local search first")

        action = resolve_address_bar_input(
            "python docs",
            search_engine_name="google",
            search_function=fail_search,
        )

        self.assertEqual(action.kind, "url")
        self.assertEqual(action.content, "https://www.google.com/search?q=python+docs")

    def test_blank_input_returns_empty_action(self):
        def fail_search(query, max_results):
            self.fail("Blank input should not run local search")

        action = resolve_address_bar_input("   ", search_function=fail_search)

        self.assertEqual(action.kind, "empty")
        self.assertEqual(action.content, "")

    def test_search_input_uses_selected_result_limit(self):
        def fake_search(query, max_results):
            self.assertEqual(query, "python docs")
            self.assertEqual(max_results, 50)
            return []

        def fake_render(query, results, result_limit):
            self.assertEqual(result_limit, 50)
            return "<html>50 results selected</html>"

        action = resolve_address_bar_input(
            "python docs",
            result_limit=50,
            search_function=fake_search,
            render_function=fake_render,
        )

        self.assertEqual(action.kind, "html")
        self.assertEqual(action.content, "<html>50 results selected</html>")


if __name__ == "__main__":
    unittest.main()
