from .crawler import load_crawled_pages


TITLE_WORD_MATCH = 3
URL_WORD_MATCH = 5
CONTENT_WORD_MATCH = 1
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
        crawled_pages = load_crawled_pages()
    else:
        crawled_pages = crawled_pages or []

    documents = []

    for crawled_page in crawled_pages:
        url = crawled_page["url"]
        content = crawled_page.get("content", "")
        crawled_at = crawled_page.get("crawled_at")

        documents.append(
            Document(
                crawled_page.get("title", url),
                url,
                "crawl",
                False,
                None,
                content,
                crawled_at,
            )
        )

    return documents


def score(query, document: Document):
    num = 0
    words = query.lower().split()

    if not words:
        return num

    title_lower = document.title.lower()
    url_lower = document.url.lower()
    content_lower = document.content.lower()

    for word in words:
        title = word in title_lower
        url = word in url_lower
        content = word in content_lower

        num += (
            (TITLE_WORD_MATCH if title else 0)
            + (URL_WORD_MATCH if url else 0)
            + (CONTENT_WORD_MATCH if content else 0)
        )

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
