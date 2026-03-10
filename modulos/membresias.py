import sqlite3


# función para crear una membresía
def crear_membresia(nombre_plan, precio, duracion_dias):

    if precio <= 0:
        print("El precio debe ser mayor a 0")
        return

    if duracion_dias <= 0:
        print("La duración debe ser mayor a 0")
        return

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    # verificar si ya existe
    cursor.execute("SELECT id FROM membresias WHERE nombre_plan = ?", (nombre_plan,))
    if cursor.fetchone():
        print("Ya existe una membresía con ese nombre")
        conexion.close()
        return

    cursor.execute(
        "INSERT INTO membresias(nombre_plan, precio, duracion_dias) VALUES (?, ?, ?)",
        (nombre_plan, precio, duracion_dias)
    )

    conexion.commit()
    conexion.close()

    print("Membresía creada correctamente")


# función para ver las membresías
def ver_membresias():

    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre_plan, precio, duracion_dias FROM membresias")

    membresias = cursor.fetchall()

    conexion.close()

    return membresias


# función para eliminar una membresía por id
def eliminar_membresia(id_membresia):
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM membresias WHERE id = ?", (id_membresia,))

    conexion.commit()
    conexion.close()

    print("Membresía eliminada correctamente")