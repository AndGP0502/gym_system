import sqlite3
from datetime import datetime, timedelta

#funcion para asignar una membresia a un cliente

def asignar_membresia(cliente_id, membresia_id, precio_total, pagado):

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    fecha_inicio = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT duracion_dias FROM membresias WHERE id = ?", (membresia_id,))
    duracion = cursor.fetchone()[0]

    fecha_vencimiento = (datetime.now() + timedelta(days=duracion)).strftime("%Y-%m-%d")

    pendiente = precio_total - pagado

    cursor.execute("""
    INSERT INTO suscripciones(
    cliente_id,
    membresia_id,
    fecha_inicio,
    fecha_vencimiento,
    precio_total,
    pagado,
    pendiente
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cliente_id, membresia_id, fecha_inicio, fecha_vencimiento, precio_total, pagado, pendiente))

    conexion.commit()
    conexion.close()

    print("Membresía asignada correctamente")

def ver_suscripciones():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM suscripciones")

    datos = cursor.fetchall()

    conexion.close()

    return datos