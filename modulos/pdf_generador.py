import os
import sys
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from tkinter import filedialog, messagebox

# ── Rutas ─────────────────────────────────────────────────────────────────────

if getattr(sys, 'frozen', False):
    _RAIZ = os.path.dirname(sys.executable)
else:
    _RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.path.join(_RAIZ, "Config.JSON")


def _leer_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _ruta_assets_lectura(nombre_archivo):
    if getattr(sys, 'frozen', False):
        base_appdata = os.path.join(os.environ.get("APPDATA", ""), "GymSystem", "assets")
        if os.path.exists(os.path.join(base_appdata, nombre_archivo)):
            return os.path.join(base_appdata, nombre_archivo)
        return os.path.join(sys._MEIPASS, "assets", nombre_archivo)
    base = os.path.join(_RAIZ, "assets")
    return os.path.join(base, nombre_archivo)


# ── Estilos ───────────────────────────────────────────────────────────────────

def _estilos():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("GymTitulo",   parent=styles["Normal"],
               fontSize=20, fontName="Helvetica-Bold",
               textColor=colors.HexColor("#1a1a2e"), alignment=TA_LEFT))
    styles.add(ParagraphStyle("GymSubtitulo", parent=styles["Normal"],
               fontSize=11, fontName="Helvetica",
               textColor=colors.HexColor("#555555"), alignment=TA_LEFT))
    styles.add(ParagraphStyle("GymNombreGym", parent=styles["Normal"],
               fontSize=13, fontName="Helvetica-Bold",
               textColor=colors.HexColor("#1f6aa5"), alignment=TA_RIGHT))
    styles.add(ParagraphStyle("GymInfoGym",  parent=styles["Normal"],
               fontSize=9,  fontName="Helvetica",
               textColor=colors.HexColor("#666666"), alignment=TA_RIGHT))
    styles.add(ParagraphStyle("GymSeccion",  parent=styles["Normal"],
               fontSize=12, fontName="Helvetica-Bold",
               textColor=colors.HexColor("#1f6aa5"), alignment=TA_LEFT))
    styles.add(ParagraphStyle("GymCampo",    parent=styles["Normal"],
               fontSize=10, fontName="Helvetica",
               textColor=colors.HexColor("#333333"), alignment=TA_LEFT))
    styles.add(ParagraphStyle("GymPie",      parent=styles["Normal"],
               fontSize=8,  fontName="Helvetica",
               textColor=colors.HexColor("#999999"), alignment=TA_CENTER))
    return styles


def _header(elementos, styles, titulo, subtitulo):
    """Encabezado con logo a la izquierda e info del gym a la derecha."""
    config = _leer_config()
    nombre_gym = config.get("nombre_gimnasio", "Gimnasio")
    telefono   = config.get("telefono", "")
    direccion  = config.get("direccion", "")
    correo     = config.get("correo", "")

    ruta_logo = _ruta_assets_lectura("logo_gym.jpg")

    # Columna izquierda: logo + título
    col_izq = []
    if os.path.exists(ruta_logo):
        try:
            col_izq.append(RLImage(ruta_logo, width=2.5*cm, height=2.5*cm))
        except Exception:
            pass
    col_izq.append(Spacer(1, 4))
    col_izq.append(Paragraph(titulo,    styles["GymTitulo"]))
    col_izq.append(Paragraph(subtitulo, styles["GymSubtitulo"]))

    # Columna derecha: datos del gym
    col_der = [
        Paragraph(nombre_gym, styles["GymNombreGym"]),
    ]
    if telefono:
        col_der.append(Paragraph(f"📞 {telefono}", styles["GymInfoGym"]))
    if direccion:
        col_der.append(Paragraph(f"📍 {direccion}", styles["GymInfoGym"]))
    if correo:
        col_der.append(Paragraph(f"✉ {correo}",   styles["GymInfoGym"]))

    tabla_header = Table([[col_izq, col_der]], colWidths=[10*cm, 8*cm])
    tabla_header.setStyle(TableStyle([
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING",(0,0), (-1,-1), 0),
    ]))
    elementos.append(tabla_header)
    elementos.append(HRFlowable(width="100%", thickness=2,
                                color=colors.HexColor("#1f6aa5"), spaceAfter=10))


def _footer_text(styles):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    return Paragraph(f"Documento generado el {fecha} · Software de Control A&D",
                     styles["GymPie"])


# PDF 1 — FICHA DEL CLIENTE

def generar_pdf_ficha_cliente(parent, cliente_id, nombre_cliente):
    """
    Genera la ficha completa de un cliente:
    datos personales + historial de suscripciones y pagos.
    """
    from modulos.clientes import ver_clientes
    from modulos.pagos import buscar_cliente_pagos, ver_historial_pagos

    # Buscar datos del cliente
    cliente = next((c for c in ver_clientes() if c[0] == cliente_id), None)
    if not cliente:
        messagebox.showerror("Error", "No se encontró el cliente.", parent=parent)
        return

    # Elegir dónde guardar
    ruta = filedialog.asksaveasfilename(
        parent=parent,
        title="Guardar ficha del cliente",
        defaultextension=".pdf",
        initialfile=f"Ficha_{nombre_cliente.replace(' ', '_')}.pdf",
        filetypes=[("PDF", "*.pdf")]
    )
    if not ruta:
        return

    styles    = _estilos()
    elementos = []

    # Encabezado
    _header(elementos, styles, "Ficha del Cliente",
            f"Generado el {datetime.now().strftime('%d/%m/%Y')}")
    elementos.append(Spacer(1, 10))

    # Datos personales
    elementos.append(Paragraph("Datos Personales", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    datos_personales = [
        ["ID",             str(cliente[0])],
        ["Nombre",         str(cliente[1])],
        ["Cédula",         str(cliente[2])],
        ["Teléfono",       str(cliente[3])],
        ["Fecha registro", str(cliente[4])],
    ]
    t = Table(datos_personales, colWidths=[5*cm, 13*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (0,-1), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR",    (0,0), (0,-1), colors.white),
        ("FONTNAME",     (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",     (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(1,0),(1,-1),[colors.HexColor("#f0f4ff"), colors.white]),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 16))

    # Suscripciones
    suscripciones = buscar_cliente_pagos(cliente_id)
    elementos.append(Paragraph("Suscripciones", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    if suscripciones:
        encabezado = [["ID Sus.", "Plan", "Total", "Pagado", "Pendiente", "Inicio", "Vence"]]
        filas = []
        for s in suscripciones:
            filas.append([
                str(s[0]),
                str(s[2]),
                f"${float(s[3]):.2f}",
                f"${float(s[4]):.2f}",
                f"${float(s[5]):.2f}",
                str(s[6]),
                str(s[7]),
            ])
        tabla_sus = Table(encabezado + filas,
                          colWidths=[1.8*cm, 4.5*cm, 2.2*cm, 2.2*cm, 2.2*cm, 2.5*cm, 2.6*cm])
        tabla_sus.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#1f6aa5")),
            ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),
             [colors.HexColor("#f0f4ff"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("ALIGN",         (2,0), (-1,-1), "CENTER"),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("RIGHTPADDING",  (0,0), (-1,-1), 6),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        elementos.append(tabla_sus)
    else:
        elementos.append(Paragraph("Sin suscripciones registradas.", styles["GymCampo"]))

    elementos.append(Spacer(1, 16))

    # Historial de pagos
    elementos.append(Paragraph("Historial de Pagos", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    todos_pagos = []
    for s in suscripciones:
        pagos = ver_historial_pagos(s[0])
        for p in pagos:
            todos_pagos.append([str(p[0]), str(s[0]), f"${float(p[1]):.2f}", str(p[2])])

    if todos_pagos:
        enc_pagos = [["ID Pago", "ID Sus.", "Monto", "Fecha"]]
        tabla_pagos = Table(enc_pagos + todos_pagos,
                            colWidths=[3*cm, 3*cm, 4*cm, 8*cm])
        tabla_pagos.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#198754")),
            ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),
             [colors.HexColor("#f0fff4"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        elementos.append(tabla_pagos)

        total_pagado = sum(float(p[2].replace("$","")) for p in todos_pagos)
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph(
            f"<b>Total pagado: ${total_pagado:.2f}</b>", styles["GymCampo"]))
    else:
        elementos.append(Paragraph("Sin pagos registrados.", styles["GymCampo"]))

    # Pie de página
    elementos.append(Spacer(1, 20))
    elementos.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#dddddd"), spaceAfter=6))
    elementos.append(_footer_text(styles))

    # Generar PDF
    doc = SimpleDocTemplate(ruta, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    doc.build(elementos)
    messagebox.showinfo("PDF generado", f"Ficha guardada en:\n{ruta}", parent=parent)
    os.startfile(ruta)

# PDF 2 — REPORTE MENSUAL

def generar_pdf_reporte_mensual(parent, mes=None, anio=None):
    """
    Genera un reporte mensual con:
    - Resumen de ingresos
    - Lista de pagos del mes
    - Clientes activos
    """
    import sqlite3
    if not mes:
        mes  = datetime.now().month
    if not anio:
        anio = datetime.now().year

    mes_str  = f"{mes:02d}"
    anio_str = str(anio)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH  = os.path.join(BASE_DIR, "..", "gym.db")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Pagos del mes
    cur.execute("""
        SELECT s.id, c.nombre, m.nombre_plan, s.pagado, s.fecha_inicio
        FROM suscripciones s
        JOIN clientes c ON s.cliente_id = c.id
        JOIN membresias m ON s.membresia_id = m.id
        WHERE strftime('%m', s.fecha_inicio) = ?
          AND strftime('%Y', s.fecha_inicio) = ?
          AND s.pagado > 0
        ORDER BY s.fecha_inicio
    """, (mes_str, anio_str))
    pagos_mes = cur.fetchall()

    # Clientes activos
    cur.execute("""
        SELECT c.nombre, m.nombre_plan, s.fecha_vencimiento, s.pagado, s.pendiente
        FROM suscripciones s
        JOIN clientes c ON s.cliente_id = c.id
        JOIN membresias m ON s.membresia_id = m.id
        WHERE s.fecha_vencimiento >= date('now')
        ORDER BY s.fecha_vencimiento
    """)
    activos = cur.fetchall()
    con.close()

    nombres_meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                     "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    nombre_mes = nombres_meses[mes - 1]

    ruta = filedialog.asksaveasfilename(
        parent=parent,
        title="Guardar reporte mensual",
        defaultextension=".pdf",
        initialfile=f"Reporte_{nombre_mes}_{anio_str}.pdf",
        filetypes=[("PDF", "*.pdf")]
    )
    if not ruta:
        return

    styles    = _estilos()
    elementos = []

    _header(elementos, styles,
            f"Reporte Mensual — {nombre_mes} {anio_str}",
            f"Generado el {datetime.now().strftime('%d/%m/%Y')}")
    elementos.append(Spacer(1, 10))

    # Resumen
    total_ingresos  = sum(float(p[3]) for p in pagos_mes)
    total_pagos     = len(pagos_mes)
    total_activos   = len(activos)

    elementos.append(Paragraph("Resumen del Mes", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    resumen = [
        ["Total ingresos",    f"${total_ingresos:.2f}"],
        ["Pagos registrados", str(total_pagos)],
        ["Clientes activos",  str(total_activos)],
    ]
    t_resumen = Table(resumen, colWidths=[7*cm, 11*cm])
    t_resumen.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (0,-1), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR",    (0,0), (0,-1), colors.white),
        ("FONTNAME",     (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",     (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",     (0,0), (-1,-1), 11),
        ("ROWBACKGROUNDS",(1,0),(1,-1),[colors.HexColor("#f0f4ff"), colors.white]),
        ("GRID",         (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
    ]))
    elementos.append(t_resumen)
    elementos.append(Spacer(1, 16))

    # Pagos del mes
    elementos.append(Paragraph("Detalle de Pagos del Mes", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    if pagos_mes:
        enc = [["ID", "Cliente", "Plan", "Monto", "Fecha"]]
        filas_pagos = [[str(p[0]), str(p[1]), str(p[2]),
                        f"${float(p[3]):.2f}", str(p[4])] for p in pagos_mes]
        t_pagos = Table(enc + filas_pagos,
                        colWidths=[1.5*cm, 6*cm, 5*cm, 3*cm, 2.5*cm])
        t_pagos.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#198754")),
            ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),
             [colors.HexColor("#f0fff4"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("ALIGN",         (3,0), (4,-1),  "CENTER"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))
        elementos.append(t_pagos)
    else:
        elementos.append(Paragraph("Sin pagos registrados en este mes.", styles["GymCampo"]))

    elementos.append(Spacer(1, 16))

    # Clientes activos
    elementos.append(Paragraph("Clientes con Suscripción Activa", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    if activos:
        enc_act = [["Cliente", "Plan", "Vence", "Pagado", "Pendiente"]]
        filas_act = [[str(a[0]), str(a[1]), str(a[2]),
                      f"${float(a[3]):.2f}", f"${float(a[4]):.2f}"] for a in activos]
        t_act = Table(enc_act + filas_act,
                      colWidths=[5.5*cm, 4.5*cm, 3*cm, 2.5*cm, 2.5*cm])
        t_act.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#1f6aa5")),
            ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),
             [colors.HexColor("#f0f4ff"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("ALIGN",         (3,0), (4,-1),  "CENTER"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))
        elementos.append(t_act)
    else:
        elementos.append(Paragraph("Sin clientes activos.", styles["GymCampo"]))

    # Pie
    elementos.append(Spacer(1, 20))
    elementos.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#dddddd"), spaceAfter=6))
    elementos.append(_footer_text(styles))

    doc = SimpleDocTemplate(ruta, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    doc.build(elementos)
    messagebox.showinfo("PDF generado", f"Reporte guardado en:\n{ruta}", parent=parent)
    os.startfile(ruta)