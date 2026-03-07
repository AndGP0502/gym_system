import sqlite3


#funcion para crear una membresia
def crear_membresia(nombre_plan, precio, duracion_dias):
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO membresias(nombre_plan, precio, duracion_dias) VALUES (?, ?, ?)",
        (nombre_plan, precio, duracion_dias)
    )

    conexion.commit()
    conexion.close()

    print("Membresía creada correctamente")

#funcion para ver las membresias
def ver_membresias():
    conexion = sqlite3.connect("gym.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM membresias")

    membresias = cursor.fetchall()

    conexion.close()

    return membresias