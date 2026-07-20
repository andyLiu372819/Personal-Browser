from dataclasses import dataclass

from search_engine import (
    DEFAULT_EXTERNAL_SEARCH_ENGINE,
    DEFAULT_SEARCH_RESULT_LIMIT,
    PERSONAL_SEARCH_ENGINE,
    build_url_from_input,
    looks_like_url,
    normalize_result_limit,
    personal_search,
    render_results_page,
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
    result_limit=DEFAULT_SEARCH_RESULT_LIMIT,
    search_function=personal_search,
    render_function=render_results_page,
):
    cleaned_text = text.strip()
    result_limit = normalize_result_limit(result_limit)

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

    results = search_function(cleaned_text, max_results=result_limit)
    html = render_function(cleaned_text, results, result_limit=result_limit)
    return AddressBarAction("html", html)
