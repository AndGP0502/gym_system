import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "gym.db")

conexion = sqlite3.connect(DB_PATH)


# FUNCION PARA CREAR UNA MEMBRESIA
def crear_membresia(nombre_plan, precio, duracion_dias):

    # validar nombre
    if nombre_plan.strip() == "":
        print("El nombre del plan no puede estar vacío")
        return

    # validar precio
    if precio <= 0:
        print("El precio debe ser mayor a 0")
        return

    # validar duración
    if duracion_dias <= 0:
        print("La duración debe ser mayor a 0")
        return

    # conectar a la base de datos
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # verificar si ya existe una membresía con ese nombre
    cursor.execute("SELECT id FROM membresias WHERE nombre_plan = ?", (nombre_plan,))
    if cursor.fetchone():
        print("Ya existe una membresía con ese nombre")
        conexion.close()
        return

    # insertar nueva membresía
    cursor.execute(
        "INSERT INTO membresias(nombre_plan, precio, duracion_dias) VALUES (?, ?, ?)",
        (nombre_plan, precio, duracion_dias)
    )

    # guardar cambios
    conexion.commit()

    # cerrar conexión
    conexion.close()

    print("Membresía creada correctamente")


# FUNCION PARA EDITAR UNA MEMBRESIA
def editar_membresia(id_membresia, nombre_plan, precio, duracion_dias):

    # validar nombre
    if nombre_plan.strip() == "":
        print("El nombre del plan no puede estar vacío")
        return

    # validar precio
    if precio <= 0:
        print("El precio debe ser mayor a 0")
        return

    # validar duración
    if duracion_dias <= 0:
        print("La duración debe ser mayor a 0")
        return

    # conectar a la base de datos
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # actualizar datos de la membresía
    cursor.execute("""
        UPDATE membresias
        SET nombre_plan = ?, precio = ?, duracion_dias = ?
        WHERE id = ?
    """, (nombre_plan, precio, duracion_dias, id_membresia))

    # guardar cambios
    conexion.commit()

    # cerrar conexión
    conexion.close()

    print("Membresía actualizada correctamente")


# FUNCION PARA VER LAS MEMBRESIAS
def ver_membresias():

    # conectar a la base de datos
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # consultar membresías
    cursor.execute("SELECT id, nombre_plan, precio, duracion_dias FROM membresias")

    membresias = cursor.fetchall()

    # cerrar conexión
    conexion.close()

    return membresias


# FUNCION PARA ELIMINAR UNA MEMBRESIA POR ID
def eliminar_membresia(id_membresia):

    # conectar a la base de datos
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # eliminar membresía
    cursor.execute("DELETE FROM membresias WHERE id = ?", (id_membresia,))

    # guardar cambios
    conexion.commit()

    # cerrar conexión
    conexion.close()

    print("Membresía eliminada correctamente")


# -------- CONTAR MEMBRESIAS --------
def contar_membresias():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM membresias")

    total = cursor.fetchone()[0]

    conexion.close()

    return total