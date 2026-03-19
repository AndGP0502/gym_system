import sqlite3
from datetime import datetime, timedelta
import os

from database.db_path import DB_PATH


def _con():
    """Devuelve siempre una conexión a la BD correcta."""
    return sqlite3.connect(DB_PATH)


def _nuevo_id_suscripcion(cur):
    """Devuelve el ID más bajo disponible en suscripciones."""
    cur.execute("SELECT id FROM suscripciones ORDER BY id")
    ids = set(r[0] for r in cur.fetchall())
    nuevo = 1
    while nuevo in ids:
        nuevo += 1
    return nuevo


# -------- ASIGNAR MEMBRESIA A CLIENTE --------
def asignar_membresia(cliente_id, membresia_id, precio_total, pagado, fecha_inicio=None):
    """
    Asigna una membresía a un cliente.
    fecha_inicio puede ser:
      - None  → se usa datetime.now() automáticamente
      - str   → fecha en formato YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY
    """
    con = _con()
    cur = con.cursor()

    cur.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,))
    if cur.fetchone() is None:
        con.close()
        print("El cliente no existe")
        return

    cur.execute("SELECT id, duracion_dias FROM membresias WHERE id = ?", (membresia_id,))
    resultado = cur.fetchone()
    if resultado is None:
        con.close()
        print("La membresía no existe")
        return

    duracion = resultado[1]

    if fecha_inicio is None:
        fecha_inicio_dt = datetime.now()
    else:
        fecha_inicio_dt = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio.strip(), fmt)
                break
            except ValueError:
                continue
        if fecha_inicio_dt is None:
            con.close()
            print(f"Formato de fecha invalido: '{fecha_inicio}'. Use YYYY-MM-DD o DD/MM/YYYY")
            return

    fecha_inicio_str  = fecha_inicio_dt.strftime("%Y-%m-%d")
    fecha_vencimiento = (fecha_inicio_dt + timedelta(days=duracion)).strftime("%Y-%m-%d")
    pendiente         = max(0, precio_total - pagado)
    nuevo_id          = _nuevo_id_suscripcion(cur)

    cur.execute("""
        INSERT INTO suscripciones(
            id, cliente_id, membresia_id, fecha_inicio, fecha_vencimiento,
            precio_total, pagado, pendiente
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nuevo_id, cliente_id, membresia_id, fecha_inicio_str, fecha_vencimiento,
          precio_total, pagado, pendiente))

    con.commit()
    con.close()
    print("Membresía asignada correctamente")


# -------- VER SUSCRIPCIONES --------
def ver_suscripciones():
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT * FROM suscripciones")
    datos = cur.fetchall()
    con.close()
    return datos


# -------- ESTADO GENERAL DEL GIMNASIO --------
def ver_estado_gimnasio():
    con = _con()
    cur = con.cursor()
    cur.execute("""
        SELECT suscripciones.id,
               clientes.nombre,
               membresias.nombre_plan,
               suscripciones.fecha_vencimiento,
               suscripciones.pagado,
               suscripciones.pendiente
        FROM suscripciones
        JOIN clientes   ON suscripciones.cliente_id   = clientes.id
        JOIN membresias ON suscripciones.membresia_id = membresias.id
    """)
    datos = cur.fetchall()
    con.close()
    return datos


# -------- CLIENTES VENCIDOS --------
def ver_clientes_vencidos():
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT clientes.nombre, suscripciones.fecha_vencimiento
        FROM suscripciones
        JOIN clientes ON suscripciones.cliente_id = clientes.id
        WHERE suscripciones.fecha_vencimiento < ?
    """, (hoy,))
    datos = cur.fetchall()
    con.close()
    return datos


# -------- REGISTRAR PAGO --------
def registrar_pago(suscripcion_id, monto):
    con = _con()
    cur = con.cursor()

    cur.execute("SELECT precio_total, pagado FROM suscripciones WHERE id = ?", (suscripcion_id,))
    datos = cur.fetchone()

    if datos is None:
        con.close()
        print("La suscripción no existe")
        return

    if monto <= 0:
        con.close()
        print("Monto inválido")
        return

    precio_total, pagado_actual = datos
    nuevo_pagado = min(pagado_actual + monto, precio_total)
    pendiente    = precio_total - nuevo_pagado

    cur.execute("""
        UPDATE suscripciones SET pagado = ?, pendiente = ? WHERE id = ?
    """, (nuevo_pagado, pendiente, suscripcion_id))

    con.commit()
    con.close()
    print("Pago registrado correctamente")


# -------- DIAS RESTANTES --------
def ver_dias_restantes():
    con = _con()
    cur = con.cursor()
    cur.execute("""
        SELECT clientes.nombre, membresias.nombre_plan, suscripciones.fecha_vencimiento
        FROM suscripciones
        JOIN clientes   ON suscripciones.cliente_id   = clientes.id
        JOIN membresias ON suscripciones.membresia_id = membresias.id
    """)
    datos = cur.fetchall()
    con.close()

    hoy = datetime.now()
    resultados = []
    for nombre, plan, fecha_vencimiento in datos:
        fecha_v        = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        dias_restantes = (fecha_v - hoy).days
        estado         = "VENCIDO" if dias_restantes < 0 else f"{dias_restantes} dias"
        resultados.append((nombre, plan, estado))
    return resultados


# -------- CLIENTES POR VENCER --------
def clientes_por_vencer():
    con = _con()
    cur = con.cursor()
    hoy = datetime.now()
    cur.execute("""
        SELECT clientes.nombre, suscripciones.fecha_vencimiento
        FROM suscripciones
        JOIN clientes ON suscripciones.cliente_id = clientes.id
    """)
    datos = cur.fetchall()
    con.close()

    resultados = []
    for nombre, fecha_vencimiento in datos:
        fecha_v        = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        dias_restantes = (fecha_v - hoy).days
        if 0 <= dias_restantes <= 5:
            resultados.append((nombre, dias_restantes))
    return resultados


# -------- VER SUSCRIPCIONES COMPLETAS --------
def ver_suscripciones_completas():
    con = _con()
    cur = con.cursor()
    cur.execute("""
        SELECT suscripciones.id,
               clientes.nombre,
               membresias.nombre_plan,
               suscripciones.fecha_inicio,
               suscripciones.fecha_vencimiento,
               suscripciones.pagado,
               suscripciones.pendiente
        FROM suscripciones
        JOIN clientes   ON suscripciones.cliente_id   = clientes.id
        JOIN membresias ON suscripciones.membresia_id = membresias.id
        ORDER BY suscripciones.id
    """)
    datos = cur.fetchall()
    con.close()
    return datos


# -------- CONTAR SUSCRIPCIONES VENCIDAS --------
def contar_suscripciones_vencidas():
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM suscripciones WHERE fecha_vencimiento < ?", (hoy,))
    total = cur.fetchone()[0]
    con.close()
    return total


# -------- CREAR SUSCRIPCION --------
def crear_suscripcion(cliente_id, membresia_id):
    con = _con()
    cur = con.cursor()

    cur.execute("SELECT precio, duracion_dias FROM membresias WHERE id = ?", (membresia_id,))
    datos = cur.fetchone()

    if not datos:
        con.close()
        print("La membresía no existe")
        return

    precio, duracion  = datos
    fecha_inicio      = datetime.now().date()
    fecha_vencimiento = fecha_inicio + timedelta(days=duracion)
    nuevo_id          = _nuevo_id_suscripcion(cur)

    cur.execute("""
        INSERT INTO suscripciones (
            id, cliente_id, membresia_id, fecha_inicio, fecha_vencimiento,
            precio_total, pagado, pendiente
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nuevo_id, cliente_id, membresia_id, fecha_inicio, fecha_vencimiento, precio, 0, precio))

    con.commit()
    con.close()
    print("Suscripción creada correctamente")


# -------- ELIMINAR SUSCRIPCION --------
def eliminar_suscripcion(suscripcion_id):
    con = _con()
    con.execute("DELETE FROM pagos WHERE suscripcion_id = ?", (suscripcion_id,))
    con.execute("DELETE FROM suscripciones WHERE id = ?", (suscripcion_id,))
    con.commit()
    con.close()


# -------- CONTAR CLIENTES ACTIVOS --------
def contar_clientes_activos():
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM suscripciones WHERE fecha_vencimiento >= ?", (hoy,))
    total = cur.fetchone()[0]
    con.close()
    return total


# -------- INGRESOS POR MES --------
def ingresos_por_mes():
    con = _con()
    cur = con.cursor()
    anio_actual = datetime.now().strftime("%Y")
    cur.execute("""
        SELECT strftime('%m', fecha_inicio) AS mes,
               COALESCE(SUM(pagado), 0)    AS total
        FROM suscripciones
        WHERE strftime('%Y', fecha_inicio) = ?
        GROUP BY strftime('%m', fecha_inicio)
        ORDER BY strftime('%m', fecha_inicio)
    """, (anio_actual,))
    datos = cur.fetchall()
    con.close()
    return datos


# -------- CLIENTES ACTIVOS CON DETALLE --------
def ver_clientes_activos_detalle():
    """
    Retorna todas las suscripciones activas (fecha_vencimiento >= hoy)
    con detalle completo para la ventana de clientes activos.
    """
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT suscripciones.id,
               clientes.nombre,
               membresias.nombre_plan,
               suscripciones.fecha_inicio,
               suscripciones.fecha_vencimiento,
               suscripciones.pagado,
               suscripciones.pendiente
        FROM suscripciones
        JOIN clientes   ON suscripciones.cliente_id   = clientes.id
        JOIN membresias ON suscripciones.membresia_id = membresias.id
        WHERE suscripciones.fecha_vencimiento >= ?
        ORDER BY suscripciones.fecha_vencimiento ASC
    """, (hoy,))
    datos = cur.fetchall()
    con.close()
    return datos


# -------- CONTAR SUSCRIPCIONES VENCIDAS POR MES/AÑO --------
def contar_suscripciones_vencidas_filtro(mes=None, anio=None):
    """Cuenta suscripciones vencidas filtrando por mes y/o año de vencimiento."""
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")

    query = "SELECT COUNT(*) FROM suscripciones WHERE fecha_vencimiento < ?"
    params = [hoy]

    if anio:
        query += " AND strftime('%Y', fecha_vencimiento) = ?"
        params.append(str(anio))
    if mes:
        query += " AND strftime('%m', fecha_vencimiento) = ?"
        params.append(f"{mes:02d}")

    total = cur.execute(query, params).fetchone()[0]
    con.close()
    return total


# -------- CONTAR CLIENTES ACTIVOS POR MES/AÑO --------
def contar_clientes_activos_filtro(mes=None, anio=None):
    """Cuenta suscripciones activas (no vencidas) filtrando por mes y/o año de inicio."""
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")

    query = "SELECT COUNT(*) FROM suscripciones WHERE fecha_vencimiento >= ?"
    params = [hoy]

    if anio:
        query += " AND strftime('%Y', fecha_inicio) = ?"
        params.append(str(anio))
    if mes:
        query += " AND strftime('%m', fecha_inicio) = ?"
        params.append(f"{mes:02d}")

    total = cur.execute(query, params).fetchone()[0]
    con.close()
    return total


# -------- RENOVAR SUSCRIPCION DE UN CLIENTE (+30 dias) --------
def renovar_suscripcion_cliente(cliente_id: int, dias: int = 30, monto: float = 0.0) -> str:
    """
    Extiende la fecha_vencimiento de la suscripcion mas reciente del cliente.
    Si monto > 0, registra el pago en la tabla pagos y actualiza pagado/pendiente.
    Devuelve: 'ok' | 'sin_suscripcion' | 'fecha_invalida'
    """
    con = _con()
    cur = con.cursor()

    cur.execute("""
        SELECT id, fecha_vencimiento, precio_total, pagado
        FROM suscripciones
        WHERE cliente_id = ?
        ORDER BY fecha_vencimiento DESC
        LIMIT 1
    """, (cliente_id,))

    fila = cur.fetchone()
    if fila is None:
        con.close()
        return "sin_suscripcion"

    sus_id, fecha_venc_str, precio_total, pagado_actual = fila
    precio_total  = float(precio_total)
    pagado_actual = float(pagado_actual)

    fecha_venc = None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            fecha_venc = datetime.strptime(fecha_venc_str, fmt)
            break
        except ValueError:
            continue

    if fecha_venc is None:
        con.close()
        return "fecha_invalida"

    nueva_fecha = (fecha_venc + timedelta(days=dias)).strftime("%Y-%m-%d")
    cur.execute("UPDATE suscripciones SET fecha_vencimiento = ? WHERE id = ?",
                (nueva_fecha, sus_id))

    # Registrar pago si monto > 0
    # En una renovacion, el precio_total se ACUMULA (nuevo periodo)
    if monto > 0:
        nuevo_precio    = precio_total + monto   # acumula el nuevo periodo
        nuevo_pagado    = pagado_actual + monto   # acumula lo pagado
        nuevo_pendiente = max(0.0, nuevo_precio - nuevo_pagado)
        cur.execute(
            "UPDATE suscripciones SET pagado=?, pendiente=?, precio_total=? WHERE id=?",
            (nuevo_pagado, nuevo_pendiente, nuevo_precio, sus_id)
        )
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO pagos (suscripcion_id, monto, fecha_pago) VALUES (?,?,?)",
            (sus_id, monto, fecha_hoy)
        )

    con.commit()
    con.close()
    return "ok"