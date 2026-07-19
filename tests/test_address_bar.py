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
            "history",
            False,
            None,
        )

        def fake_search(query):
            self.assertEqual(query, "python docs")
            return [(8, document)]

        def fake_render(query, results):
            self.assertEqual(query, "python docs")
            self.assertEqual(results, [(8, document)])
            return "<html>local search results</html>"

        action = resolve_address_bar_input(
            "python docs",
            search_function=fake_search,
            render_function=fake_render,
        )

        self.assertEqual(action.kind, "html")
        self.assertEqual(action.content, "<html>local search results</html>")

    def test_blank_input_returns_empty_action(self):
        def fail_search(query):
            self.fail("Blank input should not run local search")

        action = resolve_address_bar_input("   ", search_function=fail_search)

        self.assertEqual(action.kind, "empty")
        self.assertEqual(action.content, "")


if __name__ == "__main__":
    unittest.main()
