import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILE = PROJECT_ROOT / "data" / "settings.json"

DEFAULT_SETTINGS = {
    "homepage": "personal-browser://home",
    "default_search_engine": "personal",
    "fallback_search_engine": "duckduckgo",
    "theme": "dark",
}


def load_settings():
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    with SETTINGS_FILE.open("r", encoding="utf-8") as file:
        settings = json.load(file)

    return DEFAULT_SETTINGS | settings
