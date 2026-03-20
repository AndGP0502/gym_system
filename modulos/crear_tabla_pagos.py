import sqlite3
import os

from modulos.rutas import get_db_path
DB_PATH = get_db_path()

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