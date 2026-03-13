import database.database
from ui.ventana_princi import iniciar_ventana
from modulos.backup_db import crear_backup
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

crear_backup()
if __name__ == "__main__":
    iniciar_ventana()