from datetime import datetime, timedelta
import urllib.parse
import webbrowser
import sqlite3
import threading
import time
import os
 
# ── Ruta absoluta a la BD ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "gym.db")
 
# ── Ruta de Chrome ───────────────────────────────────────────────────────────
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
 
 
def _init_tabla_alertas():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS alertas_enviadas (
            id_cliente   INTEGER,
            fecha_alerta TEXT,
            PRIMARY KEY (id_cliente, fecha_alerta)
        )
    """)
    con.commit()
    con.close()
 
_init_tabla_alertas()
 
 
def _ya_alertado_hoy(id_cliente: int) -> bool:
    hoy = datetime.now().strftime("%Y-%m-%d")
    con = sqlite3.connect(DB_PATH)
    cur = con.execute(
        "SELECT 1 FROM alertas_enviadas WHERE id_cliente=? AND fecha_alerta=?",
        (id_cliente, hoy)
    )
    existe = cur.fetchone() is not None
    con.close()
    return existe
 
 
def _marcar_alertado(id_cliente: int):
    hoy = datetime.now().strftime("%Y-%m-%d")
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT OR IGNORE INTO alertas_enviadas (id_cliente, fecha_alerta) VALUES (?,?)",
        (id_cliente, hoy)
    )
    con.commit()
    con.close()
 
 
def formatear_telefono_url(numero: str) -> str:
    numero = str(numero).strip().replace(" ", "").replace("-", "").lstrip("+")
    if numero.startswith("593"):
        return numero
    if numero.startswith("0"):
        return "593" + numero[1:]
    return "593" + numero
 
 
def _abrir_en_chrome(url: str) -> bool:
    try:
        navegador = webbrowser.get(CHROME_PATH)
        navegador.open(url)
        return True
    except webbrowser.Error:
        print("[alertas] Chrome no encontrado, usando navegador predeterminado.")
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"[alertas] Error abriendo navegador: {e}")
            return False
 
 
def _abrir_whatsapp_web(telefono: str, mensaje: str) -> bool:
    tel_url = formatear_telefono_url(telefono)
    texto_codificado = urllib.parse.quote(mensaje)
    url = f"https://web.whatsapp.com/send?phone={tel_url}&text={texto_codificado}"
    return _abrir_en_chrome(url)
 
 
def enviar_whatsapp(nombre: str, telefono: str, dias_restantes: int, id_cliente: int):
    if dias_restantes == 0:
        aviso = "tu suscripcion *vence HOY*!"
    elif dias_restantes == 1:
        aviso = "tu suscripcion vence *manana*."
    else:
        aviso = f"tu suscripcion vence en *{dias_restantes} dias*."
 
    mensaje = (
        f"Hola {nombre}\n\n"
        f"Te informamos que {aviso}\n\n"
        f"Renovela para seguir entrenando\n\n"
        f"Te esperamos!"
    )
 
    exito = _abrir_whatsapp_web(telefono, mensaje)
 
    if exito:
        _marcar_alertado(id_cliente)
        print(f"[alertas] WhatsApp abierto para {nombre} ({dias_restantes} dias restantes)")
        time.sleep(3)
    else:
        print(f"[alertas] No se pudo abrir WhatsApp para {nombre}")
 
 
def enviar_whatsapp_thread(nombre: str, telefono: str, dias_restantes: int, id_cliente: int):
    threading.Thread(
        target=enviar_whatsapp,
        args=(nombre, telefono, dias_restantes, id_cliente),
        daemon=True
    ).start()
 
 
def enviar_recordatorio_manual(nombre: str, telefono: str):
    mensaje = (
        f"Hola {nombre}\n\n"
        f"Te recordamos que es momento de renovar tu suscripcion al gimnasio.\n\n"
        f"Te esperamos para seguir entrenando!"
    )
    _abrir_whatsapp_web(telefono, mensaje)
 
 
def verificar_vencimientos():
    from modulos.clientes import ver_clientes
 
    clientes = ver_clientes()
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
 
    for cliente in clientes:
        id_cliente     = cliente[0]
        nombre         = cliente[1]
        telefono       = cliente[3]
        fecha_registro = cliente[4]
 
        fecha_dt = None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                fecha_dt = datetime.strptime(fecha_registro, fmt)
                break
            except ValueError:
                continue
 
        if fecha_dt is None:
            print(f"[alertas] Formato de fecha desconocido para '{nombre}': {fecha_registro!r}")
            continue
 
        fecha_vencimiento = fecha_dt + timedelta(days=30)
        dias_restantes    = (fecha_vencimiento - hoy).days
 
        if 0 <= dias_restantes <= 5:
            if not _ya_alertado_hoy(id_cliente):
                print(f"[alertas] Enviando aviso a {nombre} ({dias_restantes} dias restantes)")
                enviar_whatsapp_thread(nombre, telefono, dias_restantes, id_cliente)
            else:
                print(f"[alertas] {nombre} ya fue alertado hoy, se omite.")
        elif dias_restantes < 0:
            print(f"[alertas] Cliente vencido hace {abs(dias_restantes)} dias: {nombre}")