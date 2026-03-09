import sqlite3
from datetime import datetime


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

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id, monto, fecha_pago
    FROM pagos
    WHERE suscripcion_id = ?
    ORDER BY fecha_pago
    """, (suscripcion_id,))

    pagos = cursor.fetchall()

    conexion.close()

    return pagos

def listar_suscripciones_para_pago():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT suscripciones.id,
           clientes.nombre,
           suscripciones.pendiente
    FROM suscripciones
    JOIN clientes ON suscripciones.cliente_id = clientes.id
    WHERE suscripciones.pendiente > 0
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos