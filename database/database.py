import sqlite3

conexion = sqlite3.connect("gym.db")
cursor = conexion.cursor()

# Tabla clientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nombre TEXT,
telefono TEXT,
fecha_registro TEXT
)
""")

# Tabla membresias
cursor.execute("""
CREATE TABLE IF NOT EXISTS membresias(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nombre_plan TEXT,
precio REAL,
duracion_dias INTEGER
)
""")

# Tabla pagos
cursor.execute("""
CREATE TABLE IF NOT EXISTS pagos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
cliente_id INTEGER,
monto REAL,
fecha_pago TEXT
)
""")

# Tabla de pagos parciales
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



# Tabla suscripciones (para controlar membresías activas)
cursor.execute("""
CREATE TABLE IF NOT EXISTS suscripciones(
id INTEGER PRIMARY KEY AUTOINCREMENT,
cliente_id INTEGER,
membresia_id INTEGER,
fecha_inicio TEXT,
fecha_vencimiento TEXT
)
""")

conexion.commit()

print("Base de datos del gimnasio creada correctamente")

conexion.close()