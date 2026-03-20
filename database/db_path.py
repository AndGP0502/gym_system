import os
import sys


def get_db_path() -> str:
    """
    Ruta correcta de gym.db tanto en desarrollo como en .exe compilado.
    - .exe  → junto al ejecutable (sys.executable), nunca en _MEIPASS
    - script → raíz del proyecto (un nivel arriba de cualquier subcarpeta)
    """
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "gym.db")
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, "gym.db")
    if os.path.exists(candidate):
        return candidate
    return os.path.normpath(os.path.join(here, "..", "gym.db"))


DB_PATH = get_db_path()