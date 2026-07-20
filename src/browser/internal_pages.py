from pathlib import Path
from urllib.parse import parse_qs, urlparse

from search_engine import DEFAULT_SEARCH_RESULT_LIMIT, normalize_result_limit


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERNAL_PAGES_DIR = PROJECT_ROOT / "data" / "internal_pages"
INTERNAL_BROWSER_SCHEME = "personal-browser"
INTERNAL_HOME_URL = f"{INTERNAL_BROWSER_SCHEME}://home"
INTERNAL_SEARCH_URL = f"{INTERNAL_BROWSER_SCHEME}://search"


class InternalSearchRequest:
    def __init__(self, query, result_limit=DEFAULT_SEARCH_RESULT_LIMIT):
        self.query = query
        self.result_limit = normalize_result_limit(result_limit)


def write_internal_page(name, html):
    INTERNAL_PAGES_DIR.mkdir(parents=True, exist_ok=True)

    page_path = INTERNAL_PAGES_DIR / f"{name}.html"
    page_path.write_text(html, encoding="utf-8")
    return page_path


def is_internal_page_url(url, page_name=None):
    normalized_url = url.replace("\\", "/")
    is_internal = (
        normalized_url.startswith("file:///")
        and "/data/internal_pages/" in normalized_url
    )

    if not is_internal or page_name is None:
        return is_internal

    return normalized_url.endswith(f"/{page_name}.html")


def extract_internal_search_query(url):
    request = extract_internal_search_request(url)
    return request.query if request else None


def extract_internal_search_request(url):
    url_text = url.toString() if hasattr(url, "toString") else str(url)
    parsed_url = urlparse(url_text)

    if (
        parsed_url.scheme != INTERNAL_BROWSER_SCHEME
        or parsed_url.netloc != "search"
    ):
        return None

    parsed_query = parse_qs(parsed_url.query)
    values = parsed_query.get("q", [""])
    result_limits = parsed_query.get("limit", [DEFAULT_SEARCH_RESULT_LIMIT])

    return InternalSearchRequest(values[0].strip(), result_limits[0])
