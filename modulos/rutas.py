import os
import sys
from database.db_path import get_db_path as _get_db_path

def get_app_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(os.environ.get("APPDATA", ""), "GymSystem")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, ".."))

def get_db_path() -> str:
    return _get_db_path()

def get_config_path() -> str:
    path = get_app_dir()
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "config.json")

def get_backup_dir() -> str:
    path = os.path.join(get_app_dir(), "backups")
    os.makedirs(path, exist_ok=True)
    return path

def get_assets_dir() -> str:
    path = os.path.join(get_app_dir(), "assets")
    os.makedirs(path, exist_ok=True)
    return path