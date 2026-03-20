import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import inicializar_base_datos
inicializar_base_datos()

from ui.ventana_princi import iniciar_ventana

if __name__ == "__main__":
    iniciar_ventana()