import os
import sys


def get_db_path() -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.join(os.environ.get("APPDATA", ""), "GymSystem")
        os.makedirs(base, exist_ok=True)
        return os.path.join(base, "gym.db")
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, "gym.db")
    if os.path.exists(candidate):
        return candidate
    candidate = os.path.join(here, "..", "gym.db")
    return os.path.normpath(candidate)