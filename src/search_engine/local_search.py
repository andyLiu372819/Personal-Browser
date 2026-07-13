from bookmarks import load_bookmarks
from history import load_history


TITLE_WORD_MATCH = 3
URL_WORD_MATCH = 5
BOOKMARKED = 10
THRESHOLD = 2


class Document:
    def __init__(self, title, url, source, bookmarked, visited):
        self.title = title
        self.url = url
        self.source = source
        self.bookmarked = bookmarked
        self.visited_at = visited


def build_documents(histories=None, bookmarks=None):
    if histories is None:
        histories = load_history()
    if bookmarks is None:
        bookmarks = load_bookmarks()

    documents = []
    seen = set()

    bookmark_urls = {bookmark["url"] for bookmark in bookmarks}

    for history_entry in histories:
        url = history_entry["url"]
        bookmarked = url in bookmark_urls
        seen.add(url)
        documents.append(
            Document(
                history_entry["title"],
                url,
                "history",
                bookmarked,
                history_entry["visited_at"],
            )
        )

    for bookmark_entry in bookmarks:
        url = bookmark_entry["url"]
        if url not in seen:
            documents.append(
                Document(bookmark_entry["title"], url, "bookmark", True, None)
            )

    return documents


def score(query, document: Document):
    num = 0
    words = query.lower().split()

    if not words:
        return num

    title_lower = document.title.lower()
    url_lower = document.url.lower()
    matched = False

    for word in words:
        title = word in title_lower
        url = word in url_lower

        if title or url:
            matched = True

        num += (TITLE_WORD_MATCH if title else 0) + (URL_WORD_MATCH if url else 0)

    if matched and document.bookmarked:
        num += BOOKMARKED

    return num


def search(query, documents=None):
    results = []
    if documents is None:
        documents = build_documents()

    for document in documents:
        scores = score(query, document)
        if scores > THRESHOLD:
            results.append((scores, document))

    results.sort(key=lambda result: result[0], reverse=True)
    return results
