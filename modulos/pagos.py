import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "gym.db")

conexion = sqlite3.connect(DB_PATH)

def registrar_pago(suscripcion_id, monto):

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    if monto <= 0:
        print("Monto inválido")
        conexion.close()
        return

    # verificar suscripcion
    cursor.execute("""
    SELECT precio_total, pagado
    FROM suscripciones
    WHERE id = ?
    """, (suscripcion_id,))

    datos = cursor.fetchone()

    if datos is None:
        print("La suscripción no existe")
        conexion.close()
        return

    precio_total, pagado_actual = datos

    if pagado_actual >= precio_total:
        print("La suscripción ya está pagada completamente")
        conexion.close()
        return

    nuevo_pagado = pagado_actual + monto

    if nuevo_pagado > precio_total:
        nuevo_pagado = precio_total

    pendiente = max(0, precio_total - nuevo_pagado)

    # actualizar suscripcion
    cursor.execute("""
    UPDATE suscripciones
    SET pagado = ?, pendiente = ?
    WHERE id = ?
    """, (nuevo_pagado, pendiente, suscripcion_id))

    # guardar historial
    fecha = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO pagos (suscripcion_id, monto, fecha_pago)
    VALUES (?, ?, ?)
    """, (suscripcion_id, monto, fecha))

    conexion.commit()
    conexion.close()

    print("Pago registrado correctamente")

def ver_historial_pagos(suscripcion_id):

    import sqlite3

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, monto, fecha_pago
        FROM pagos
        WHERE suscripcion_id = ?
        ORDER BY fecha_pago
    """, (suscripcion_id,))

    datos = cursor.fetchall()


    conexion.close()

    return datos

def listar_suscripciones_para_pago():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        c.id,
        c.nombre,
        s.id,
        m.nombre_plan,
        s.precio_total,
        s.pagado,
        s.pendiente,
        s.fecha_inicio,
        s.fecha_vencimiento
    FROM suscripciones s
    JOIN clientes c ON s.cliente_id = c.id
    JOIN membresias m ON s.membresia_id = m.id
    ORDER BY s.id
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos

def eliminar_pago(pago_id):

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # obtener datos del pago
    cursor.execute(
        "SELECT suscripcion_id, monto FROM pagos WHERE id = ?",
        (pago_id,)
    )

    pago = cursor.fetchone()

    if not pago:
        conexion.close()
        return False

    suscripcion_id, monto = pago

    # eliminar pago
    cursor.execute(
        "DELETE FROM pagos WHERE id = ?",
        (pago_id,)
    )

    # actualizar suscripción
    cursor.execute("""
        UPDATE suscripciones
        SET pagado = pagado - ?
        WHERE id = ?
    """, (monto, suscripcion_id))

    cursor.execute("""
        UPDATE suscripciones
        SET pendiente = precio_total - pagado
        WHERE id = ?
    """, (suscripcion_id,))

    conexion.commit()
    conexion.close()

    return True


def buscar_cliente_pagos(cliente_id):

    import sqlite3

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        s.id,
        c.nombre,
        m.nombre_plan,
        s.precio_total,
        s.pagado,
        s.pendiente,
        s.fecha_inicio,
        s.fecha_vencimiento
    FROM suscripciones s
    JOIN clientes c ON s.cliente_id = c.id
    JOIN membresias m ON s.membresia_id = m.id
    WHERE c.id = ?
    """, (cliente_id,))

    datos = cursor.fetchall()

    conexion.close()
    
    return datos