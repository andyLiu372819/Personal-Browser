import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


from search_engine import Document
from search_engine.results_page import render_results_page


class ResultsPageTests(unittest.TestCase):
    def test_renders_query_heading(self):
        html = render_results_page("python docs", [])

        self.assertIn("Search results for python docs", html)

    def test_renders_result_title_and_url(self):
        document = Document(
            "Python Documentation",
            "https://docs.python.org/3/",
            "history",
            True,
            "2026-07-15T10:00:00",
        )

        html = render_results_page("python", [(18, document)])

        self.assertIn("Python Documentation", html)
        self.assertIn("https://docs.python.org/3/", html)
        self.assertIn('href="https://docs.python.org/3/"', html)

    def test_renders_empty_results_message(self):
        html = render_results_page("nothing", [])

        self.assertIn("No local results found", html)

    def test_escapes_html_in_query_and_results(self):
        document = Document(
            "<script>alert('title')</script>",
            "https://example.com/?x=<bad>",
            "history",
            False,
            None,
        )

        html = render_results_page("<script>alert('query')</script>", [(3, document)])

        self.assertIn("&lt;script&gt;alert(&#x27;query&#x27;)&lt;/script&gt;", html)
        self.assertIn("&lt;script&gt;alert(&#x27;title&#x27;)&lt;/script&gt;", html)
        self.assertIn("https://example.com/?x=&lt;bad&gt;", html)
        self.assertNotIn("<script>", html)


if __name__ == "__main__":
    unittest.main()
