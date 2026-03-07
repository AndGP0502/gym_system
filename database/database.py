import sqlite3

conexion = sqlite3.connect("gym.db")

cursor = conexion.cursor()

# tabla clientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nombre TEXT,
telefono TEXT,
fecha_registro TEXT
)
""")

# tabla membresias
cursor.execute("""
CREATE TABLE IF NOT EXISTS membresias(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nombre_plan TEXT,
precio REAL,
duracion_dias INTEGER
)
""")

# tabla suscripciones
cursor.execute("""
CREATE TABLE IF NOT EXISTS suscripciones(
id INTEGER PRIMARY KEY AUTOINCREMENT,
cliente_id INTEGER,
membresia_id INTEGER,
fecha_inicio TEXT,
fecha_vencimiento TEXT,
precio_total REAL,
pagado REAL,
pendiente REAL
)
""")

conexion.commit()

print("Base de datos y tablas creadas correctamente")

conexion.close()


