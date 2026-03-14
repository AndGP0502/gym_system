import sys
import os
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database.database
from ui.ventana_princi import iniciar_ventana
from modulos.backup_db import crear_backup
from modulos.alertas import verificar_vencimientos

if __name__ == "__main__":
    crear_backup()

    # Ejecutar alertas en segundo plano para no bloquear la interfaz
    threading.Thread(target=verificar_vencimientos, daemon=True).start()

    iniciar_ventana()