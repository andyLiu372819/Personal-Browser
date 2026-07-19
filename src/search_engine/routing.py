from urllib.parse import quote_plus


SEARCH_URLS = {
    "duckduckgo": "https://duckduckgo.com/?q={query}",
    "google": "https://www.google.com/search?q={query}",
    "bing": "https://www.bing.com/search?q={query}",
}

PERSONAL_SEARCH_ENGINE = "personal"
DEFAULT_EXTERNAL_SEARCH_ENGINE = "duckduckgo"


def looks_like_url(text):
    return "." in text and " " not in text


def build_url_from_input(text, search_engine="duckduckgo"):
    cleaned_text = text.strip()

    if cleaned_text.startswith(("https://", "http://")):
        return cleaned_text

    if looks_like_url(cleaned_text):
        return f"https://{cleaned_text}"

    query = quote_plus(cleaned_text)
    search_url = SEARCH_URLS.get(search_engine, SEARCH_URLS[DEFAULT_EXTERNAL_SEARCH_ENGINE])
    return search_url.format(query=query)


def uses_personal_search(search_engine):
    return search_engine == PERSONAL_SEARCH_ENGINE
