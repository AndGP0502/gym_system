from datetime import datetime
import urllib.parse
import webbrowser
import sqlite3
import os

# ── Ruta absoluta a la BD ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "gym.db")

# ── Ruta de Chrome ───────────────────────────────────────────────────────────
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"


def formatear_telefono_url(numero: str) -> str:
    numero = str(numero).strip().replace(" ", "").replace("-", "").lstrip("+")
    if numero.startswith("593"):
        return numero
    if numero.startswith("0"):
        return "593" + numero[1:]
    return "593" + numero


def _abrir_en_chrome(url: str):
    try:
        webbrowser.get(CHROME_PATH).open(url)
    except webbrowser.Error:
        webbrowser.open(url)


def _abrir_whatsapp_web(telefono: str, mensaje: str):
    tel_url = formatear_telefono_url(telefono)
    url = f"https://web.whatsapp.com/send?phone={tel_url}&text={urllib.parse.quote(mensaje)}"
    _abrir_en_chrome(url)


def dias_restantes(id_cliente: int) -> int | None:
    """Devuelve los días restantes de la suscripción activa del cliente, o None si no tiene."""
    con = sqlite3.connect(DB_PATH)
    cur = con.execute("""
        SELECT fecha_vencimiento
        FROM suscripciones
        WHERE cliente_id = ?
        ORDER BY fecha_vencimiento DESC
        LIMIT 1
    """, (id_cliente,))
    fila = cur.fetchone()
    con.close()

    if not fila:
        return None

    try:
        vence = datetime.strptime(fila[0], "%Y-%m-%d")
        delta = (vence - datetime.now()).days
        return delta
    except Exception:
        return None


def enviar_recordatorio_manual(nombre: str, telefono: str, id_cliente: int):
    """
    Abre WhatsApp Web con un mensaje personalizado que incluye
    los días restantes de la suscripción del cliente.
    """
    dias = dias_restantes(id_cliente)

    if dias is None:
        estado_msg = "no encontramos una suscripcion activa a tu nombre"
    elif dias <= 0:
        estado_msg = f"tu suscripcion vencio hace {abs(dias)} dia(s)"
    elif dias == 1:
        estado_msg = "tu suscripcion vence MAÑANA"
    else:
        estado_msg = f"tu suscripcion vence en {dias} dia(s)"

    mensaje = (
        f"Hola {nombre} 👋\n\n"
        f"Te recordamos que {estado_msg}.\n\n"
        f"Renueva tu suscripcion para seguir entrenando con nosotros 💪\n\n"
        f"Te esperamos en FIVGYM!"
    )

    _abrir_whatsapp_web(telefono, mensaje)