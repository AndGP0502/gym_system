import sqlite3
import os
import shutil
from datetime import datetime

from modulos.rutas import get_db_path, get_assets_dir
DB_PATH   = get_db_path()
FOTOS_DIR = os.path.join(get_assets_dir(), "fotos_clientes")


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
    for col, tipo in [
        ("peso_kg",        "REAL"),
        ("altura_m",       "REAL"),
        ("cir_abdominal",  "REAL"),
        ("status_fisico",  "TEXT"),
        ("objetivo_2",     "TEXT"),
        ("peso_ideal",     "REAL"),
        ("lesion",         "TEXT"),
        ("cardiovascular", "TEXT"),
        ("asfixia",        "TEXT"),
        ("asmatico",       "TEXT"),
        ("medicacion",     "TEXT"),
        ("mareos",         "TEXT"),
    ]:
        try:
            con.execute(f"ALTER TABLE ficha_cliente ADD COLUMN {col} {tipo}")
        except sqlite3.OperationalError:
            pass
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


def guardar_foto(cliente_id: int, ruta_origen: str) -> str:
    os.makedirs(FOTOS_DIR, exist_ok=True)
    ext          = os.path.splitext(ruta_origen)[1].lower()
    nombre       = f"cliente_{cliente_id}{ext}"
    ruta_destino = os.path.join(FOTOS_DIR, nombre)
    shutil.copy2(ruta_origen, ruta_destino)
    return ruta_destino


def obtener_foto(cliente_id: int) -> str | None:
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT foto_ruta FROM ficha_cliente WHERE cliente_id = ?", (cliente_id,))
    fila = cur.fetchone()
    con.close()
    if fila and fila[0] and os.path.exists(fila[0]):
        return fila[0]
    return None


def obtener_ficha(cliente_id: int) -> dict | None:
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT * FROM ficha_cliente WHERE cliente_id = ?", (cliente_id,))
    fila = cur.fetchone()
    con.close()
    if fila is None:
        return None
    cols = ["id","cliente_id","objetivo","estado_fisico","condiciones","notas","foto_ruta",
            "peso_kg","altura_m","cir_abdominal","status_fisico","objetivo_2","peso_ideal",
            "lesion","cardiovascular","asfixia","asmatico","medicacion","mareos"]
    return dict(zip(cols, fila + (None,) * (len(cols) - len(fila))))


def guardar_ficha(cliente_id: int, objetivo: str, estado_fisico: str,
                  condiciones: str, notas: str, foto_ruta: str = None,
                  peso_kg=None, altura_m=None, cir_abdominal=None,
                  status_fisico=None, objetivo_2=None, peso_ideal=None,
                  lesion=None, cardiovascular=None, asfixia=None,
                  asmatico=None, medicacion=None, mareos=None):
    con = _con()
    ficha_actual = obtener_ficha(cliente_id)
    ruta_final   = foto_ruta if foto_ruta else (ficha_actual["foto_ruta"] if ficha_actual else None)
    con.execute("""
        INSERT INTO ficha_cliente
            (cliente_id, objetivo, estado_fisico, condiciones, notas, foto_ruta,
             peso_kg, altura_m, cir_abdominal, status_fisico, objetivo_2, peso_ideal,
             lesion, cardiovascular, asfixia, asmatico, medicacion, mareos)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(cliente_id) DO UPDATE SET
            objetivo=excluded.objetivo, estado_fisico=excluded.estado_fisico,
            condiciones=excluded.condiciones, notas=excluded.notas,
            foto_ruta=excluded.foto_ruta, peso_kg=excluded.peso_kg,
            altura_m=excluded.altura_m, cir_abdominal=excluded.cir_abdominal,
            status_fisico=excluded.status_fisico, objetivo_2=excluded.objetivo_2,
            peso_ideal=excluded.peso_ideal, lesion=excluded.lesion,
            cardiovascular=excluded.cardiovascular, asfixia=excluded.asfixia,
            asmatico=excluded.asmatico, medicacion=excluded.medicacion,
            mareos=excluded.mareos
    """, (cliente_id, objetivo, estado_fisico, condiciones, notas, ruta_final,
          peso_kg, altura_m, cir_abdominal, status_fisico, objetivo_2, peso_ideal,
          lesion, cardiovascular, asfixia, asmatico, medicacion, mareos))
    con.commit()
    con.close()


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
        FROM historial_medidas WHERE cliente_id = ?
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