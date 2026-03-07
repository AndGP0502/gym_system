import sqlite3

def agregar_cliente(nombre, telefono, fecha_registro):
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO clientes(nombre, telefono, fecha_registro) VALUES (?, ?, ?)",
        (nombre, telefono, fecha_registro)
    )

    conexion.commit()
    conexion.close()

    return("Cliente agregado correctamente")

def ver_clientes():
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM clientes ORDER BY id")

    clientes = cursor.fetchall()

    conexion.close()

    return clientes