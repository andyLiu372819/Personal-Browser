from dataclasses import dataclass

from search_engine import (
    DEFAULT_EXTERNAL_SEARCH_ENGINE,
    PERSONAL_SEARCH_ENGINE,
    build_url_from_input,
    looks_like_url,
    render_results_page,
    search,
    uses_personal_search,
)


@dataclass(frozen=True)
class AddressBarAction:
    kind: str
    content: str


def resolve_address_bar_input(
    text,
    search_engine_name=PERSONAL_SEARCH_ENGINE,
    fallback_search_engine_name=DEFAULT_EXTERNAL_SEARCH_ENGINE,
    search_function=search,
    render_function=render_results_page,
):
    cleaned_text = text.strip()

    if not cleaned_text:
        return AddressBarAction("empty", "")

    if cleaned_text.startswith(("https://", "http://")) or looks_like_url(
        cleaned_text
    ):
        url = build_url_from_input(cleaned_text, search_engine_name)
        return AddressBarAction("url", url)

    if not uses_personal_search(search_engine_name):
        url = build_url_from_input(cleaned_text, search_engine_name)
        return AddressBarAction("url", url)

    results = search_function(cleaned_text)
    if not results:
        url = build_url_from_input(cleaned_text, fallback_search_engine_name)
        return AddressBarAction("url", url)

    html = render_function(cleaned_text, results)
    return AddressBarAction("html", html)
