import sqlite3
import os
import sys

from modulos.rutas import get_db_path
DB_PATH = get_db_path()


def _con():
    return sqlite3.connect(DB_PATH)


def asegurar_columnas():
    con = _con()
    for col in ["cedula TEXT", "correo TEXT"]:
        try:
            con.execute(f"ALTER TABLE clientes ADD COLUMN {col}")
            con.commit()
        except sqlite3.OperationalError:
            pass
    con.close()

asegurar_columnas()


def agregar_cliente(nombre, cedula, telefono, fecha_registro, correo=""):
    if not nombre.strip():
        return "El nombre del cliente es obligatorio"
    if not cedula.strip():
        return "La cédula es obligatoria"
    if not telefono.strip():
        return "El teléfono es obligatorio"

    con = _con()
    cur = con.cursor()

    cur.execute("SELECT id FROM clientes WHERE cedula = ?", (cedula,))
    if cur.fetchone():
        con.close()
        return "Ya existe un cliente registrado con esa cédula"

    cur.execute("SELECT id FROM clientes ORDER BY id")
    ids_existentes = set(r[0] for r in cur.fetchall())
    nuevo_id = 1
    while nuevo_id in ids_existentes:
        nuevo_id += 1

    cur.execute(
        "INSERT INTO clientes(id, nombre, cedula, telefono, fecha_registro, correo) VALUES (?,?,?,?,?,?)",
        (nuevo_id, nombre, cedula, telefono, fecha_registro, correo)
    )
    con.commit()
    con.close()
    return "Cliente agregado correctamente"


def ver_clientes():
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT id, nombre, cedula, telefono, fecha_registro, COALESCE(correo,'') FROM clientes ORDER BY id")
    clientes = cur.fetchall()
    con.close()
    return clientes


def eliminar_cliente(cliente_id):
    con = _con()
    con.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    con.commit()
    con.close()


def editar_cliente(cliente_id, nombre, cedula, telefono, fecha, correo=""):
    con = _con()
    cur = con.cursor()
    cur.execute(
        "SELECT id FROM clientes WHERE cedula = ? AND id != ?",
        (cedula, cliente_id)
    )
    if cur.fetchone():
        con.close()
        return "Ya existe otro cliente con esa cédula"
    cur.execute(
        "UPDATE clientes SET nombre=?, cedula=?, telefono=?, fecha_registro=?, correo=? WHERE id=?",
        (nombre, cedula, telefono, fecha, correo, cliente_id)
    )
    con.commit()
    con.close()
    return "Cliente actualizado correctamente"


def contar_clientes():
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM clientes")
    total = cur.fetchone()[0]
    con.close()
    return total


def contar_clientes_filtro(mes=None, anio=None):
    con = _con()
    cur = con.cursor()
    query = "SELECT COUNT(*) FROM clientes WHERE 1=1"
    params = []
    if anio:
        query += " AND (strftime('%Y', fecha_registro) = ? OR fecha_registro LIKE ?)"
        params.append(str(anio))
        params.append(f"%/{anio}")
    if mes:
        query += " AND (strftime('%m', fecha_registro) = ? OR fecha_registro LIKE ?)"
        params.append(f"{mes:02d}")
        params.append(f"{mes:02d}/%")
    total = cur.execute(query, params).fetchone()[0]
    con.close()
    return total