import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from browser.history_page import render_history_page


class HistoryPageTests(unittest.TestCase):
    def test_renders_history_entry_title_url_and_time(self):
        html = render_history_page(
            [
                {
                    "title": "Python Documentation",
                    "url": "https://docs.python.org/3/",
                    "visited_at": "2026-07-18T10:00:00",
                }
            ]
        )

        self.assertIn("Python Documentation", html)
        self.assertIn("https://docs.python.org/3/", html)
        self.assertIn('href="https://docs.python.org/3/"', html)
        self.assertIn("2026-07-18T10:00:00", html)

    def test_renders_newest_history_first(self):
        html = render_history_page(
            [
                {
                    "title": "Older Page",
                    "url": "https://example.com/older",
                    "visited_at": "2026-07-18T09:00:00",
                },
                {
                    "title": "Newer Page",
                    "url": "https://example.com/newer",
                    "visited_at": "2026-07-18T10:00:00",
                },
            ]
        )

        self.assertLess(html.index("Newer Page"), html.index("Older Page"))

    def test_renders_empty_history_message(self):
        html = render_history_page([])

        self.assertIn("No browsing history yet", html)

    def test_escapes_html_in_history_entries(self):
        html = render_history_page(
            [
                {
                    "title": "<script>alert('title')</script>",
                    "url": "https://example.com/?x=<bad>",
                    "visited_at": "<time>",
                }
            ]
        )

        self.assertIn("&lt;script&gt;alert(&#x27;title&#x27;)&lt;/script&gt;", html)
        self.assertIn("https://example.com/?x=&lt;bad&gt;", html)
        self.assertIn("&lt;time&gt;", html)
        self.assertNotIn("<script>", html)


if __name__ == "__main__":
    unittest.main()
