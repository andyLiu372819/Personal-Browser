import json
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = PROJECT_ROOT / "data" / "history.json"


def load_history():
    if not HISTORY_FILE.exists():
        return []

    with HISTORY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_history(history):
    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)


def add_history_entry(title, url):
    history = load_history()

    entry = {
        "title": title,
        "url": url,
        "visited_at": datetime.now().isoformat(timespec="seconds"),
    }

    history.append(entry)
    save_history(history)
