import json
from datetime import datetime

from paths import user_data_path


HISTORY_FILE = user_data_path("history.json")


def load_history():
    if not HISTORY_FILE.exists():
        return []

    with HISTORY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)
        file.write("\n")


def add_history_entry(title, url):
    history = load_history()

    entry = {
        "title": title,
        "url": url,
        "visited_at": datetime.now().isoformat(timespec="seconds"),
    }

    history.append(entry)
    save_history(history)
