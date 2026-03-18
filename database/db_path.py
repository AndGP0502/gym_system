import os
import sys


def get_db_path() -> str:
    """
    Ruta correcta de gym.db tanto en desarrollo como en .exe compilado.
    - .exe  → junto al ejecutable (sys.executable), nunca en _MEIPASS
    - script → raíz del proyecto (un nivel arriba de cualquier subcarpeta)
    """
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        # Sube hasta encontrar gym.db o usa la raíz del proyecto
        here = os.path.dirname(os.path.abspath(__file__))
        # Si estamos en database/ o modulos/, subir un nivel
        candidate = os.path.join(here, "gym.db")
        if os.path.exists(candidate):
            return candidate
        candidate = os.path.join(here, "..", "gym.db")
        return os.path.normpath(candidate)
    return os.path.join(base, "gym.db")


DB_PATH = get_db_path()