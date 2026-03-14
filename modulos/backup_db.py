import os
import sqlite3
from datetime import datetime
from tkinter import filedialog, messagebox

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DB_PATH       = os.path.join(BASE_DIR, "..", "gym.db")
CARPETA_BACKUP = os.path.join(BASE_DIR, "..", "backups")


def crear_backup() -> str:
    """
    Crea un backup de gym.db usando la API nativa de SQLite.
    Garantiza que todos los datos estén escritos antes de copiar.
    Devuelve la ruta del archivo de backup creado.
    """
    os.makedirs(CARPETA_BACKUP, exist_ok=True)

    fecha        = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre       = f"gym_backup_{fecha}.db"
    ruta_backup  = os.path.join(CARPETA_BACKUP, nombre)

    # Conexión origen
    con_origen = sqlite3.connect(DB_PATH)

    # Conexión destino (crea el archivo)
    con_backup = sqlite3.connect(ruta_backup)

    # API nativa — copia página a página con todos los datos confirmados
    con_origen.backup(con_backup, pages=-1)

    con_backup.close()
    con_origen.close()

    return ruta_backup


def restaurar_backup() -> str | None:
    """
    Restaura un backup seleccionado por el usuario sobre gym.db.
    Verifica que el archivo seleccionado sea un SQLite válido antes de restaurar.
    Devuelve la ruta del backup restaurado o None si se canceló.
    """
    archivo_backup = filedialog.askopenfilename(
        title="Seleccionar backup a restaurar",
        filetypes=[("Base de datos SQLite", "*.db")],
        initialdir=CARPETA_BACKUP if os.path.exists(CARPETA_BACKUP) else "/"
    )

    if not archivo_backup:
        return None

    # Verificar que el archivo sea un SQLite válido antes de restaurar
    try:
        con_verificar = sqlite3.connect(archivo_backup)
        con_verificar.execute("SELECT name FROM sqlite_master LIMIT 1")
        con_verificar.close()
    except Exception:
        messagebox.showerror(
            "Archivo inválido",
            "El archivo seleccionado no es una base de datos SQLite válida."
        )
        return None

    # Restaurar usando API nativa — sin borrar el archivo original
    try:
        con_backup  = sqlite3.connect(archivo_backup)
        con_destino = sqlite3.connect(DB_PATH)

        # Vaciar la BD actual y copiar desde el backup
        con_backup.backup(con_destino, pages=-1)

        con_destino.close()
        con_backup.close()

    except Exception as e:
        messagebox.showerror("Error al restaurar", f"No se pudo restaurar el backup:\n{e}")
        return None

    return archivo_backup