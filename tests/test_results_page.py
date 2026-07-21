import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


from search_engine import Document
from search_engine.results_page import render_result_limit_options, render_results_page


class ResultsPageTests(unittest.TestCase):
    def test_renders_query_heading(self):
        html = render_results_page("python docs", [])

        self.assertIn("Search results for python docs", html)

    def test_renders_result_title_and_url(self):
        document = Document(
            "Python Documentation",
            "https://docs.python.org/3/",
            "crawl",
            False,
            None,
        )

        html = render_results_page("python", [(18, document)])

        self.assertIn("Python Documentation", html)
        self.assertIn("https://docs.python.org/3/", html)
        self.assertIn('href="https://docs.python.org/3/"', html)
        self.assertIn('class="result-url"', html)
        self.assertIn('class="result-card"', html)

    def test_renders_empty_results_message(self):
        html = render_results_page("nothing", [])

        self.assertIn("No results found", html)
        self.assertIn("Search DuckDuckGo", html)
        self.assertIn("Search Google", html)
        self.assertIn("https://www.google.com/search?q=nothing", html)

    def test_renders_top_search_form_with_existing_query(self):
        html = render_results_page("python docs", [])

        self.assertIn('form action="personal-browser://search"', html)
        self.assertIn('name="q"', html)
        self.assertIn('name="limit"', html)
        self.assertIn('value="python docs"', html)
        self.assertIn("Nexus Search", html)

    def test_renders_selected_result_limit(self):
        html = render_results_page("python docs", [], result_limit=100)

        self.assertIn('<option value="100" selected>', html)
        self.assertIn("Display limit", html)

    def test_render_result_limit_options_clamps_invalid_value(self):
        options = render_result_limit_options(500)

        self.assertIn('<option value="100" selected>', options)

    def test_escapes_html_in_query_and_results(self):
        document = Document(
            "<script>alert('title')</script>",
            "https://example.com/?x=<bad>",
            "crawl",
            False,
            None,
        )

        html = render_results_page("<script>alert('query')</script>", [(3, document)])

        self.assertIn("&lt;script&gt;alert(&#x27;query&#x27;)&lt;/script&gt;", html)
        self.assertIn("&lt;script&gt;alert(&#x27;title&#x27;)&lt;/script&gt;", html)
        self.assertIn("https://example.com/?x=&lt;bad&gt;", html)
        self.assertNotIn("<script>", html)

    def test_renders_web_result_label(self):
        document = Document(
            "Python Docs",
            "https://docs.python.org/3/",
            "web",
            False,
            None,
            "Official Python documentation.",
        )

        html = render_results_page("python", [(1, document)])

        self.assertIn("Official Python documentation.", html)
        self.assertIn("Web result", html)
        self.assertNotIn("Score 1", html)

    def test_renders_visited_web_result_with_score(self):
        document = Document(
            "Python Docs",
            "https://docs.python.org/3/",
            "web",
            False,
            "2026-07-20T10:00:00",
            "Official Python documentation.",
        )

        html = render_results_page("python", [(6, document)])

        self.assertIn("Web result", html)
        self.assertIn("Visited before", html)
        self.assertIn("Score 6", html)


if __name__ == "__main__":
    unittest.main()
