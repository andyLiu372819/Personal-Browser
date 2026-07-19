from bookmarks import load_bookmarks
from history import load_history

from .crawler import load_crawled_pages


TITLE_WORD_MATCH = 3
URL_WORD_MATCH = 5
CONTENT_WORD_MATCH = 1
BOOKMARKED = 10
THRESHOLD = 0


class Document:
    def __init__(
        self,
        title,
        url,
        source,
        bookmarked,
        visited,
        content="",
        crawled_at=None,
    ):
        self.title = title
        self.url = url
        self.source = source
        self.bookmarked = bookmarked
        self.visited_at = visited
        self.content = content
        self.crawled_at = crawled_at


def build_documents(histories=None, bookmarks=None, crawled_pages=None):
    if histories is None and bookmarks is None and crawled_pages is None:
        histories = load_history()
        bookmarks = load_bookmarks()
        crawled_pages = load_crawled_pages()
    else:
        histories = histories or []
        bookmarks = bookmarks or []
        crawled_pages = crawled_pages or []

    documents = []
    documents_by_url = {}
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
        documents_by_url[url] = documents[-1]

    for bookmark_entry in bookmarks:
        url = bookmark_entry["url"]
        if url not in seen:
            documents.append(
                Document(bookmark_entry["title"], url, "bookmark", True, None)
            )
            documents_by_url[url] = documents[-1]

    for crawled_page in crawled_pages:
        url = crawled_page["url"]
        content = crawled_page.get("content", "")
        crawled_at = crawled_page.get("crawled_at")

        if url in documents_by_url:
            document = documents_by_url[url]
            document.content = content
            document.crawled_at = crawled_at
            continue

        documents.append(
            Document(
                crawled_page.get("title", url),
                url,
                "crawl",
                url in bookmark_urls,
                None,
                content,
                crawled_at,
            )
        )
        documents_by_url[url] = documents[-1]

    return documents


def score(query, document: Document):
    num = 0
    words = query.lower().split()

    if not words:
        return num

    title_lower = document.title.lower()
    url_lower = document.url.lower()
    content_lower = document.content.lower()
    matched = False

    for word in words:
        title = word in title_lower
        url = word in url_lower
        content = word in content_lower

        if title or url or content:
            matched = True

        num += (
            (TITLE_WORD_MATCH if title else 0)
            + (URL_WORD_MATCH if url else 0)
            + (CONTENT_WORD_MATCH if content else 0)
        )

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
