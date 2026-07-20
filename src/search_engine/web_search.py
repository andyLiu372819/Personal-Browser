from dataclasses import dataclass
from math import ceil
from html import unescape
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, unquote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_WEB_SEARCH_PROVIDER = "duckduckgo"
DUCKDUCKGO_RESULTS_PER_PAGE = 15
WEB_SEARCH_URLS = {
    "duckduckgo": "https://html.duckduckgo.com/html/?q={query}",
}
WEB_SEARCH_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "PersonalBrowser/1.0 Safari/537.36"
)


@dataclass(frozen=True)
class WebSearchResult:
    title: str
    url: str
    snippet: str = ""
    provider: str = DEFAULT_WEB_SEARCH_PROVIDER


class DuckDuckGoResultsParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results = []
        self._current_result = None
        self._in_title = False
        self._in_snippet = False
        self._in_nav_link = 0
        self._in_next_form = False
        self._next_form_is_next = False
        self._next_form_fields = {}
        self.next_params = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        class_names = set(attributes.get("class", "").split())

        if tag == "div" and "nav-link" in class_names:
            self._in_nav_link += 1
            return

        if self._in_nav_link and tag == "form":
            self._in_next_form = True
            self._next_form_is_next = False
            self._next_form_fields = {}
            return

        if self._in_next_form and tag == "input":
            input_type = attributes.get("type", "").lower()
            name = attributes.get("name")
            value = attributes.get("value", "")

            if input_type == "submit" and value.lower() == "next":
                self._next_form_is_next = True

            if input_type == "hidden" and name is not None:
                self._next_form_fields[name] = value

            return

        if tag == "a" and (
            "result__a" in class_names or "result-link" in class_names
        ):
            self._finish_current_result()
            self._current_result = {
                "title_parts": [],
                "url": clean_duckduckgo_result_url(attributes.get("href", "")),
                "snippet_parts": [],
            }
            self._in_title = True
            return

        if self._current_result and (
            "result__snippet" in class_names
            or "result-snippet" in class_names
        ):
            self._in_snippet = True

    def handle_endtag(self, tag):
        if tag == "form" and self._in_next_form:
            if self._next_form_is_next and self._next_form_fields:
                self.next_params = self._next_form_fields.copy()

            self._in_next_form = False
            self._next_form_is_next = False
            self._next_form_fields = {}
            return

        if tag == "div" and self._in_nav_link:
            self._in_nav_link -= 1
            return

        if tag == "a" and self._in_title:
            self._in_title = False
            return

        if tag in {"a", "div"} and self._in_snippet:
            self._in_snippet = False

    def handle_data(self, data):
        if self._current_result is None:
            return

        text = " ".join(data.split())
        if not text:
            return

        if self._in_title:
            self._current_result["title_parts"].append(text)
        elif self._in_snippet:
            self._current_result["snippet_parts"].append(text)

    def close(self):
        super().close()
        self._finish_current_result()

    def _finish_current_result(self):
        if self._current_result is None:
            return

        title = " ".join(self._current_result["title_parts"]).strip()
        url = self._current_result["url"]
        snippet = " ".join(self._current_result["snippet_parts"]).strip()

        if title and url:
            self.results.append(
                WebSearchResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    provider=DEFAULT_WEB_SEARCH_PROVIDER,
                )
            )

        self._current_result = None
        self._in_title = False
        self._in_snippet = False


def clean_duckduckgo_result_url(url):
    cleaned_url = unescape(url).strip()
    if not cleaned_url:
        return None

    if cleaned_url.startswith("//"):
        cleaned_url = f"https:{cleaned_url}"

    parsed_url = urlparse(cleaned_url)
    if parsed_url.scheme in {"http", "https"} and parsed_url.netloc:
        if parsed_url.netloc.endswith("duckduckgo.com") and parsed_url.path == "/l/":
            redirected_url = parse_qs(parsed_url.query).get("uddg", [""])[0]
            return unquote(redirected_url) or cleaned_url

        return cleaned_url

    if cleaned_url.startswith("/l/"):
        redirected_url = parse_qs(urlparse(cleaned_url).query).get("uddg", [""])[0]
        if redirected_url:
            return unquote(redirected_url)

    if cleaned_url.startswith("/"):
        return urljoin("https://duckduckgo.com", cleaned_url)

    return None


def build_web_search_url(query, provider=DEFAULT_WEB_SEARCH_PROVIDER, offset=0):
    search_url = WEB_SEARCH_URLS.get(provider, WEB_SEARCH_URLS[DEFAULT_WEB_SEARCH_PROVIDER])
    url = search_url.format(query=quote_plus(query.strip()))

    if provider == "duckduckgo" and offset:
        url = f"{url}&s={offset}"

    return url


def build_duckduckgo_next_url(next_params):
    return f"https://html.duckduckgo.com/html/?{urlencode(next_params)}"


def fetch_search_page(url, timeout=8, max_bytes=2_000_000):
    request = Request(
        url,
        headers={
            "User-Agent": WEB_SEARCH_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        raw_html = response.read(max_bytes)
        charset = response.headers.get_content_charset() or "utf-8"

    return raw_html.decode(charset, errors="replace")


def parse_duckduckgo_page(html, max_results=10):
    parser = DuckDuckGoResultsParser()
    parser.feed(html)
    parser.close()
    return parser.results[:max_results], parser.next_params


def parse_duckduckgo_results(html, max_results=10):
    results, _next_params = parse_duckduckgo_page(html, max_results)
    return results


def search_web(
    query,
    provider=DEFAULT_WEB_SEARCH_PROVIDER,
    max_results=10,
    fetcher=fetch_search_page,
):
    from .hybrid_search import normalize_result_limit

    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    result_limit = normalize_result_limit(max_results)
    provider = provider if provider in WEB_SEARCH_URLS else DEFAULT_WEB_SEARCH_PROVIDER

    if provider == "duckduckgo":
        results = []
        seen_urls = set()
        max_pages = min(
            8,
            max(1, ceil(result_limit / DUCKDUCKGO_RESULTS_PER_PAGE) + 1),
        )
        search_url = build_web_search_url(cleaned_query, provider)

        for _page_number in range(max_pages):
            html = fetcher(search_url)
            page_results, next_params = parse_duckduckgo_page(
                html,
                result_limit - len(results),
            )

            if not page_results:
                break

            for result in page_results:
                if result.url in seen_urls:
                    continue

                results.append(result)
                seen_urls.add(result.url)

                if len(results) >= result_limit:
                    break

            if len(results) >= result_limit:
                break

            if not next_params:
                break

            search_url = build_duckduckgo_next_url(next_params)

        return results

    return []
