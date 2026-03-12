import sqlite3
from tkinter import messagebox


# -------- ASEGURAR QUE EXISTA LA COLUMNA CEDULA --------
def asegurar_columna_cedula():
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN cedula TEXT")
        conexion.commit()
    except sqlite3.OperationalError:
        pass

    conexion.close()


# se ejecuta al cargar este módulo
asegurar_columna_cedula()


def agregar_cliente(nombre, cedula, telefono, fecha_registro):

    if not nombre.strip():
        return "El nombre del cliente es obligatorio"

    if not cedula.strip():
        return "La cédula es obligatoria"

    if not telefono.strip():
        return "El teléfono es obligatorio"

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # evitar duplicados
    cursor.execute(
        "SELECT id FROM clientes WHERE cedula = ?",
        (cedula,)
    )

    if cursor.fetchone():
        conexion.close()
        return "Ya existe un cliente registrado con esa cédula"

    cursor.execute(
        "INSERT INTO clientes(nombre, cedula, telefono, fecha_registro) VALUES (?, ?, ?, ?)",
        (nombre, cedula, telefono, fecha_registro)
    )

    conexion.commit()
    conexion.close()

    return "Cliente agregado correctamente"


def ver_clientes():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre, cedula, telefono, fecha_registro FROM clientes ORDER BY id")

    clientes = cursor.fetchall()

    conexion.close()

    return clientes


def eliminar_cliente(cliente_id):
    
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()
    
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    
    conexion.commit()
    conexion.close()


def editar_cliente(cliente_id, nombre, cedula, telefono, fecha):

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # validar duplicado de cédula en otro cliente
    cursor.execute(
        "SELECT id FROM clientes WHERE cedula = ? AND id != ?",
        (cedula, cliente_id)
    )

    if cursor.fetchone():
        conexion.close()
        return "Ya existe otro cliente con esa cédula"

    cursor.execute(
        """
        UPDATE clientes
        SET nombre = ?, cedula = ?, telefono = ?, fecha_registro = ?
        WHERE id = ?
        """,
        (nombre, cedula, telefono, fecha, cliente_id)
    )

    conexion.commit()
    conexion.close()

    return "Cliente actualizado correctamente"


# -------- CONTAR CLIENTES PARA EL DASHBOARD --------
def contar_clientes():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM clientes")

    total = cursor.fetchone()[0]

    conexion.close()

    return total