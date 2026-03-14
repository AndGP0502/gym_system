"""
reset_db.py
Ejecuta este script UNA SOLA VEZ desde la raíz del proyecto.
Borra todos los datos y reinicia los contadores de ID.
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "gym.db")

con = sqlite3.connect(DB_PATH)

tablas = ["pagos", "suscripciones", "alertas_enviadas", "membresias", "clientes"]

for tabla in tablas:
    try:
        con.execute(f"DELETE FROM {tabla}")
        con.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabla}'")
        print(f"✅ Tabla '{tabla}' limpiada")
    except sqlite3.OperationalError as e:
        print(f"⚠️  '{tabla}' omitida ({e})")

con.commit()
con.close()

print("\n🎉 Base de datos reseteada. Los IDs vuelven a empezar desde 1.")