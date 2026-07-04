import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOKMARKS_FILE = PROJECT_ROOT / "data" / "bookmarks.json"


def load_bookmarks():
    if not BOOKMARKS_FILE.exists():
        return []

    with BOOKMARKS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_bookmarks(bookmarks):
    BOOKMARKS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with BOOKMARKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(bookmarks, file, indent=2)
        file.write("\n")


def is_bookmarked(url):
    return any(bookmark["url"] == url for bookmark in load_bookmarks())


def add_bookmark(title, url):
    bookmarks = load_bookmarks()

    if not url or any(bookmark["url"] == url for bookmark in bookmarks):
        return False

    bookmarks.append(
        {
            "title": title.strip() or url,
            "url": url,
            "added_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
    save_bookmarks(bookmarks)
    return True


def remove_bookmark(url):
    bookmarks = load_bookmarks()
    remaining_bookmarks = [
        bookmark for bookmark in bookmarks if bookmark["url"] != url
    ]

    if len(remaining_bookmarks) == len(bookmarks):
        return False

    save_bookmarks(remaining_bookmarks)
    return True
