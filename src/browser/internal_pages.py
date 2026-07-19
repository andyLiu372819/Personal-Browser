from pathlib import Path
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERNAL_PAGES_DIR = PROJECT_ROOT / "data" / "internal_pages"
INTERNAL_BROWSER_SCHEME = "personal-browser"
INTERNAL_HOME_URL = f"{INTERNAL_BROWSER_SCHEME}://home"
INTERNAL_SEARCH_URL = f"{INTERNAL_BROWSER_SCHEME}://search"


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
    url_text = url.toString() if hasattr(url, "toString") else str(url)
    parsed_url = urlparse(url_text)

    if (
        parsed_url.scheme != INTERNAL_BROWSER_SCHEME
        or parsed_url.netloc != "search"
    ):
        return None

    values = parse_qs(parsed_url.query).get("q", [""])
    return values[0].strip()
