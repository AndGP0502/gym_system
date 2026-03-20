import sqlite3
import os
import sys

from database.db_path import get_db_path

def inicializar_base_datos():
    """
    Crea las tablas si no existen. Se llama explícitamente desde main.py,
    no al importar el módulo — evita el error 'unable to open database file'
    en la PC del cliente.
    """
    conexion = sqlite3.connect(get_db_path())
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes(
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT,
            cedula         TEXT,
            telefono       TEXT,
            fecha_registro TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membresias(
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_plan   TEXT,
            precio        REAL,
            duracion_dias INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suscripciones(
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id        INTEGER,
            membresia_id      INTEGER,
            fecha_inicio      TEXT,
            fecha_vencimiento TEXT,
            precio_total      REAL,
            pagado            REAL,
            pendiente         REAL,
            FOREIGN KEY(cliente_id)   REFERENCES clientes(id),
            FOREIGN KEY(membresia_id) REFERENCES membresias(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos(
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            suscripcion_id INTEGER,
            monto          REAL,
            fecha_pago     TEXT,
            FOREIGN KEY(suscripcion_id) REFERENCES suscripciones(id)
        )
    """)

    conexion.commit()
    conexion.close()
    print("Base de datos lista")