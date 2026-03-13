import shutil
import os
from datetime import datetime
from tkinter import filedialog
import sqlite3


def crear_backup():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    db_origen = os.path.join(BASE_DIR, "..", "gym.db")

    carpeta_backup = os.path.join(BASE_DIR, "..", "backups")

    # crear carpeta si no existe
    os.makedirs(carpeta_backup, exist_ok=True)

    # fecha automática
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    nombre_backup = f"gym_backup_{fecha}.db"

    db_destino = os.path.join(carpeta_backup, nombre_backup)

    # copia segura
    shutil.copy2(db_origen, db_destino)

    return db_destino


def restaurar_backup():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    db_destino = os.path.join(BASE_DIR, "..", "gym.db")

    archivo_backup = filedialog.askopenfilename(
        title="Seleccionar backup",
        filetypes=[("Base de datos SQLite", "*.db")]
    )

    if not archivo_backup:
        return None

    # eliminar base actual primero
    if os.path.exists(db_destino):
        os.remove(db_destino)

    shutil.copy2(archivo_backup, db_destino)

    return archivo_backup