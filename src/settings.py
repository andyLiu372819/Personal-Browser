import json

from search_engine import (
    DEFAULT_CRAWLER_MAX_DEPTH,
    DEFAULT_CRAWLER_MAX_PAGES,
    DEFAULT_SEARCH_RESULT_LIMIT,
    normalize_crawler_depth,
    normalize_crawler_page_limit,
    normalize_result_limit,
)
from search_engine.routing import SEARCH_URLS
from paths import user_data_path
from theme import (
    DEFAULT_CUSTOM_ACCENT_COLOR,
    DEFAULT_THEME_ACCENT,
    DEFAULT_THEME_MODE,
    THEME_MODES,
    normalize_hex_color,
    normalize_theme_accent,
    normalize_theme_mode,
)


SETTINGS_FILE = user_data_path("settings.json")
INTERNAL_HOME_URL = "personal-browser://home"
SEARCH_ENGINE_OPTIONS = ("personal", *SEARCH_URLS)
EXTERNAL_SEARCH_ENGINE_OPTIONS = tuple(SEARCH_URLS)

DEFAULT_SETTINGS = {
    "homepage": INTERNAL_HOME_URL,
    "default_search_engine": "personal",
    "fallback_search_engine": "duckduckgo",
    "search_results_limit": DEFAULT_SEARCH_RESULT_LIMIT,
    "crawler_max_pages": DEFAULT_CRAWLER_MAX_PAGES,
    "crawler_max_depth": DEFAULT_CRAWLER_MAX_DEPTH,
    "theme": DEFAULT_THEME_MODE,
    "theme_mode": DEFAULT_THEME_MODE,
    "theme_accent": DEFAULT_THEME_ACCENT,
    "custom_accent_color": DEFAULT_CUSTOM_ACCENT_COLOR,
}


def normalize_search_engine(value):
    return value if value in SEARCH_ENGINE_OPTIONS else "personal"


def normalize_external_search_engine(value):
    return value if value in EXTERNAL_SEARCH_ENGINE_OPTIONS else "duckduckgo"


def normalize_homepage(value):
    if not isinstance(value, str):
        return INTERNAL_HOME_URL

    value = value.strip()
    return value or INTERNAL_HOME_URL


def normalize_settings(settings):
    raw_settings = settings or {}
    normalized = DEFAULT_SETTINGS | raw_settings

    if "theme_mode" not in raw_settings and raw_settings.get("theme") in THEME_MODES:
        normalized["theme_mode"] = raw_settings["theme"]

    normalized["homepage"] = normalize_homepage(normalized.get("homepage"))
    normalized["default_search_engine"] = normalize_search_engine(
        normalized.get("default_search_engine")
    )
    normalized["fallback_search_engine"] = normalize_external_search_engine(
        normalized.get("fallback_search_engine")
    )
    normalized["search_results_limit"] = normalize_result_limit(
        normalized.get("search_results_limit")
    )
    normalized["crawler_max_pages"] = normalize_crawler_page_limit(
        normalized.get("crawler_max_pages")
    )
    normalized["crawler_max_depth"] = normalize_crawler_depth(
        normalized.get("crawler_max_depth")
    )
    normalized["theme_mode"] = normalize_theme_mode(normalized.get("theme_mode"))
    normalized["theme"] = normalized["theme_mode"]
    normalized["theme_accent"] = normalize_theme_accent(normalized.get("theme_accent"))
    normalized["custom_accent_color"] = normalize_hex_color(
        normalized.get("custom_accent_color")
    )

    return normalized


def load_settings(file_path=SETTINGS_FILE):
    if not file_path.exists():
        return DEFAULT_SETTINGS.copy()

    with file_path.open("r", encoding="utf-8") as file:
        settings = json.load(file)

    return normalize_settings(settings)


def save_settings(settings, file_path=SETTINGS_FILE):
    normalized_settings = normalize_settings(settings)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(normalized_settings, file, indent=2)
        file.write("\n")

    return normalized_settings
