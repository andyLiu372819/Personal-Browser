import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from search_engine.web_search import (
    WebSearchResult,
    build_duckduckgo_next_url,
    build_web_search_url,
    clean_duckduckgo_result_url,
    parse_duckduckgo_page,
    parse_duckduckgo_results,
    search_web,
)


class WebSearchTests(unittest.TestCase):
    def test_builds_duckduckgo_html_search_url(self):
        self.assertEqual(
            build_web_search_url("python docs"),
            "https://html.duckduckgo.com/html/?q=python+docs",
        )

    def test_decodes_duckduckgo_redirect_url(self):
        self.assertEqual(
            clean_duckduckgo_result_url(
                "//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fdocs"
            ),
            "https://example.com/docs",
        )

    def test_parse_duckduckgo_results_extracts_title_url_and_snippet(self):
        html = """
        <html>
            <body>
                <a class="result__a" href="/l/?uddg=https%3A%2F%2Fexample.com%2Fdocs">
                    Example Docs
                </a>
                <a class="result__snippet">
                    Helpful documentation for examples.
                </a>
            </body>
        </html>
        """

        results = parse_duckduckgo_results(html)

        self.assertEqual(
            results,
            [
                WebSearchResult(
                    title="Example Docs",
                    url="https://example.com/docs",
                    snippet="Helpful documentation for examples.",
                )
            ],
        )

    def test_parse_duckduckgo_page_extracts_next_params(self):
        html = """
        <a class="result__a" href="https://example.com/one">One</a>
        <div class="nav-link">
            <form action="/html/" method="post">
                <input type="submit" value="Next" />
                <input type="hidden" name="q" value="example query" />
                <input type="hidden" name="s" value="10" />
                <input type="hidden" name="dc" value="11" />
            </form>
        </div>
        """

        results, next_params = parse_duckduckgo_page(html)

        self.assertEqual(results[0].title, "One")
        self.assertEqual(
            next_params,
            {
                "q": "example query",
                "s": "10",
                "dc": "11",
            },
        )

    def test_builds_duckduckgo_next_url(self):
        self.assertEqual(
            build_duckduckgo_next_url({"q": "example query", "s": "10"}),
            "https://html.duckduckgo.com/html/?q=example+query&s=10",
        )

    def test_search_web_uses_fetcher_and_limits_results(self):
        html = """
        <a class="result__a" href="https://example.com/one">One</a>
        <a class="result__a" href="https://example.com/two">Two</a>
        """
        fetched_urls = []

        def fake_fetcher(url):
            fetched_urls.append(url)
            return html

        results = search_web("example query", max_results=1, fetcher=fake_fetcher)

        self.assertEqual(
            fetched_urls,
            ["https://html.duckduckgo.com/html/?q=example+query"],
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "One")

    def test_search_web_fetches_more_pages_for_larger_limits(self):
        pages = {
            "https://html.duckduckgo.com/html/?q=example+query": """
                <a class="result__a" href="https://example.com/one">One</a>
                <div class="nav-link">
                    <form action="/html/" method="post">
                        <input type="submit" value="Next" />
                        <input type="hidden" name="q" value="example query" />
                        <input type="hidden" name="s" value="10" />
                    </form>
                </div>
            """,
            "https://html.duckduckgo.com/html/?q=example+query&s=10": """
                <a class="result__a" href="https://example.com/two">Two</a>
            """,
        }
        fetched_urls = []

        def fake_fetcher(url):
            fetched_urls.append(url)
            return pages.get(url, "")

        results = search_web("example query", max_results=2, fetcher=fake_fetcher)

        self.assertEqual(
            fetched_urls,
            [
                "https://html.duckduckgo.com/html/?q=example+query",
                "https://html.duckduckgo.com/html/?q=example+query&s=10",
            ],
        )
        self.assertEqual([result.title for result in results], ["One", "Two"])

    def test_search_web_clamps_large_limits_to_one_hundred(self):
        html = "\n".join(
            f'<a class="result__a" href="https://example.com/{index}">Result {index}</a>'
            for index in range(120)
        )

        results = search_web("example query", max_results=500, fetcher=lambda url: html)

        self.assertEqual(len(results), 100)


if __name__ == "__main__":
    unittest.main()
