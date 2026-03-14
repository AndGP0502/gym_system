import sqlite3
import os
import shutil
from datetime import datetime

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DB_PATH       = os.path.join(BASE_DIR, "..", "gym.db")
FOTOS_DIR     = os.path.join(BASE_DIR, "..", "assets", "fotos_clientes")


def _con():
    return sqlite3.connect(DB_PATH)


def init_tablas_ficha():
    os.makedirs(FOTOS_DIR, exist_ok=True)

    con = _con()
    con.execute("""
        CREATE TABLE IF NOT EXISTS ficha_cliente (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id      INTEGER UNIQUE,
            objetivo        TEXT,
            estado_fisico   TEXT,
            condiciones     TEXT,
            notas           TEXT,
            foto_ruta       TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS historial_medidas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id  INTEGER,
            fecha       TEXT,
            peso_kg     REAL,
            altura_cm   REAL,
            imc         REAL,
            notas       TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)
    con.commit()
    con.close()

init_tablas_ficha()


# ── Foto ──────────────────────────────────────────────────────────────────────

def guardar_foto(cliente_id: int, ruta_origen: str) -> str:
    """
    Copia la foto al directorio de fotos del proyecto.
    Devuelve la ruta relativa guardada.
    """
    os.makedirs(FOTOS_DIR, exist_ok=True)
    extension  = os.path.splitext(ruta_origen)[1].lower()
    nombre     = f"cliente_{cliente_id}{extension}"
    ruta_destino = os.path.join(FOTOS_DIR, nombre)
    shutil.copy2(ruta_origen, ruta_destino)
    return ruta_destino


def obtener_foto(cliente_id: int) -> str | None:
    """Devuelve la ruta de la foto del cliente o None si no tiene."""
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT foto_ruta FROM ficha_cliente WHERE cliente_id = ?", (cliente_id,))
    fila = cur.fetchone()
    con.close()
    if fila and fila[0] and os.path.exists(fila[0]):
        return fila[0]
    return None


# ── Ficha general ─────────────────────────────────────────────────────────────

def obtener_ficha(cliente_id: int) -> dict | None:
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT * FROM ficha_cliente WHERE cliente_id = ?", (cliente_id,))
    fila = cur.fetchone()
    con.close()
    if fila is None:
        return None
    return {
        "id": fila[0], "cliente_id": fila[1], "objetivo": fila[2],
        "estado_fisico": fila[3], "condiciones": fila[4],
        "notas": fila[5], "foto_ruta": fila[6]
    }


def guardar_ficha(cliente_id: int, objetivo: str, estado_fisico: str,
                  condiciones: str, notas: str, foto_ruta: str = None):
    con = _con()

    ficha_actual = obtener_ficha(cliente_id)
    ruta_final   = foto_ruta if foto_ruta else (ficha_actual["foto_ruta"] if ficha_actual else None)

    con.execute("""
        INSERT INTO ficha_cliente (cliente_id, objetivo, estado_fisico, condiciones, notas, foto_ruta)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(cliente_id) DO UPDATE SET
            objetivo      = excluded.objetivo,
            estado_fisico = excluded.estado_fisico,
            condiciones   = excluded.condiciones,
            notas         = excluded.notas,
            foto_ruta     = excluded.foto_ruta
    """, (cliente_id, objetivo, estado_fisico, condiciones, notas, ruta_final))
    con.commit()
    con.close()


# ── Historial de medidas ──────────────────────────────────────────────────────

def agregar_medida(cliente_id: int, peso_kg: float, altura_cm: float, notas: str = "") -> float:
    imc   = round(peso_kg / ((altura_cm / 100) ** 2), 2) if altura_cm > 0 else 0
    fecha = datetime.now().strftime("%d/%m/%Y")
    con   = _con()
    con.execute("""
        INSERT INTO historial_medidas (cliente_id, fecha, peso_kg, altura_cm, imc, notas)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cliente_id, fecha, peso_kg, altura_cm, imc, notas))
    con.commit()
    con.close()
    return imc


def obtener_historial(cliente_id: int) -> list:
    con = _con()
    cur = con.cursor()
    cur.execute("""
        SELECT id, fecha, peso_kg, altura_cm, imc, notas
        FROM historial_medidas
        WHERE cliente_id = ?
        ORDER BY id DESC
    """, (cliente_id,))
    datos = cur.fetchall()
    con.close()
    return datos


def eliminar_medida(medida_id: int):
    con = _con()
    con.execute("DELETE FROM historial_medidas WHERE id = ?", (medida_id,))
    con.commit()
    con.close()
