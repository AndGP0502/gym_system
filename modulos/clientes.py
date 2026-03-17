import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "gym.db")


def _con():
    """Devuelve siempre una conexión a la BD correcta."""
    return sqlite3.connect(DB_PATH)


# -------- ASEGURAR QUE EXISTA LA COLUMNA CEDULA --------
def asegurar_columna_cedula():
    con = _con()
    try:
        con.execute("ALTER TABLE clientes ADD COLUMN cedula TEXT")
        con.commit()
    except sqlite3.OperationalError:
        pass
    con.close()

asegurar_columna_cedula()


# -------- AGREGAR CLIENTE --------
def agregar_cliente(nombre, cedula, telefono, fecha_registro):
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

    cur.execute(
        "INSERT INTO clientes(nombre, cedula, telefono, fecha_registro) VALUES (?, ?, ?, ?)",
        (nombre, cedula, telefono, fecha_registro)
    )
    con.commit()
    con.close()
    return "Cliente agregado correctamente"


# -------- VER CLIENTES --------
def ver_clientes():
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT id, nombre, cedula, telefono, fecha_registro FROM clientes ORDER BY id")
    clientes = cur.fetchall()
    con.close()
    return clientes


# -------- ELIMINAR CLIENTE --------
def eliminar_cliente(cliente_id):
    con = _con()
    con.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    con.commit()
    con.close()


# -------- EDITAR CLIENTE --------
def editar_cliente(cliente_id, nombre, cedula, telefono, fecha):
    con = _con()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM clientes WHERE cedula = ? AND id != ?",
        (cedula, cliente_id)
    )
    if cur.fetchone():
        con.close()
        return "Ya existe otro cliente con esa cédula"

    cur.execute("""
        UPDATE clientes
        SET nombre = ?, cedula = ?, telefono = ?, fecha_registro = ?
        WHERE id = ?
    """, (nombre, cedula, telefono, fecha, cliente_id))

    con.commit()
    con.close()
    return "Cliente actualizado correctamente"

# -------- CONTAR CLIENTES POR MES/AÑO DE REGISTRO --------
def contar_clientes_filtro(mes=None, anio=None):
    """Cuenta clientes registrados filtrando por mes y/o año."""
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


# -------- CONTAR CLIENTES --------
def contar_clientes():
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM clientes")
    total = cur.fetchone()[0]
    con.close()
    return total