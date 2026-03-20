import os
import sys
import json
import tkinter as tk
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from tkinter import filedialog, messagebox
from modulos.rutas import get_db_path, get_config_path, get_assets_dir
import sys, os, json, tkinter as tk
from datetime import datetime
DB_PATH = get_db_path()

# ── Rutas ─────────────────────────────────────────────────────────────────────

if getattr(sys, 'frozen', False):
    _RAIZ = os.path.dirname(sys.executable)
else:
    _RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.path.join(_RAIZ, "Config.JSON")

# ... resto de imports de reportlab igual

CONFIG_PATH = get_config_path()

def _leer_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _ruta_assets_lectura(nombre_archivo):
    return os.path.join(get_assets_dir(), nombre_archivo)

# ── Estilos ───────────────────────────────────────────────────────────────────

def _estilos():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("GymTitulo",   parent=styles["Normal"],
               fontSize=16, fontName="Helvetica-Bold",
               textColor=colors.HexColor("#1a1a2e"), alignment=TA_LEFT,
               spaceAfter=6))
    styles.add(ParagraphStyle("GymSubtitulo", parent=styles["Normal"],
               fontSize=11, fontName="Helvetica",
               textColor=colors.HexColor("#555555"), alignment=TA_LEFT,
               spaceBefore=4))
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
    config = _leer_config()
    nombre_gym = config.get("nombre_gimnasio", "Gimnasio")
    telefono   = config.get("telefono", "")
    direccion  = config.get("direccion", "")
    correo     = config.get("correo", "")

    ruta_logo = _ruta_assets_lectura("logo_gym.jpg")

    col_izq = []
    if os.path.exists(ruta_logo):
        try:
            col_izq.append(RLImage(ruta_logo, width=2.5*cm, height=2.5*cm))
        except Exception:
            pass
    col_izq.append(Spacer(1, 4))
    col_izq.append(Paragraph(titulo,    styles["GymTitulo"]))
    col_izq.append(Paragraph(subtitulo, styles["GymSubtitulo"]))

    col_der = [Paragraph(nombre_gym, styles["GymNombreGym"])]
    if telefono:
        col_der.append(Paragraph(f"■ {telefono}", styles["GymInfoGym"]))
    if direccion:
        col_der.append(Paragraph(f"■ {direccion}", styles["GymInfoGym"]))
    if correo:
        col_der.append(Paragraph(f"✉ {correo}", styles["GymInfoGym"]))

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

# ══════════════════════════════════════════════════════════════════════════════
# PDF 1 — FICHA DEL CLIENTE
# ══════════════════════════════════════════════════════════════════════════════

def generar_pdf_ficha_cliente(parent, cliente_id, nombre_cliente):
    from modulos.clientes import ver_clientes
    from modulos.pagos import buscar_cliente_pagos
    from modulos.ficha_cliente import obtener_ficha, obtener_historial

    cliente = next((c for c in ver_clientes() if c[0] == cliente_id), None)
    if not cliente:
        messagebox.showerror("Error", "No se encontró el cliente.", parent=parent)
        return

    ficha     = obtener_ficha(cliente_id) or {}
    historial = obtener_historial(cliente_id)
    suscs     = buscar_cliente_pagos(cliente_id)

    # ── Ventana de objetivo actual ────────────────────────────────────────────
    objetivo_extra = {"valor": None}

    win = tk.Toplevel(parent)
    win.title("Objetivo del Cliente")
    win.geometry("420x200")
    win.resizable(False, False)
    win.grab_set()
    win.focus_force()

    # Centrar
    parent.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width()  // 2) - 210
    y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text=f"¿Cuál es el objetivo de {nombre_cliente} por el momento?",
             font=("Segoe UI", 11, "bold"), wraplength=380,
             justify="center").pack(pady=(20, 12))

    entry_obj = tk.Entry(win, font=("Segoe UI", 11), width=42)
    entry_obj.pack(pady=(0, 16))
    entry_obj.focus_set()

    def confirmar():
        objetivo_extra["valor"] = entry_obj.get().strip()
        win.destroy()

    def cancelar():
        win.destroy()

    entry_obj.bind("<Return>", lambda e: confirmar())

    frame_btns = tk.Frame(win)
    frame_btns.pack()
    tk.Button(frame_btns, text="Generar PDF", font=("Segoe UI", 11, "bold"),
              bg="#198754", fg="white", padx=12, pady=4,
              command=confirmar).pack(side="left", padx=8)
    tk.Button(frame_btns, text="Cancelar", font=("Segoe UI", 11),
              padx=12, pady=4, command=cancelar).pack(side="left", padx=8)

    win.wait_window()

    if objetivo_extra["valor"] is None:
        return

    # ── Elegir dónde guardar ──────────────────────────────────────────────────
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

    _header(elementos, styles, "Ficha del Cliente",
            f"Generado el {datetime.now().strftime('%d/%m/%Y')}")
    elementos.append(Spacer(1, 10))

    # Objetivo actual del cliente
    if objetivo_extra["valor"]:
        elementos.append(Paragraph(
            f"<b>Objetivo actual:</b> {objetivo_extra['valor']}",
            styles["GymCampo"]
        ))
        elementos.append(Spacer(1, 8))

    # Foto + datos personales
    col_izq = []
    ruta_foto = ficha.get("foto_ruta")
    if ruta_foto and os.path.exists(ruta_foto):
        try:
            col_izq.append(RLImage(ruta_foto, width=3.5*cm, height=3.5*cm))
        except Exception:
            col_izq.append(Paragraph("Sin foto", styles["GymCampo"]))
    else:
        col_izq.append(Paragraph("Sin foto", styles["GymCampo"]))

    col_der = [
        Paragraph(str(cliente[1]), ParagraphStyle("NombreCliente",
            parent=styles["Normal"], fontSize=18, fontName="Helvetica-Bold",
            textColor=colors.HexColor("#1a1a2e"))),
        Spacer(1, 4),
        Paragraph(f"<b>Cedula:</b> {cliente[2]}", styles["GymCampo"]),
        Paragraph(f"<b>Telefono:</b> {cliente[3]}", styles["GymCampo"]),
        Paragraph(f"<b>Fecha de registro:</b> {cliente[4]}", styles["GymCampo"]),
    ]

    t_perfil = Table([[col_izq, col_der]], colWidths=[4*cm, 14*cm])
    t_perfil.setStyle(TableStyle([
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("BACKGROUND",   (0,0), (-1,-1), colors.HexColor("#f0f4ff")),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
    ]))
    elementos.append(t_perfil)
    elementos.append(Spacer(1, 14))

    # Objetivo y estado físico
    elementos.append(Paragraph("Objetivo y Estado Fisico", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    objetivo      = ficha.get("objetivo",      "No registrado")
    objetivo_2    = ficha.get("objetivo_2",    "No registrado")
    estado_fisico = ficha.get("estado_fisico", "No registrado")
    status_fisico = ficha.get("status_fisico", "No registrado")
    notas         = ficha.get("notas", "")

    t_obj = Table([
        ["Objetivo principal",  objetivo],
        ["Objetivo secundario", objetivo_2],
        ["Estado fisico",       estado_fisico],
        ["Status",              status_fisico],
    ], colWidths=[5*cm, 13*cm])
    t_obj.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR",     (0,0), (0,-1), colors.white),
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(1,0),(1,-1),[colors.HexColor("#f0f4ff"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elementos.append(t_obj)

    if notas:
        elementos.append(Spacer(1, 6))
        elementos.append(Paragraph(f"<b>Notas:</b> {notas}", styles["GymCampo"]))

    elementos.append(Spacer(1, 14))

    # Datos físicos
    elementos.append(Paragraph("Datos Fisicos", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    peso_kg       = ficha.get("peso_kg")
    altura_m      = ficha.get("altura_m")
    cir_abdominal = ficha.get("cir_abdominal")
    peso_ideal    = ficha.get("peso_ideal")

    imc_texto = "No calculado"
    if peso_kg and altura_m:
        try:
            imc = round(float(peso_kg) / (float(altura_m) ** 2), 2)
            if   imc < 18.5: cat = "Bajo peso"
            elif imc < 25:   cat = "Normal"
            elif imc < 30:   cat = "Sobrepeso"
            else:            cat = "Obesidad"
            imc_texto = f"{imc} ({cat})"
        except Exception:
            pass

    t_fis = Table([
        ["Peso actual (kg)",         str(peso_kg)       if peso_kg       else "No registrado"],
        ["Altura (m)",               str(altura_m)      if altura_m      else "No registrado"],
        ["IMC",                      imc_texto],
        ["Circunferencia abdominal", str(cir_abdominal) if cir_abdominal else "No registrado"],
        ["Peso ideal (kg)",          str(peso_ideal)    if peso_ideal    else "No registrado"],
    ], colWidths=[5*cm, 13*cm])
    t_fis.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), colors.HexColor("#198754")),
        ("TEXTCOLOR",     (0,0), (0,-1), colors.white),
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(1,0),(1,-1),[colors.HexColor("#f0fff4"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elementos.append(t_fis)
    elementos.append(Spacer(1, 14))

    # Condiciones médicas
    elementos.append(Paragraph("Condiciones Medicas", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    condiciones_map = [
        ("lesion",         "Lesion muscular o articular"),
        ("cardiovascular", "Enfermedad cardiovascular"),
        ("asfixia",        "Se asfixia con facilidad"),
        ("asmatico",       "Asmatico / Epileptico / Diabetico"),
        ("medicacion",     "Toma medicacion actualmente"),
        ("mareos",         "Mareos o desmayos al ejercitar"),
    ]

    filas_med = []
    for key, label in condiciones_map:
        val   = ficha.get(key, "NO")
        tiene = str(val).upper() == "SI"
        filas_med.append([label, "SI" if tiene else "NO"])

    t_med = Table(filas_med, colWidths=[13*cm, 5*cm])
    t_med.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.HexColor("#fff8f8"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("ALIGN",         (1,0), (1,-1), "CENTER"),
        ("FONTNAME",      (1,0), (1,-1), "Helvetica-Bold"),
    ]))
    for i, (key, _) in enumerate(condiciones_map):
        if str(ficha.get(key, "NO")).upper() == "SI":
            t_med.setStyle(TableStyle([
                ("TEXTCOLOR", (1,i), (1,i), colors.HexColor("#dc3545")),
            ]))
    elementos.append(t_med)
    elementos.append(Spacer(1, 14))

    # Suscripción
    elementos.append(Paragraph("Suscripcion", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    if suscs:
        enc = [["Plan", "Total", "Pagado", "Pendiente", "Inicio", "Vence"]]
        filas_sus = [[str(s[2]), f"${float(s[3]):.2f}", f"${float(s[4]):.2f}",
                      f"${float(s[5]):.2f}", str(s[6]), str(s[7])] for s in suscs]
        t_sus = Table(enc + filas_sus,
                      colWidths=[5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        t_sus.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#1f6aa5")),
            ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f4ff"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        elementos.append(t_sus)
    else:
        elementos.append(Paragraph("Sin suscripciones registradas.", styles["GymCampo"]))

    elementos.append(Spacer(1, 14))

    # Historial de medidas
    if historial:
        elementos.append(Paragraph("Historial de Medidas", styles["GymSeccion"]))
        elementos.append(Spacer(1, 6))

        enc_h   = [["Fecha", "Peso (kg)", "Altura (cm)", "IMC", "Notas"]]
        filas_h = []
        for id_m, fecha, peso, altura, imc, notas_h in historial:
            if   imc < 18.5: cat = f"{imc} (Bajo peso)"
            elif imc < 25:   cat = f"{imc} (Normal)"
            elif imc < 30:   cat = f"{imc} (Sobrepeso)"
            else:            cat = f"{imc} (Obesidad)"
            filas_h.append([str(fecha), str(peso), str(altura), cat, notas_h or ""])

        t_hist = Table(enc_h + filas_h,
                       colWidths=[2.8*cm, 2.5*cm, 3*cm, 5*cm, 4.7*cm])
        t_hist.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#6f42c1")),
            ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8f4ff"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("ALIGN",         (1,0), (3,-1),  "CENTER"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))
        elementos.append(t_hist)
        elementos.append(Spacer(1, 14))

    # Mensaje motivacional
    elementos.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#1f6aa5"), spaceAfter=10))
    elementos.append(Paragraph(
        "<b>Cada dia es una oportunidad para ser mejor que ayer!</b>",
        ParagraphStyle("Motiv", parent=styles["Normal"],
                       fontSize=11, fontName="Helvetica-Bold",
                       textColor=colors.HexColor("#1f6aa5"),
                       alignment=TA_CENTER)
    ))
    elementos.append(Spacer(1, 10))

    # Pie
    elementos.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#dddddd"), spaceAfter=6))
    elementos.append(_footer_text(styles))

    doc = SimpleDocTemplate(ruta, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    doc.build(elementos)
    messagebox.showinfo("PDF generado", f"Ficha guardada en:\n{ruta}", parent=parent)
    os.startfile(ruta)

# ══════════════════════════════════════════════════════════════════════════════
# PDF 2 — REPORTE MENSUAL
# ══════════════════════════════════════════════════════════════════════════════

def generar_pdf_reporte_mensual(parent, mes=None, anio=None):
    import sqlite3
    if not mes:
        mes  = datetime.now().month
    if not anio:
        anio = datetime.now().year

    mes_str  = f"{mes:02d}"
    anio_str = str(anio)


    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

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
            f"Reporte Mensual - {nombre_mes}",
            f"Año {anio_str}  ·  Generado el {datetime.now().strftime('%d/%m/%Y')}")
    elementos.append(Spacer(1, 10))

    total_ingresos = sum(float(p[3]) for p in pagos_mes)
    total_pagos    = len(pagos_mes)
    total_activos  = len(activos)

    elementos.append(Paragraph("Resumen del Mes", styles["GymSeccion"]))
    elementos.append(Spacer(1, 6))

    resumen = [
        ["Total ingresos",    f"${total_ingresos:.2f}"],
        ["Pagos registrados", str(total_pagos)],
        ["Clientes activos",  str(total_activos)],
    ]
    t_resumen = Table(resumen, colWidths=[7*cm, 11*cm])
    t_resumen.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR",     (0,0), (0,-1), colors.white),
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 11),
        ("ROWBACKGROUNDS",(1,0),(1,-1),[colors.HexColor("#f0f4ff"), colors.white]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    elementos.append(t_resumen)
    elementos.append(Spacer(1, 16))

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
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0fff4"), colors.white]),
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

    elementos.append(Paragraph("Clientes con Suscripcion Activa", styles["GymSeccion"]))
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
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f0f4ff"), colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("ALIGN",         (3,0), (4,-1),  "CENTER"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ]))
        elementos.append(t_act)

        total_pagado_activos    = sum(float(a[3]) for a in activos)
        total_pendiente_activos = sum(float(a[4]) for a in activos)
        elementos.append(Spacer(1, 6))
        fila_total = [["", "TOTAL", "", f"${total_pagado_activos:.2f}", f"${total_pendiente_activos:.2f}"]]
        t_total = Table(fila_total, colWidths=[5.5*cm, 4.5*cm, 3*cm, 2.5*cm, 2.5*cm])
        t_total.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR",    (0,0), (-1,-1), colors.white),
            ("FONTNAME",     (0,0), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 10),
            ("ALIGN",        (0,0), (-1,-1), "CENTER"),
            ("TOPPADDING",   (0,0), (-1,-1), 7),
            ("BOTTOMPADDING",(0,0), (-1,-1), 7),
        ]))
        elementos.append(t_total)
    else:
        elementos.append(Paragraph("Sin clientes activos.", styles["GymCampo"]))

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