import sqlite3

conexion = sqlite3.connect("gym.db")

conexion.execute("PRAGMA foreign_keys = ON")

cursor = conexion.cursor()

# activar claves foraneas
conexion.execute("PRAGMA foreign_keys = ON")

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

# tabla de cada pago que se hace
cursor.execute("""
CREATE TABLE IF NOT EXISTS pagos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
suscripcion_id INTEGER,
monto REAL,
fecha_pago TEXT,
FOREIGN KEY(suscripcion_id) REFERENCES suscripciones(id)
)
""")

conexion.commit()

print("Base de datos y tablas creadas correctamente")

conexion.close()


