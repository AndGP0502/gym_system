import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

from database.database import inicializar_base_datos
inicializar_base_datos()

from ui.ventana_princi import iniciar_ventana

if __name__ == "__main__":
    iniciar_ventana()