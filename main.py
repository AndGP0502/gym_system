import sys
import os
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database.database
from ui.ventana_princi import iniciar_ventana
from modulos.backup_db import crear_backup

if __name__ == "__main__":
    crear_backup()


    iniciar_ventana()