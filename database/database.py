import sqlite3

conexion = sqlite3.connect("gym.db")

cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nombre TEXT,
telefono TEXT,
fecha_registro TEXT
)
""")

conexion.commit()

print("Tabla clientes creada")

conexion.close()