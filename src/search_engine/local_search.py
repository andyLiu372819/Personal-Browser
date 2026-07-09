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


def build_documents():
    histories = load_history()
    bookmarks = load_bookmarks()
    documents = []
    seen = set()

    bookmark_url = {i["url"] for i in bookmarks}

    for i in histories:
        bookmarked = i["url"] in bookmark_url
        seen.add(i["url"])
        documents.append(Document(i["title"], i["url"], "history", bookmarked, i["visited_at"]))

    for j in bookmarks:
        if j["url"] not in seen:
            documents.append(Document(j["title"], j["url"], "bookmark", True, None))

    return documents


def score(query, document: Document):
    num = 0
    words = query.lower().split()

    if not words:
        return num

    for word in words:
        title, url, booked = False, False, False

        title_lower = document.title.lower()
        url_lower = document.url.lower()

        if word in title_lower:
            title = True
        if word in url_lower:
            url = True
        
        if title or url:
            booked = document.bookmarked   
            
        num += (TITLE_WORD_MATCH if title else 0) + (URL_WORD_MATCH if url else 0) + (BOOKMARKED if booked else 0)
            

    return num


def search(query):
    results = []
    documents = build_documents()

    for i in documents:
        scores = score(query, i)
        if scores > THRESHOLD:
            results.append((scores, i))

    results.sort(key=lambda result: result[0], reverse=True)
    return results
