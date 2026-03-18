import sqlite3
import os
import sys

<<<<<<< HEAD
=======

def obtener_ruta_db():
    if getattr(sys, 'frozen', False):
        # Cuando corre como .exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Cuando corre como proyecto normal en Python
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.abspath(os.path.join(base_path, ".."))

    return os.path.join(base_path, "gym.db")


DB_PATH = obtener_ruta_db()
>>>>>>> b85ef348a5d9369008925001f98a0aa5fda198bf

def get_db_path() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "gym.db")

<<<<<<< HEAD
=======
# activar claves foráneas
conexion.execute("PRAGMA foreign_keys = ON")
>>>>>>> b85ef348a5d9369008925001f98a0aa5fda198bf

DB_PATH = get_db_path()

<<<<<<< HEAD
# Solo crear tablas, NUNCA sobreescribir datos existentes
con = sqlite3.connect(DB_PATH)
con.execute("PRAGMA foreign_keys = ON")
cur = con.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes(
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre         TEXT,
        cedula         TEXT,
        telefono       TEXT,
        fecha_registro TEXT
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS membresias(
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_plan   TEXT,
        precio        REAL,
        duracion_dias INTEGER
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS suscripciones(
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id        INTEGER,
        membresia_id      INTEGER,
        fecha_inicio      TEXT,
        fecha_vencimiento TEXT,
        precio_total      REAL,
        pagado            REAL,
        pendiente         REAL,
        FOREIGN KEY(cliente_id)   REFERENCES clientes(id),
        FOREIGN KEY(membresia_id) REFERENCES membresias(id)
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS pagos(
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        suscripcion_id INTEGER,
        monto          REAL,
        fecha_pago     TEXT,
        FOREIGN KEY(suscripcion_id) REFERENCES suscripciones(id)
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS alertas_enviadas(
        id_cliente   INTEGER,
        fecha_alerta TEXT,
        PRIMARY KEY (id_cliente, fecha_alerta)
    )
""")

con.commit()
con.close()
print(f"Base de datos lista en: {DB_PATH}")
=======
# tabla clientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    cedula TEXT,
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
    pendiente REAL,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id),
    FOREIGN KEY(membresia_id) REFERENCES membresias(id)
)
""")

# tabla pagos
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
conexion.close()

print("Base de datos lista")
>>>>>>> b85ef348a5d9369008925001f98a0aa5fda198bf
