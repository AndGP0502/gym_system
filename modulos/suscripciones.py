import sqlite3
from datetime import datetime, timedelta

#funcion para asignar una membresia a un cliente

def asignar_membresia(cliente_id, membresia_id, precio_total, pagado):

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # verificar rango de clientes
    cursor.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,))
    
    if cursor.fetchone() is None:
        print("El cliente no existe")
        conexion.close()
        return

    # verificar rango de membresias
    cursor.execute("SELECT id FROM membresias WHERE id = ?", (membresia_id,))
    
    if cursor.fetchone() is None:
        print("La membresía no existe")
        conexion.close()
        return

    fecha_inicio = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT duracion_dias FROM membresias WHERE id = ?", (membresia_id,))
    resultado = cursor.fetchone()
    
    if resultado is None:
        print("La membresía no existe")
        conexion.close()
        return
    
    duracion = resultado[0]

    fecha_vencimiento = (datetime.now() + timedelta(days=duracion)).strftime("%Y-%m-%d")

    pendiente = max(0, precio_total - pagado)

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

def ver_estado_gimnasio():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT suscripciones.id,
           clientes.nombre,
           membresias.nombre_plan,
           suscripciones.fecha_vencimiento,
           suscripciones.pagado,
           suscripciones.pendiente
    FROM suscripciones
    JOIN clientes ON suscripciones.cliente_id = clientes.id
    JOIN membresias ON suscripciones.membresia_id = membresias.id
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos

def ver_clientes_vencidos():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    hoy = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    SELECT clientes.nombre, suscripciones.fecha_vencimiento
    FROM suscripciones
    JOIN clientes ON suscripciones.cliente_id = clientes.id
    WHERE suscripciones.fecha_vencimiento < ?
    """, (hoy,))

    datos = cursor.fetchall()

    conexion.close()

    return datos


def registrar_pago(suscripcion_id, monto):

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT precio_total, pagado FROM suscripciones
    WHERE id = ?
    """, (suscripcion_id,))

    datos = cursor.fetchone()

    if datos is None:
        print("La suscripción no existe")
        conexion.close()
        return

    if monto <= 0:
        print("Monto inválido")
        conexion.close()
        return

    precio_total, pagado_actual = datos

    nuevo_pagado = pagado_actual + monto

    if nuevo_pagado > precio_total:
        nuevo_pagado = precio_total

    pendiente = precio_total - nuevo_pagado


    cursor.execute("""
    UPDATE suscripciones
    SET pagado = ?, pendiente = ?
    WHERE id = ?
    """, (nuevo_pagado, pendiente, suscripcion_id))

    conexion.commit()
    conexion.close()

    print("Pago registrado correctamente")

def ver_dias_restantes():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT clientes.nombre,
           membresias.nombre_plan,
           suscripciones.fecha_vencimiento
    FROM suscripciones
    JOIN clientes ON suscripciones.cliente_id = clientes.id
    JOIN membresias ON suscripciones.membresia_id = membresias.id
    """)

    datos = cursor.fetchall()

    hoy = datetime.now()

    resultados = []

    for nombre, plan, fecha_vencimiento in datos:

        fecha_v = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")

        dias_restantes = (fecha_v - hoy).days

        if dias_restantes < 0:
            estado = "VENCIDO"
        else:
            estado = f"{dias_restantes} dias"

        resultados.append((nombre, plan, estado))

    conexion.close()

    return resultados

def crear_suscripcion(cliente_id, membresia_id):

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # obtener datos de la membresía
    cursor.execute("""
        SELECT precio, duracion_dias
        FROM membresias
        WHERE id = ?
    """, (membresia_id,))

    datos = cursor.fetchone()

    if not datos:
        conexion.close()
        return

    precio, duracion = datos

    fecha_inicio = datetime.now().date()
    fecha_vencimiento = fecha_inicio + timedelta(days=duracion)

    pagado = 0
    pendiente = precio

    cursor.execute("""
        INSERT INTO suscripciones (
            cliente_id,
            membresia_id,
            fecha_inicio,
            fecha_vencimiento,
            precio_total,
            pagado,
            pendiente
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        cliente_id,
        membresia_id,
        fecha_inicio,
        fecha_vencimiento,
        precio,
        pagado,
        pendiente
    ))

    conexion.commit()
    conexion.close()

def clientes_por_vencer():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    hoy = datetime.now()

    cursor.execute("""
    SELECT clientes.nombre, suscripciones.fecha_vencimiento
    FROM suscripciones
    JOIN clientes ON suscripciones.cliente_id = clientes.id
    """)

    datos = cursor.fetchall()

    resultados = []

    for nombre, fecha_vencimiento in datos:

        fecha_v = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        dias_restantes = (fecha_v - hoy).days

        if 0 <= dias_restantes <= 5:
            resultados.append((nombre, dias_restantes))

    conexion.close()

    return resultados

def ver_suscripciones_completas():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT suscripciones.id,
           clientes.nombre,
           membresias.nombre_plan,
           suscripciones.fecha_inicio,
           suscripciones.fecha_vencimiento,
           suscripciones.pagado,
           suscripciones.pendiente
    FROM suscripciones
    JOIN clientes ON suscripciones.cliente_id = clientes.id
    JOIN membresias ON suscripciones.membresia_id = membresias.id
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos