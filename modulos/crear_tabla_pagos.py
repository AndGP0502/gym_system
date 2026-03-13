import sqlite3
import os

conexion = sqlite3.connect("gym.db")

# activar claves foraneas
conexion.execute("PRAGMA foreign_keys = ON")

cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suscripcion_id INTEGER,
    monto REAL CHECK(monto > 0),
    fecha_pago TEXT,
    FOREIGN KEY (suscripcion_id) REFERENCES suscripciones(id)
)
""")

conexion.commit()
conexion.close()

print("Tabla pagos creada correctamente")