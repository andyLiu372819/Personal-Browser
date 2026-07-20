from urllib.parse import urlparse

from history import load_history

from .local_search import Document, search as search_local
from .web_search import DEFAULT_WEB_SEARCH_PROVIDER, search_web


DEFAULT_SEARCH_RESULT_LIMIT = 10
MAX_SEARCH_RESULT_LIMIT = 100
MIN_SEARCH_RESULT_LIMIT = 1
SEARCH_RESULT_LIMIT_OPTIONS = (10, 25, 50, 75, 100)
WEB_RESULT_SCORE = 1
HISTORY_VISIT_BONUS = 5


def normalize_result_limit(value, default=DEFAULT_SEARCH_RESULT_LIMIT):
    try:
        result_limit = int(value)
    except (TypeError, ValueError):
        result_limit = default

    return max(MIN_SEARCH_RESULT_LIMIT, min(result_limit, MAX_SEARCH_RESULT_LIMIT))


def normalize_history_url(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        return None

    path = (parsed_url.path or "/").rstrip("/") or "/"
    return f"{parsed_url.scheme.lower()}://{parsed_url.netloc.lower()}{path}"


def history_site_key(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        return None

    return parsed_url.netloc.lower()


def latest_visit(first_visit, second_visit):
    if not first_visit:
        return second_visit

    if not second_visit:
        return first_visit

    return max(first_visit, second_visit)


def build_history_index(history_entries=None, history_loader=load_history):
    if history_entries is None:
        history_entries = history_loader()

    visits_by_url = {}
    visits_by_site = {}

    for entry in history_entries:
        url = entry.get("url", "")
        visited_at = entry.get("visited_at")
        url_key = normalize_history_url(url)
        site_key = history_site_key(url)

        if url_key:
            visits_by_url[url_key] = latest_visit(visits_by_url.get(url_key), visited_at)

        if site_key:
            visits_by_site[site_key] = latest_visit(
                visits_by_site.get(site_key),
                visited_at,
            )

    return {"urls": visits_by_url, "sites": visits_by_site}


def history_visit_for_url(url, history_index):
    url_key = normalize_history_url(url)
    site_key = history_site_key(url)

    if url_key and url_key in history_index["urls"]:
        return history_index["urls"][url_key]

    if site_key and site_key in history_index["sites"]:
        return history_index["sites"][site_key]

    return None


def apply_history_boost(results, history_entries=None, history_loader=load_history):
    history_index = build_history_index(history_entries, history_loader)
    boosted_results = []

    for result_score, document in results:
        visited_at = history_visit_for_url(document.url, history_index)

        if visited_at:
            document.visited_at = visited_at
            result_score += HISTORY_VISIT_BONUS

        boosted_results.append((result_score, document))

    boosted_results.sort(key=lambda result: result[0], reverse=True)
    return boosted_results


def personal_search(
    query,
    documents=None,
    web_provider=DEFAULT_WEB_SEARCH_PROVIDER,
    max_results=DEFAULT_SEARCH_RESULT_LIMIT,
    max_web_results=None,
    local_search_function=search_local,
    web_search_function=search_web,
    history_entries=None,
    history_loader=load_history,
):
    result_limit = normalize_result_limit(
        max_web_results if max_web_results is not None else max_results
    )
    local_results = local_search_function(query, documents)
    results = []
    seen_urls = set()

    for result_score, document in local_results:
        if document.url in seen_urls:
            continue

        results.append((result_score, document))
        seen_urls.add(document.url)

    try:
        web_results = web_search_function(
            query,
            provider=web_provider,
            max_results=result_limit,
        )
    except Exception:
        web_results = []

    for web_result in web_results:
        if web_result.url in seen_urls:
            continue

        results.append(
            (
                WEB_RESULT_SCORE,
                Document(
                    web_result.title,
                    web_result.url,
                    "web",
                    False,
                    None,
                    web_result.snippet,
                ),
            )
        )
        seen_urls.add(web_result.url)

    return apply_history_boost(
        results,
        history_entries=history_entries,
        history_loader=history_loader,
    )[:result_limit]
