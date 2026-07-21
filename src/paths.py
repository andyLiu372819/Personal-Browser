import os
import sys
from pathlib import Path

from theme import APP_NAME, APP_SLUG


def is_frozen():
    return bool(getattr(sys, "frozen", False))


def project_root():
    return Path(__file__).resolve().parent.parent


def resource_root():
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))

    return project_root()


def resource_path(*parts):
    return resource_root().joinpath(*parts)


def user_data_dir():
    if not is_frozen():
        return project_root() / "data"

    roaming_app_data = os.environ.get("APPDATA")
    if roaming_app_data:
        return Path(roaming_app_data) / APP_NAME

    return Path.home() / f".{APP_SLUG.lower()}"


def user_data_path(*parts):
    return user_data_dir().joinpath(*parts)
