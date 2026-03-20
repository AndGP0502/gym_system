import os
import sys
from database.db_path import get_db_path as _get_db_path


def get_app_dir() -> str:
    """Carpeta raíz de la aplicación — junto al .exe o raíz del proyecto."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, ".."))


def get_db_path() -> str:
    return _get_db_path()


def get_config_path() -> str:
    return os.path.join(get_app_dir(), "config.json")


def get_backup_dir() -> str:
    path = os.path.join(get_app_dir(), "backups")
    os.makedirs(path, exist_ok=True)
    return path


def get_assets_dir() -> str:
    return os.path.join(get_app_dir(), "assets")