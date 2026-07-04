import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import bookmarks


class BookmarkStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_bookmarks_file = bookmarks.BOOKMARKS_FILE
        bookmarks.BOOKMARKS_FILE = (
            Path(self.temp_directory.name) / "bookmarks.json"
        )

    def tearDown(self):
        bookmarks.BOOKMARKS_FILE = self.original_bookmarks_file
        self.temp_directory.cleanup()

    def test_adds_and_loads_bookmark(self):
        added = bookmarks.add_bookmark("Example", "https://example.com")

        self.assertTrue(added)
        saved_bookmarks = bookmarks.load_bookmarks()
        self.assertEqual(len(saved_bookmarks), 1)
        self.assertEqual(saved_bookmarks[0]["title"], "Example")
        self.assertEqual(saved_bookmarks[0]["url"], "https://example.com")
        self.assertTrue(saved_bookmarks[0]["added_at"])

    def test_rejects_duplicate_url(self):
        bookmarks.add_bookmark("Example", "https://example.com")

        duplicate_added = bookmarks.add_bookmark(
            "Duplicate title", "https://example.com"
        )

        self.assertFalse(duplicate_added)
        self.assertEqual(len(bookmarks.load_bookmarks()), 1)

    def test_removes_bookmark_by_url(self):
        bookmarks.add_bookmark("Example", "https://example.com")

        self.assertTrue(bookmarks.remove_bookmark("https://example.com"))
        self.assertFalse(bookmarks.is_bookmarked("https://example.com"))
        self.assertFalse(bookmarks.remove_bookmark("https://example.com"))


if __name__ == "__main__":
    unittest.main()
