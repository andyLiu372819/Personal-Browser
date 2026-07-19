from dataclasses import dataclass

from search_engine import (
    build_url_from_input,
    looks_like_url,
    render_results_page,
    search,
)


@dataclass(frozen=True)
class AddressBarAction:
    kind: str
    content: str


def resolve_address_bar_input(
    text,
    search_engine_name="duckduckgo",
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

    results = search_function(cleaned_text)
    html = render_function(cleaned_text, results)
    return AddressBarAction("html", html)
