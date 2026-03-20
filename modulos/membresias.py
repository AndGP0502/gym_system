import sqlite3
import os

from modulos.rutas import get_db_path
DB_PATH = get_db_path()


def _con():
    return sqlite3.connect(DB_PATH)


def crear_membresia(nombre_plan, precio, duracion_dias):
    if nombre_plan.strip() == "":
        print("El nombre del plan no puede estar vacío")
        return
    if precio <= 0:
        print("El precio debe ser mayor a 0")
        return
    if duracion_dias <= 0:
        print("La duración debe ser mayor a 0")
        return

    con = _con()
    cur = con.cursor()
    cur.execute("SELECT id FROM membresias WHERE nombre_plan = ?", (nombre_plan,))
    if cur.fetchone():
        print("Ya existe una membresía con ese nombre")
        con.close()
        return
    cur.execute(
        "INSERT INTO membresias(nombre_plan, precio, duracion_dias) VALUES (?, ?, ?)",
        (nombre_plan, precio, duracion_dias)
    )
    con.commit()
    con.close()
    print("Membresía creada correctamente")


def editar_membresia(id_membresia, nombre_plan, precio, duracion_dias):
    if nombre_plan.strip() == "":
        print("El nombre del plan no puede estar vacío")
        return
    if precio <= 0:
        print("El precio debe ser mayor a 0")
        return
    if duracion_dias <= 0:
        print("La duración debe ser mayor a 0")
        return

    con = _con()
    con.execute("""
        UPDATE membresias
        SET nombre_plan = ?, precio = ?, duracion_dias = ?
        WHERE id = ?
    """, (nombre_plan, precio, duracion_dias, id_membresia))
    con.commit()
    con.close()
    print("Membresía actualizada correctamente")


def ver_membresias():
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT id, nombre_plan, precio, duracion_dias FROM membresias")
    membresias = cur.fetchall()
    con.close()
    return membresias


def eliminar_membresia(id_membresia):
    con = _con()
    con.execute("DELETE FROM membresias WHERE id = ?", (id_membresia,))
    con.commit()
    con.close()
    print("Membresía eliminada correctamente")


def contar_membresias():
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM membresias")
    total = cur.fetchone()[0]
    con.close()
    return total