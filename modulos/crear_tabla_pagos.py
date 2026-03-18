import sqlite3
import os
import sys


def _get_db_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "gym.db")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "gym.db"))


DB_PATH = _get_db_path()

con = sqlite3.connect(DB_PATH)
con.execute("PRAGMA foreign_keys = ON")
cur = con.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS pagos (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        suscripcion_id INTEGER,
        monto          REAL CHECK(monto > 0),
        fecha_pago     TEXT,
        FOREIGN KEY (suscripcion_id) REFERENCES suscripciones(id)
    )
""")

con.commit()
con.close()
print("Tabla pagos creada correctamente")