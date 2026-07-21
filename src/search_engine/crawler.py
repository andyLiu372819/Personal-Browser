import json
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from paths import user_data_path


CRAWLED_PAGES_FILE = user_data_path("crawled_pages.json")
USER_AGENT = "PersonalBrowserCrawler/1.0"
DEFAULT_CRAWLER_MAX_PAGES = 75
DEFAULT_CRAWLER_MAX_DEPTH = 2
MAX_CRAWLER_MAX_PAGES = 100
MIN_CRAWLER_MAX_PAGES = 1
MAX_CRAWLER_MAX_DEPTH = 4


@dataclass(frozen=True)
class FetchedPage:
    url: str
    html: str


def normalize_crawler_page_limit(value, default=DEFAULT_CRAWLER_MAX_PAGES):
    try:
        page_limit = int(value)
    except (TypeError, ValueError):
        page_limit = default

    return max(MIN_CRAWLER_MAX_PAGES, min(page_limit, MAX_CRAWLER_MAX_PAGES))


def normalize_crawler_depth(value, default=DEFAULT_CRAWLER_MAX_DEPTH):
    try:
        depth = int(value)
    except (TypeError, ValueError):
        depth = default

    return max(0, min(depth, MAX_CRAWLER_MAX_DEPTH))


class PageHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.text_parts = []
        self.links = []
        self._in_title = False
        self._ignored_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)

        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1
            return

        if tag == "title":
            self._in_title = True

        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag == "title":
            self._in_title = False

        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return

        if self._in_title:
            self.title_parts.append(text)
        elif not self._ignored_depth:
            self.text_parts.append(text)

    @property
    def title(self):
        return " ".join(self.title_parts).strip()

    @property
    def text(self):
        return " ".join(self.text_parts).strip()


def normalize_url(url, base_url=None):
    if not url:
        return None

    absolute_url = urljoin(base_url, url.strip()) if base_url else url.strip()
    absolute_url, _fragment = urldefrag(absolute_url)
    parsed = urlparse(absolute_url)

    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"

    return urlunparse((scheme, netloc, path, "", parsed.query, ""))


def is_same_site(start_url, candidate_url):
    return urlparse(start_url).netloc == urlparse(candidate_url).netloc


def extract_page_data(html):
    parser = PageHTMLParser()
    parser.feed(html)

    return {
        "title": parser.title,
        "content": parser.text,
        "links": parser.links,
    }


def fetch_page(url, timeout=10, max_bytes=1_000_000):
    request = Request(url, headers={"User-Agent": USER_AGENT})

    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        if "html" not in content_type.lower():
            return None

        raw_html = response.read(max_bytes)
        charset = response.headers.get_content_charset() or "utf-8"
        final_url = normalize_url(response.geturl()) or url

    return FetchedPage(final_url, raw_html.decode(charset, errors="replace"))


def crawl_site(
    start_url,
    max_pages=DEFAULT_CRAWLER_MAX_PAGES,
    max_depth=DEFAULT_CRAWLER_MAX_DEPTH,
    fetcher=fetch_page,
):
    normalized_start = normalize_url(start_url)
    if normalized_start is None:
        return []

    max_pages = normalize_crawler_page_limit(max_pages)
    max_depth = normalize_crawler_depth(max_depth)
    crawled_pages = []
    queued_urls = {normalized_start}
    visited_urls = set()
    pages_to_visit = deque([(normalized_start, 0)])

    while pages_to_visit and len(crawled_pages) < max_pages:
        current_url, depth = pages_to_visit.popleft()
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        try:
            fetched_page = fetcher(current_url)
        except Exception:
            continue

        if fetched_page is None:
            continue

        final_url = normalize_url(fetched_page.url) or current_url
        if not is_same_site(normalized_start, final_url):
            continue

        page_data = extract_page_data(fetched_page.html)
        crawled_pages.append(
            {
                "title": page_data["title"] or final_url,
                "url": final_url,
                "content": page_data["content"],
                "crawled_at": datetime.now().isoformat(timespec="seconds"),
            }
        )

        if depth >= max_depth:
            continue

        for link in page_data["links"]:
            next_url = normalize_url(link, final_url)
            if (
                next_url
                and is_same_site(normalized_start, next_url)
                and next_url not in queued_urls
                and next_url not in visited_urls
            ):
                queued_urls.add(next_url)
                pages_to_visit.append((next_url, depth + 1))

    return crawled_pages


def load_crawled_pages(file_path=CRAWLED_PAGES_FILE):
    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_crawled_pages(pages, file_path=CRAWLED_PAGES_FILE):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(pages, file, indent=2)
        file.write("\n")


def merge_crawled_pages(existing_pages, new_pages):
    pages_by_url = {page["url"]: page for page in existing_pages}

    for page in new_pages:
        pages_by_url[page["url"]] = page

    return list(pages_by_url.values())


def crawl_and_store(
    start_url,
    max_pages=DEFAULT_CRAWLER_MAX_PAGES,
    max_depth=DEFAULT_CRAWLER_MAX_DEPTH,
    fetcher=fetch_page,
):
    new_pages = crawl_site(start_url, max_pages, max_depth, fetcher)
    existing_pages = load_crawled_pages()
    save_crawled_pages(merge_crawled_pages(existing_pages, new_pages))
    return new_pages
