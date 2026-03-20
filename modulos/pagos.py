import sqlite3
import os
from datetime import datetime

from modulos.rutas import get_db_path
DB_PATH = get_db_path()


def _con():
    return sqlite3.connect(DB_PATH)


def registrar_pago(suscripcion_id, monto):
    con = _con()
    cursor = con.cursor()

    if monto <= 0:
        print("Monto invalido")
        con.close()
        return

    cursor.execute("""
        SELECT precio_total, pagado
        FROM suscripciones
        WHERE id = ?
    """, (suscripcion_id,))
    datos = cursor.fetchone()

    if datos is None:
        print("La suscripcion no existe")
        con.close()
        return

    precio_total, pagado_actual = float(datos[0]), float(datos[1])

    if precio_total > 0 and pagado_actual >= precio_total:
        print("La suscripcion ya esta pagada completamente")
        con.close()
        return

    nuevo_pagado = pagado_actual + monto

    if precio_total == 0:
        nuevo_precio_total = nuevo_pagado
        nuevo_pendiente    = 0.0
    else:
        nuevo_precio_total = precio_total
        nuevo_pagado       = min(nuevo_pagado, precio_total)
        nuevo_pendiente    = max(0, nuevo_precio_total - nuevo_pagado)

    cursor.execute("""
        UPDATE suscripciones
        SET pagado = ?, pendiente = ?, precio_total = ?
        WHERE id = ?
    """, (nuevo_pagado, nuevo_pendiente, nuevo_precio_total, suscripcion_id))

    fecha = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO pagos (suscripcion_id, monto, fecha_pago)
        VALUES (?, ?, ?)
    """, (suscripcion_id, monto, fecha))

    con.commit()
    con.close()
    print("Pago registrado correctamente")


def ver_historial_pagos(suscripcion_id):
    con = _con()
    cursor = con.cursor()
    cursor.execute("""
        SELECT id, monto, fecha_pago
        FROM pagos
        WHERE suscripcion_id = ?
        ORDER BY fecha_pago
    """, (suscripcion_id,))
    datos = cursor.fetchall()
    con.close()
    return datos


def listar_suscripciones_para_pago():
    con = _con()
    cursor = con.cursor()
    cursor.execute("""
        SELECT
            c.id, c.nombre, s.id, m.nombre_plan,
            s.precio_total, s.pagado, s.pendiente,
            s.fecha_inicio, s.fecha_vencimiento
        FROM suscripciones s
        JOIN clientes   c ON s.cliente_id   = c.id
        JOIN membresias m ON s.membresia_id = m.id
        ORDER BY s.id
    """)
    datos = cursor.fetchall()
    con.close()
    return datos


def eliminar_pago(pago_id):
    con = _con()
    cursor = con.cursor()
    cursor.execute("SELECT suscripcion_id, monto FROM pagos WHERE id = ?", (pago_id,))
    pago = cursor.fetchone()
    if not pago:
        con.close()
        return False
    suscripcion_id, monto = pago
    cursor.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))
    cursor.execute("""
        UPDATE suscripciones
        SET pagado    = pagado - ?,
            pendiente = MAX(0, precio_total - (pagado - ?))
        WHERE id = ?
    """, (monto, monto, suscripcion_id))
    con.commit()
    con.close()
    return True


def buscar_cliente_pagos(cliente_id):
    con = _con()
    cursor = con.cursor()
    cursor.execute("""
        SELECT
            s.id, c.nombre, m.nombre_plan,
            s.precio_total, s.pagado, s.pendiente,
            s.fecha_inicio, s.fecha_vencimiento
        FROM suscripciones s
        JOIN clientes   c ON s.cliente_id   = c.id
        JOIN membresias m ON s.membresia_id = m.id
        WHERE c.id = ?
    """, (cliente_id,))
    datos = cursor.fetchall()
    con.close()
    return datos