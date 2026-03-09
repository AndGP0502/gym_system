import sqlite3
from tkinter import messagebox

def agregar_cliente(nombre, telefono, fecha_registro):

    if not nombre.strip():
        return "El nombre del cliente es obligatorio"

    if not telefono.strip():
        return "El teléfono es obligatorio"

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # evitar duplicados
    cursor.execute(
        "SELECT id FROM clientes WHERE nombre = ? AND telefono = ?",
        (nombre, telefono)
    )

    if cursor.fetchone():
        conexion.close()
        return "Este cliente ya está registrado"

    cursor.execute(
        "INSERT INTO clientes(nombre, telefono, fecha_registro) VALUES (?, ?, ?)",
        (nombre, telefono, fecha_registro)
    )

    conexion.commit()
    conexion.close()

    return "Cliente agregado correctamente"


def ver_clientes():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre, telefono, fecha_registro FROM clientes ORDER BY id")

    clientes = cursor.fetchall()

    conexion.close()

    return clientes

def eliminar_cliente(cliente_id):
    
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()
    
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    
    conexion.commit()
    conexion.close()

def editar_cliente(cliente_id, nombre, telefono, fecha):

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE clientes
        SET nombre = ?, telefono = ?, fecha_registro = ?
        WHERE id = ?
        """,
        (nombre, telefono, fecha, cliente_id)
    )

    conexion.commit()
    conexion.close()