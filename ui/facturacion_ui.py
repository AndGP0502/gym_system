import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import sqlite3
import os
from datetime import datetime

from modulos.rutas import get_db_path
from services.factura_service import (
    obtener_config_sri, guardar_factura,
    procesar_factura_completa
)

DB_PATH = get_db_path()

def abrir_ventana_facturacion(parent):
    ventana = ctk.CTkToplevel(parent)
    ventana.title("Facturación Electrónica")
    ventana.geometry("1400x850")
    ventana.minsize(1200, 750)
    ventana.resizable(True, True)
    ventana.attributes("-topmost", True)
    ventana.after(300, lambda: ventana.attributes("-topmost", False))
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    canvas_p = tk.Canvas(ventana, highlightthickness=0, bg="#1e1e2e")
    sb_p     = ttk.Scrollbar(ventana, orient="vertical", command=canvas_p.yview)
    canvas_p.configure(yscrollcommand=sb_p.set)
    sb_p.pack(side="right", fill="y")
    canvas_p.pack(side="left", fill="both", expand=True)

    scroll = ctk.CTkFrame(canvas_p, fg_color="#1e1e2e")
    sid    = canvas_p.create_window((0, 0), window=scroll, anchor="nw")

    scroll.bind("<Configure>", lambda e: canvas_p.configure(scrollregion=canvas_p.bbox("all")))
    canvas_p.bind("<Configure>", lambda e: canvas_p.itemconfig(sid, width=e.width))
    canvas_p.bind("<MouseWheel>", lambda e: canvas_p.yview_scroll(int(-1*(e.delta/120)*2), "units"))

    # ── HEADER ────────────────────────────────────────────────────────────────
    header = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    header.pack(fill="x", padx=20, pady=(20, 10))

    ctk.CTkLabel(header, text="🧾 Facturación Electrónica",
                 font=("Segoe UI", 26, "bold"), text_color="#cba6f7").pack(side="left", padx=20, pady=18)
    ctk.CTkLabel(header, text="SRI Ecuador — Emisión electrónica",
                 font=("Segoe UI", 13), text_color="#6c7086").pack(side="left")
    ctk.CTkButton(header, text="⚙ Configurar SRI", width=160, height=38,
                  fg_color="#313244", hover_color="#45475a",
                  font=("Segoe UI", 13, "bold"),
                  command=lambda: abrir_config_sri(ventana)).pack(side="right", padx=10)
    ctk.CTkButton(header, text="← Volver", width=110, height=38,
                  fg_color="#2A2A2A", hover_color="#3A3A3A",
                  font=("Segoe UI", 13, "bold"),
                  command=ventana.destroy).pack(side="right", padx=(20, 4))

    # ── TARJETAS ──────────────────────────────────────────────────────────────
    frame_cards = ctk.CTkFrame(scroll, fg_color="transparent")
    frame_cards.pack(fill="x", padx=20, pady=10)

    def _card(parent, color, icono, titulo, col):
        f = ctk.CTkFrame(parent, corner_radius=14, fg_color=color, height=100)
        f.grid(row=0, column=col, padx=8, sticky="ew")
        f.grid_propagate(False)
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(f, text=icono, font=("Segoe UI", 24)).pack(pady=(12, 2))
        ctk.CTkLabel(f, text=titulo, font=("Segoe UI", 11), text_color="#cdd6f4").pack()
        lbl = ctk.CTkLabel(f, text="0", font=("Segoe UI", 22, "bold"), text_color="white")
        lbl.pack(pady=(2, 10))
        return lbl

    lbl_emitidas    = _card(frame_cards, "#1e3a5f", "📄", "Emitidas hoy",  0)
    lbl_autorizadas = _card(frame_cards, "#1a4731", "✅", "Autorizadas",    1)
    lbl_mes         = _card(frame_cards, "#3d1f5c", "📅", "Este mes",       2)
    lbl_total_mes   = _card(frame_cards, "#4a1c1c", "💰", "Recaudado ($)",  3)

    def actualizar_cards():
        con = sqlite3.connect(DB_PATH)
        hoy = datetime.now().strftime("%Y-%m-%d")
        mes = datetime.now().strftime("%Y-%m")
        e = con.execute("SELECT COUNT(*) FROM facturas WHERE fecha_emision=?", (hoy,)).fetchone()[0]
        a = con.execute("SELECT COUNT(*) FROM facturas WHERE estado='AUTORIZADO'").fetchone()[0]
        m = con.execute("SELECT COUNT(*) FROM facturas WHERE fecha_emision LIKE ?", (f"{mes}%",)).fetchone()[0]
        t = con.execute("SELECT COALESCE(SUM(total),0) FROM facturas WHERE fecha_emision LIKE ? AND estado='AUTORIZADO'", (f"{mes}%",)).fetchone()[0]
        con.close()
        lbl_emitidas.configure(text=str(e))
        lbl_autorizadas.configure(text=str(a))
        lbl_mes.configure(text=str(m))
        lbl_total_mes.configure(text=f"${t:,.2f}")

    # ── FORMULARIO ────────────────────────────────────────────────────────────
    frame_form = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_form.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_form, text="Nueva Factura",
                 font=("Segoe UI", 18, "bold"), text_color="#89b4fa").pack(anchor="w", padx=20, pady=(16, 4))
    ctk.CTkLabel(frame_form, text="Datos del receptor",
                 font=("Segoe UI", 12), text_color="#6c7086").pack(anchor="w", padx=20)

    grid_receptor = ctk.CTkFrame(frame_form, fg_color="transparent")
    grid_receptor.pack(fill="x", padx=20, pady=12)

    def _lbl_entry(parent, texto, row, col, width=260):
        ctk.CTkLabel(parent, text=texto, font=("Segoe UI", 12),
                     text_color="#cdd6f4").grid(row=row*2, column=col, sticky="w", padx=8)
        e = ctk.CTkEntry(parent, width=width, height=36)
        e.grid(row=row*2+1, column=col, padx=8, pady=(2, 10), sticky="w")
        return e

    entry_id        = _lbl_entry(grid_receptor, "Cédula / RUC",  0, 0)
    entry_nombre    = _lbl_entry(grid_receptor, "Razón Social",   0, 1, 340)
    entry_correo    = _lbl_entry(grid_receptor, "Correo",         0, 2, 260)
    entry_telefono  = _lbl_entry(grid_receptor, "Teléfono",       1, 0)
    entry_direccion = _lbl_entry(grid_receptor, "Dirección",      1, 1, 340)

    combo_tipo_id = ctk.CTkComboBox(
        grid_receptor, width=180,
        values=["05 - Cédula", "04 - RUC", "06 - Pasaporte", "07 - Consumidor Final"],
        state="readonly"
    )
    ctk.CTkLabel(grid_receptor, text="Tipo ID",
                 font=("Segoe UI", 12), text_color="#cdd6f4").grid(row=2, column=2, sticky="w", padx=8)
    combo_tipo_id.grid(row=3, column=2, padx=8, pady=(2, 10), sticky="w")
    combo_tipo_id.set("05 - Cédula")

    def buscar_cliente_por_id(event=None):
        cedula = entry_id.get().strip()
        if len(cedula) < 5:
            return
        con = sqlite3.connect(DB_PATH)
        c = con.execute("SELECT nombre, telefono FROM clientes WHERE cedula=? LIMIT 1", (cedula,)).fetchone()
        con.close()
        if c:
            entry_nombre.delete(0, "end"); entry_nombre.insert(0, c[0])
            entry_telefono.delete(0, "end"); entry_telefono.insert(0, c[1] or "")

    entry_id.bind("<FocusOut>", buscar_cliente_por_id)
    entry_id.bind("<Return>", buscar_cliente_por_id)

    # ── DETALLE ───────────────────────────────────────────────────────────────
    frame_detalle = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_detalle.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_detalle, text="Detalle de Servicios",
                 font=("Segoe UI", 18, "bold"), text_color="#89b4fa").pack(anchor="w", padx=20, pady=(16, 4))

    frame_item = ctk.CTkFrame(frame_detalle, fg_color="#313244", corner_radius=10)
    frame_item.pack(fill="x", padx=20, pady=(0, 10))

    ctk.CTkLabel(frame_item, text="Descripción", font=("Segoe UI", 11), text_color="#cdd6f4").grid(row=0, column=0, padx=8, pady=(8,2), sticky="w")
    entry_desc = ctk.CTkEntry(frame_item, width=280, height=34)
    entry_desc.grid(row=1, column=0, padx=8, pady=(0,10))

    ctk.CTkLabel(frame_item, text="Cantidad", font=("Segoe UI", 11), text_color="#cdd6f4").grid(row=0, column=1, padx=8, pady=(8,2), sticky="w")
    entry_cant = ctk.CTkEntry(frame_item, width=80, height=34)
    entry_cant.insert(0, "1")
    entry_cant.grid(row=1, column=1, padx=8, pady=(0,10))

    ctk.CTkLabel(frame_item, text="Precio Unit.", font=("Segoe UI", 11), text_color="#cdd6f4").grid(row=0, column=2, padx=8, pady=(8,2), sticky="w")
    entry_precio = ctk.CTkEntry(frame_item, width=100, height=34)
    entry_precio.grid(row=1, column=2, padx=8, pady=(0,10))

    ctk.CTkLabel(frame_item, text="Descuento", font=("Segoe UI", 11), text_color="#cdd6f4").grid(row=0, column=3, padx=8, pady=(8,2), sticky="w")
    entry_desc_val = ctk.CTkEntry(frame_item, width=80, height=34)
    entry_desc_val.insert(0, "0")
    entry_desc_val.grid(row=1, column=3, padx=8, pady=(0,10))

    ctk.CTkLabel(frame_item, text="IVA", font=("Segoe UI", 11), text_color="#cdd6f4").grid(row=0, column=4, padx=8, pady=(8,2), sticky="w")
    combo_iva = ctk.CTkComboBox(frame_item, width=100, values=["15%", "0%"], state="readonly")
    combo_iva.set("15%")
    combo_iva.grid(row=1, column=4, padx=8, pady=(0,10))

    ctk.CTkButton(frame_item, text="+ Agregar", width=110, height=34,
                  fg_color="#1e3a5f", hover_color="#2d5a8e",
                  font=("Segoe UI", 12, "bold"),
                  command=lambda: agregar_item()).grid(row=1, column=5, padx=12, pady=(0,10))

    style = ttk.Style()
    style.configure("Fact.Treeview", font=("Segoe UI", 10), rowheight=30)
    style.configure("Fact.Treeview.Heading", font=("Segoe UI", 10, "bold"))

    cols_tabla = ("Descripción", "Cant.", "Precio", "Desc.", "IVA%", "Subtotal", "IVA", "Total")
    tabla_items = ttk.Treeview(frame_detalle, columns=cols_tabla, show="headings", height=6, style="Fact.Treeview")
    for col in cols_tabla:
        tabla_items.heading(col, text=col)
        tabla_items.column(col, width=110, anchor="center", minwidth=60)
    tabla_items.column("Descripción", width=220, anchor="w")
    tabla_items.pack(fill="x", padx=20, pady=(0, 6))

    ctk.CTkButton(frame_detalle, text="🗑 Eliminar seleccionado",
                  width=180, height=32, fg_color="#4a1c1c",
                  hover_color="#7f1d1d", font=("Segoe UI", 11),
                  command=lambda: eliminar_item()).pack(anchor="e", padx=20, pady=(0, 12))

    items = []

    def agregar_item():
        try:
            desc    = entry_desc.get().strip()
            cant    = float(entry_cant.get())
            precio  = float(entry_precio.get())
            desc_v  = float(entry_desc_val.get())
            pct_iva = 15.0 if combo_iva.get() == "15%" else 0.0
            if not desc:
                messagebox.showwarning("Advertencia", "Ingresa una descripción.", parent=ventana)
                return
            subtotal = round((precio - desc_v) * cant, 2)
            iva      = round(subtotal * pct_iva / 100, 2)
            total    = round(subtotal + iva, 2)
            item = {"descripcion": desc, "cantidad": cant, "precio_unitario": precio,
                    "descuento": desc_v, "porcentaje_iva": pct_iva,
                    "subtotal": subtotal, "iva": iva, "total": total}
            items.append(item)
            tabla_items.insert("", "end", values=(
                desc, cant, f"${precio:.2f}", f"${desc_v:.2f}",
                f"{pct_iva:.0f}%", f"${subtotal:.2f}", f"${iva:.2f}", f"${total:.2f}"
            ))
            entry_desc.delete(0, "end")
            entry_cant.delete(0, "end"); entry_cant.insert(0, "1")
            entry_precio.delete(0, "end")
            entry_desc_val.delete(0, "end"); entry_desc_val.insert(0, "0")
            calcular_totales()
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números.", parent=ventana)

    def eliminar_item():
        sel = tabla_items.selection()
        if not sel:
            return
        idx = tabla_items.index(sel[0])
        tabla_items.delete(sel[0])
        items.pop(idx)
        calcular_totales()

    # ── TOTALES ───────────────────────────────────────────────────────────────
    frame_totales = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_totales.pack(fill="x", padx=20, pady=10)

    frame_tot_inner = ctk.CTkFrame(frame_totales, fg_color="transparent")
    frame_tot_inner.pack(anchor="e", padx=30, pady=16)

    def _tot_row(texto, bold=False):
        f = ctk.CTkFrame(frame_tot_inner, fg_color="transparent")
        f.pack(fill="x", pady=2)
        ctk.CTkLabel(f, text=texto, width=160, anchor="w",
                     font=("Segoe UI", 12, "bold" if bold else "normal"),
                     text_color="#cdd6f4").pack(side="left")
        lbl = ctk.CTkLabel(f, text="$0.00", width=100, anchor="e",
                           font=("Segoe UI", 12, "bold" if bold else "normal"),
                           text_color="#a6e3a1" if bold else "#cdd6f4")
        lbl.pack(side="left")
        return lbl

    lbl_sub0  = _tot_row("Subtotal IVA 0%:")
    lbl_sub15 = _tot_row("Subtotal IVA 15%:")
    lbl_desc  = _tot_row("Descuento total:")
    lbl_iva15 = _tot_row("IVA 15%:")
    lbl_total = _tot_row("TOTAL:", bold=True)

    def calcular_totales():
        sub0  = sum(i["subtotal"] for i in items if i["porcentaje_iva"] == 0)
        sub15 = sum(i["subtotal"] for i in items if i["porcentaje_iva"] == 15)
        desc  = sum(i["descuento"] * i["cantidad"] for i in items)
        iva15 = sum(i["iva"] for i in items if i["porcentaje_iva"] == 15)
        tot   = sub0 + sub15 + iva15
        lbl_sub0.configure(text=f"${sub0:.2f}")
        lbl_sub15.configure(text=f"${sub15:.2f}")
        lbl_desc.configure(text=f"${desc:.2f}")
        lbl_iva15.configure(text=f"${iva15:.2f}")
        lbl_total.configure(text=f"${tot:.2f}")

    # ── BOTONES ───────────────────────────────────────────────────────────────
    frame_acciones = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_acciones.pack(fill="x", padx=20, pady=(10, 20))

    frame_btns = ctk.CTkFrame(frame_acciones, fg_color="transparent")
    frame_btns.pack(pady=16, padx=20)

    def _btn(texto, color, hover, cmd):
        return ctk.CTkButton(frame_btns, text=texto, width=170, height=44,
                             fg_color=color, hover_color=hover,
                             font=("Segoe UI", 13, "bold"), command=cmd)

    def guardar_borrador():
        if not items:
            messagebox.showwarning("Sin items", "Agrega al menos un servicio.", parent=ventana)
            return
        config = obtener_config_sri()
        if not config:
            messagebox.showerror("Sin configuración", "Configura los datos del SRI primero.", parent=ventana)
            return
        factura = _construir_factura(config)
        fid = guardar_factura(factura, items)
        messagebox.showinfo("Guardado", f"Factura #{fid} guardada como borrador.", parent=ventana)
        cargar_historial()
        actualizar_cards()

    def emitir_factura():
        if not items:
            messagebox.showwarning("Sin items", "Agrega al menos un servicio.", parent=ventana)
            return
        config = obtener_config_sri()
        if not config or not config.get("ruc"):
            messagebox.showerror("Sin configuración", "Configura los datos del SRI primero.", parent=ventana)
            return
        if not config.get("ruta_certificado") or not os.path.exists(config.get("ruta_certificado", "")):
            messagebox.showerror("Sin certificado", "Configura la ruta al archivo .p12 en la configuración SRI.", parent=ventana)
            return
        factura = _construir_factura(config)
        fid = guardar_factura(factura, items)
        messagebox.showinfo("Procesando", "Enviando factura al SRI...\nEsto puede tomar unos segundos.", parent=ventana)
        try:
            resultado = procesar_factura_completa(fid)
            if resultado["ok"]:
                messagebox.showinfo("✅ Autorizada",
                    f"Factura AUTORIZADA por el SRI\n\n"
                    f"Clave de acceso: {resultado['clave_acceso']}\n"
                    f"Autorización: {resultado['numero_autorizacion']}", parent=ventana)
                limpiar_formulario()
            else:
                messagebox.showerror("❌ Error SRI",
                    f"Estado: {resultado.get('estado', 'ERROR')}\n{resultado.get('error', '')}", parent=ventana)
        except Exception as e:
            messagebox.showerror("❌ Error", str(e), parent=ventana)
        cargar_historial()
        actualizar_cards()

    def _construir_factura(config):
        sub0  = sum(i["subtotal"] for i in items if i["porcentaje_iva"] == 0)
        sub15 = sum(i["subtotal"] for i in items if i["porcentaje_iva"] == 15)
        desc  = sum(i["descuento"] * i["cantidad"] for i in items)
        iva15 = sum(i["iva"] for i in items if i["porcentaje_iva"] == 15)
        tot   = sub0 + sub15 + iva15
        tipo_id_map = {"05 - Cédula": "05", "04 - RUC": "04",
                       "06 - Pasaporte": "06", "07 - Consumidor Final": "07"}
        return {
            "fecha_emision":       datetime.now().strftime("%Y-%m-%d"),
            "tipo_identificacion": tipo_id_map.get(combo_tipo_id.get(), "05"),
            "identificacion":      entry_id.get().strip(),
            "razon_social":        entry_nombre.get().strip() or "CONSUMIDOR FINAL",
            "correo":              entry_correo.get().strip(),
            "telefono":            entry_telefono.get().strip(),
            "direccion":           entry_direccion.get().strip() or "N/A",
            "subtotal_0":          sub0,
            "subtotal_15":         sub15,
            "iva_15":              iva15,
            "descuento_total":     desc,
            "total":               tot,
            "establecimiento":     config.get("codigo_establecimiento", "001"),
            "punto_emision":       config.get("punto_emision", "001"),
            "secuencial":          str(config.get("siguiente_secuencial", 1)).zfill(9),
            "ambiente":            config.get("ambiente", 2),
            "ruc_emisor":          config.get("ruc", ""),
            "razon_social_emisor": config.get("razon_social", ""),
        }

    def limpiar_formulario():
        for e in [entry_id, entry_nombre, entry_correo, entry_telefono, entry_direccion]:
            e.delete(0, "end")
        for row in tabla_items.get_children():
            tabla_items.delete(row)
        items.clear()
        calcular_totales()

    _btn("💾 Guardar Borrador", "#1e3a5f", "#2d5a8e", guardar_borrador).pack(side="left", padx=8)
    _btn("🚀 Emitir al SRI",   "#1a4731", "#166534", emitir_factura).pack(side="left", padx=8)
    _btn("🗑 Limpiar",         "#3d1f00", "#78350f", limpiar_formulario).pack(side="left", padx=8)

    # ── HISTORIAL ─────────────────────────────────────────────────────────────
    frame_hist = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_hist.pack(fill="x", padx=20, pady=(0, 20))

    ctk.CTkLabel(frame_hist, text="Historial de Facturas",
                 font=("Segoe UI", 18, "bold"), text_color="#89b4fa").pack(anchor="w", padx=20, pady=(16, 8))

    cols_h = ("ID", "Fecha", "Cliente", "Total", "Estado", "Autorización")
    tabla_hist = ttk.Treeview(frame_hist, columns=cols_h, show="headings", height=8, style="Fact.Treeview")
    for col in cols_h:
        tabla_hist.heading(col, text=col)
        tabla_hist.column(col, width=130, anchor="center", minwidth=60)
    tabla_hist.column("Cliente",      width=220, anchor="w")
    tabla_hist.column("Autorización", width=180, anchor="center")

    tabla_hist.tag_configure("AUTORIZADO", foreground="#a6e3a1")
    tabla_hist.tag_configure("RECHAZADA",  foreground="#f38ba8")
    tabla_hist.tag_configure("PENDIENTE",  foreground="#f9e2af")
    tabla_hist.tag_configure("BORRADOR",   foreground="#89b4fa")

    sb_hist = ttk.Scrollbar(frame_hist, orient="vertical", command=tabla_hist.yview)
    tabla_hist.configure(yscrollcommand=sb_hist.set)
    tabla_hist.pack(side="left", fill="x", expand=True, padx=(20, 0), pady=(0, 8))
    sb_hist.pack(side="right", fill="y", pady=(0, 8), padx=(0, 10))

    # ── BOTÓN PDF ─────────────────────────────────────────────────────────────
    def _generar_pdf_factura(factura_id, parent):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable, Image as RLImage)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        con = sqlite3.connect(DB_PATH)
        fila = con.execute("SELECT * FROM facturas WHERE id=?", (factura_id,)).fetchone()
        cols = ["id","clave_acceso","numero_autorizacion","estado","ambiente",
                "fecha_emision","fecha_autorizacion","ruc_emisor","razon_social_emisor",
                "tipo_identificacion","identificacion","razon_social","correo",
                "telefono","direccion","subtotal_0","subtotal_15","subtotal_no_iva",
                "descuento_total","iva_15","total","establecimiento","punto_emision",
                "secuencial","ruta_xml","ruta_xml_autorizado","ruta_ride",
                "cliente_id","observacion"]
        if not fila:
            messagebox.showerror("Error", "No se encontró la factura.", parent=parent)
            con.close()
            return
        f = dict(zip(cols, fila))
        detalles = con.execute(
            "SELECT descripcion, cantidad, precio_unitario, descuento, porcentaje_iva, subtotal, iva, total FROM factura_detalle WHERE factura_id=?",
            (factura_id,)
        ).fetchall()
        con.close()

        ruta = filedialog.asksaveasfilename(
            parent=parent, title="Guardar factura PDF",
            defaultextension=".pdf",
            initialfile=f"Factura_{f.get('secuencial','')}.pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if not ruta:
            return

        AZUL      = colors.HexColor("#003087")
        AZUL_CLARO= colors.HexColor("#e8f0fe")
        GRIS      = colors.HexColor("#f5f5f5")
        NEGRO     = colors.HexColor("#1a1a1a")

        doc = SimpleDocTemplate(ruta, pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles  = getSampleStyleSheet()
        config  = obtener_config_sri() or {}
        elementos = []

        # ── ENCABEZADO: Logo + Datos emisor + Número factura ──────────────────
        nombre_gym = config.get("razon_social", f.get("razon_social_emisor", ""))
        ruc_emisor = f.get("ruc_emisor", "")
        dir_emisor = config.get("direccion_matriz", "")

        # Columna izquierda: logo
        col_logo = []
        from modulos.rutas import get_app_dir
        import sys
        if getattr(sys, 'frozen', False):
            ruta_logo = os.path.join(os.environ.get("APPDATA",""), "GymSystem", "assets", "logo_gym.jpg")
        else:
            ruta_logo = os.path.join(get_app_dir(), "assets", "logo_gym.jpg")

        if os.path.exists(ruta_logo):
            try:
                col_logo.append(RLImage(ruta_logo, width=3*cm, height=3*cm))
            except Exception:
                col_logo.append(Spacer(1, 3*cm))
        else:
            col_logo.append(Spacer(1, 3*cm))

        # Columna centro: datos del emisor
        col_emisor = [
            Paragraph(f"<b>{nombre_gym}</b>",
                ParagraphStyle("emp", parent=styles["Normal"], fontSize=13,
                               fontName="Helvetica-Bold", textColor=AZUL, alignment=TA_CENTER)),
            Paragraph(f"RUC: {ruc_emisor}",
                ParagraphStyle("ruc", parent=styles["Normal"], fontSize=9,
                               textColor=NEGRO, alignment=TA_CENTER)),
            Paragraph(f"Dirección: {dir_emisor}",
                ParagraphStyle("dir", parent=styles["Normal"], fontSize=9,
                               textColor=NEGRO, alignment=TA_CENTER)),
        ]

        # Columna derecha: número de factura en caja azul
        num_factura = f"{f.get('establecimiento','001')}-{f.get('punto_emision','001')}-{f.get('secuencial','')}"
        col_factura = [
            Paragraph("<b>FACTURA</b>",
                ParagraphStyle("ftit", parent=styles["Normal"], fontSize=14,
                               fontName="Helvetica-Bold", textColor=colors.white, alignment=TA_CENTER)),
            Paragraph(f"<b>No. {num_factura}</b>",
                ParagraphStyle("fnum", parent=styles["Normal"], fontSize=10,
                               textColor=colors.white, alignment=TA_CENTER)),
            Spacer(1, 4),
            Paragraph(f"Fecha: {f.get('fecha_emision','')}",
                ParagraphStyle("ffec", parent=styles["Normal"], fontSize=9,
                               textColor=colors.white, alignment=TA_CENTER)),
            Paragraph(f"Ambiente: {'PRODUCCION' if f.get('ambiente')==2 else 'PRUEBAS'}",
                ParagraphStyle("famb", parent=styles["Normal"], fontSize=8,
                               textColor=colors.HexColor("#ccddff"), alignment=TA_CENTER)),
        ]

        t_header = Table([[col_logo, col_emisor, col_factura]], colWidths=[3.5*cm, 9*cm, 5*cm])
        t_header.setStyle(TableStyle([
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("BACKGROUND",  (2,0), (2,0),   AZUL),
            ("ROUNDEDCORNERS", [6,6,6,6]),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING",(0,0), (-1,-1), 8),
            ("TOPPADDING",  (0,0), (-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("BOX",         (0,0), (-1,-1), 1, colors.HexColor("#cccccc")),
        ]))
        elementos.append(t_header)
        elementos.append(Spacer(1, 10))
        elementos.append(HRFlowable(width="100%", thickness=2, color=AZUL, spaceAfter=8))

        # ── DATOS DEL RECEPTOR ────────────────────────────────────────────────
        elementos.append(Paragraph("<b>DATOS DEL RECEPTOR</b>",
            ParagraphStyle("sec", parent=styles["Normal"], fontSize=10,
                           fontName="Helvetica-Bold", textColor=colors.white,
                           backColor=AZUL, leftIndent=-5, rightIndent=-5,
                           spaceBefore=2, spaceAfter=4)))

        tipo_map = {"05":"Cédula","04":"RUC","06":"Pasaporte","07":"Consumidor Final"}
        tipo_id  = tipo_map.get(f.get("tipo_identificacion","05"), "Cédula")

        datos_rec = [
            [f"<b>Razón Social:</b>  {f.get('razon_social','')}",
             f"<b>Tipo ID:</b>  {tipo_id}"],
            [f"<b>Identificación:</b>  {f.get('identificacion','')}",
             f"<b>Teléfono:</b>  {f.get('telefono','')}"],
            [f"<b>Dirección:</b>  {f.get('direccion','')}",
             f"<b>Correo:</b>  {f.get('correo','')}"],
        ]
        st_rec = ParagraphStyle("rec", parent=styles["Normal"], fontSize=9, textColor=NEGRO)
        filas_rec = [[Paragraph(c[0], st_rec), Paragraph(c[1], st_rec)] for c in datos_rec]
        t_rec = Table(filas_rec, colWidths=[9*cm, 8.5*cm])
        t_rec.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), GRIS),
            ("GRID",         (0,0),(-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("TOPPADDING",   (0,0),(-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ]))
        elementos.append(t_rec)
        elementos.append(Spacer(1, 10))

        # ── DETALLE ───────────────────────────────────────────────────────────
        elementos.append(Paragraph("<b>DETALLE DE SERVICIOS</b>",
            ParagraphStyle("sec2", parent=styles["Normal"], fontSize=10,
                           fontName="Helvetica-Bold", textColor=colors.white,
                           backColor=AZUL, spaceBefore=2, spaceAfter=4)))

        enc = [["Descripción","Cant.","P.Unit.","Desc.","IVA%","Subtotal","IVA","Total"]]
        filas_det = [[d[0], f"{d[1]:.2f}", f"${d[2]:.2f}", f"${d[3]:.2f}",
                      f"{d[4]:.0f}%", f"${d[5]:.2f}", f"${d[6]:.2f}", f"${d[7]:.2f}"]
                     for d in detalles]
        t_det = Table(enc + filas_det,
                      colWidths=[5.5*cm,1.4*cm,2*cm,1.4*cm,1.2*cm,2*cm,1.5*cm,2.5*cm])
        t_det.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  AZUL),
            ("TEXTCOLOR",     (0,0), (-1,0),  colors.white),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [AZUL_CLARO, colors.white]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#bbccee")),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (0,-1),  8),
        ]))
        elementos.append(t_det)
        elementos.append(Spacer(1, 10))

        # ── TOTALES ───────────────────────────────────────────────────────────
        totales = [
            ["Subtotal IVA 0%:",  f"${float(f.get('subtotal_0',0)):.2f}"],
            ["Subtotal IVA 15%:", f"${float(f.get('subtotal_15',0)):.2f}"],
            ["Descuento:",        f"${float(f.get('descuento_total',0)):.2f}"],
            ["IVA 15%:",          f"${float(f.get('iva_15',0)):.2f}"],
            ["TOTAL A PAGAR:",    f"${float(f.get('total',0)):.2f}"],
        ]
        st_tot  = ParagraphStyle("tot",  parent=styles["Normal"], fontSize=10, textColor=NEGRO)
        st_totb = ParagraphStyle("totb", parent=styles["Normal"], fontSize=11,
                                 fontName="Helvetica-Bold", textColor=colors.white)
        filas_tot = []
        for i, (lab, val) in enumerate(totales):
            if i == len(totales)-1:
                filas_tot.append([Paragraph(f"<b>{lab}</b>", st_totb),
                                   Paragraph(f"<b>{val}</b>", st_totb)])
            else:
                filas_tot.append([Paragraph(lab, st_tot), Paragraph(val, st_tot)])

        t_tot = Table(filas_tot, colWidths=[14*cm, 3.5*cm], hAlign="RIGHT")
        t_tot.setStyle(TableStyle([
            ("ALIGN",         (1,0), (1,-1),  "RIGHT"),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
            ("LINEABOVE",     (0,-1),(-1,-1), 1, AZUL),
            ("BACKGROUND",    (0,-1),(-1,-1), AZUL),
            ("ROWBACKGROUNDS",(0,0), (-1,-2), [GRIS, colors.white]),
        ]))
        elementos.append(t_tot)

        # ── AUTORIZACIÓN SRI ──────────────────────────────────────────────────
        if f.get("numero_autorizacion"):
            elementos.append(Spacer(1, 12))
            elementos.append(HRFlowable(width="100%", thickness=1,
                                        color=colors.HexColor("#aaaaaa"), spaceAfter=6))
            auth_data = [
                [Paragraph("<b>AUTORIZACIÓN SRI</b>",
                    ParagraphStyle("atit", parent=styles["Normal"], fontSize=9,
                                   fontName="Helvetica-Bold", textColor=AZUL)),
                 Paragraph(f.get("numero_autorizacion",""),
                    ParagraphStyle("anum", parent=styles["Normal"], fontSize=9, textColor=NEGRO))],
                [Paragraph("<b>CLAVE DE ACCESO</b>",
                    ParagraphStyle("ctit", parent=styles["Normal"], fontSize=8,
                                   fontName="Helvetica-Bold", textColor=AZUL)),
                 Paragraph(f.get("clave_acceso",""),
                    ParagraphStyle("cval", parent=styles["Normal"], fontSize=7,
                                   textColor=NEGRO))],
            ]
            t_auth = Table(auth_data, colWidths=[4*cm, 13.5*cm])
            t_auth.setStyle(TableStyle([
                ("BACKGROUND",   (0,0),(-1,-1), GRIS),
                ("GRID",         (0,0),(-1,-1), 0.5, colors.HexColor("#dddddd")),
                ("TOPPADDING",   (0,0),(-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
                ("LEFTPADDING",  (0,0),(-1,-1), 8),
                ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
            ]))
            elementos.append(t_auth)

        # ── PIE ───────────────────────────────────────────────────────────────
        elementos.append(Spacer(1, 14))
        elementos.append(HRFlowable(width="100%", thickness=1,
                                    color=colors.HexColor("#cccccc"), spaceAfter=6))
        elementos.append(Paragraph(
            "Documento generado por GymSystem — Software de Control A&D",
            ParagraphStyle("pie", parent=styles["Normal"], fontSize=7,
                           textColor=colors.HexColor("#999999"), alignment=TA_CENTER)))

        doc.build(elementos)
        messagebox.showinfo("PDF generado", f"Factura guardada en:\n{ruta}", parent=parent)
        os.startfile(ruta)

    def generar_pdf_factura():
        sel = tabla_hist.selection()
        if not sel:
            messagebox.showwarning("Sin seleccion",
                "Selecciona una factura del historial.", parent=ventana)
            return
        valores    = tabla_hist.item(sel[0], "values")
        factura_id = int(valores[0])
        _generar_pdf_factura(factura_id, ventana)

    ctk.CTkButton(frame_hist, text="📄 Generar PDF",
                  width=180, height=38, fg_color="#1f6aa5",
                  hover_color="#174f7a", font=("Segoe UI", 12, "bold"),
                  command=generar_pdf_factura).pack(anchor="e", padx=20, pady=(0, 16))

    def cargar_historial():
        for row in tabla_hist.get_children():
            tabla_hist.delete(row)
        con = sqlite3.connect(DB_PATH)
        filas = con.execute("""
            SELECT id, fecha_emision, razon_social, total,
                   estado, numero_autorizacion
            FROM facturas ORDER BY id DESC LIMIT 50
        """).fetchall()
        con.close()
        for f in filas:
            estado = f[4] or "BORRADOR"
            tabla_hist.insert("", "end", values=(
                f[0], f[1], f[2], f"${float(f[3] or 0):.2f}",
                estado, f[5] or "—"
            ), tags=(estado,))

    def _propagar_scroll(widget):
        try:
            widget.bind("<MouseWheel>", lambda e: canvas_p.yview_scroll(
                int(-1 * (e.delta / 120) * 2), "units"))
        except Exception:
            pass
        for hijo in widget.winfo_children():
            _propagar_scroll(hijo)

    ventana.after(200, lambda: _propagar_scroll(scroll))

    cargar_historial()
    actualizar_cards()

# ── CONFIGURACIÓN SRI ─────────────────────────────────────────────────────────

def abrir_config_sri(parent):
    from modulos.rutas import get_db_path
    DB = get_db_path()

    popup = ctk.CTkToplevel(parent)
    popup.title("Configuración SRI")
    popup.geometry("700x820")
    popup.resizable(False, True)
    popup.attributes("-topmost", True)
    popup.after(300, lambda: popup.attributes("-topmost", False))
    popup.lift()
    popup.focus_force()
    popup.grab_set()

    scroll = ctk.CTkScrollableFrame(popup, fg_color="#1e1e2e", width=680, height=800)
    scroll.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(scroll, text="⚙ Configuración SRI",
                 font=("Segoe UI", 24, "bold"), text_color="#cba6f7").pack(pady=(25, 4))
    ctk.CTkLabel(scroll, text="Datos del emisor y certificado digital",
                 font=("Segoe UI", 12), text_color="#6c7086").pack(pady=(0, 16))

    frame = ctk.CTkFrame(scroll, fg_color="#181825", corner_radius=16)
    frame.pack(fill="x", padx=25, pady=5)

    def _seccion(texto):
        ctk.CTkLabel(frame, text=texto, font=("Segoe UI", 12, "bold"),
                     text_color="#89b4fa", anchor="w").pack(fill="x", padx=22, pady=(16, 2))

    def _campo(label, placeholder="", show=""):
        ctk.CTkLabel(frame, text=label, font=("Segoe UI", 11),
                     text_color="#cdd6f4", anchor="w").pack(fill="x", padx=22, pady=(8, 2))
        entrada = ctk.CTkEntry(frame, height=38, placeholder_text=placeholder, show=show)
        entrada.pack(fill="x", padx=22)
        return entrada

    def _fila2(label1, label2, ph1="", ph2=""):
        f = ctk.CTkFrame(frame, fg_color="transparent")
        f.pack(fill="x", padx=22, pady=(8, 0))
        ctk.CTkLabel(f, text=label1, font=("Segoe UI", 11),
                     text_color="#cdd6f4", width=140, anchor="w").pack(side="left")
        e1 = ctk.CTkEntry(f, height=38, placeholder_text=ph1)
        e1.pack(side="left", fill="x", expand=True, padx=(4, 10))
        ctk.CTkLabel(f, text=label2, font=("Segoe UI", 11),
                     text_color="#cdd6f4", width=140, anchor="w").pack(side="left")
        e2 = ctk.CTkEntry(f, height=38, placeholder_text=ph2)
        e2.pack(side="left", fill="x", expand=True, padx=(4, 0))
        return e1, e2

    # ── DATOS DE IDENTIDAD ────────────────────────────────────────────────────
    _seccion("📋 Datos de Identidad")
    e_ap_pat, e_ap_mat = _fila2("Apellido Paterno*", "Apellido Materno", "Ej: GARCÍA", "Ej: LÓPEZ")
    e_p_nom,  e_s_nom  = _fila2("Primer Nombre*",    "Segundo Nombre",   "Ej: JUAN",   "Ej: CARLOS")

    # ── DATOS DE CONTACTO ─────────────────────────────────────────────────────
    _seccion("📞 Datos de Contacto")
    e_correo_e = _campo("Correo Electrónico*", "ejemplo@correo.com")
    e_tel_conv, e_tel_cel = _fila2("Telf. Convencional", "Teléfono Celular*", "022123456", "0991234567")
    e_dir_dom  = _campo("Dirección Domicilio*", "Calle, número, ciudad")

    # ── DATOS DEL NEGOCIO ─────────────────────────────────────────────────────
    _seccion("🏢 Datos del Negocio")
    e_ruc   = _campo("RUC del emisor*",  "Ej: 1714518964001")
    e_razon = _campo("Razón Social*",    "Nombre del gimnasio o contribuyente")

    # ── CERTIFICADO DIGITAL ───────────────────────────────────────────────────
    _seccion("🔐 Certificado Digital")
    ctk.CTkLabel(frame, text="Archivo certificado (.p12)*", font=("Segoe UI", 11),
                 text_color="#cdd6f4", anchor="w").pack(fill="x", padx=22, pady=(8, 2))
    frame_p12 = ctk.CTkFrame(frame, fg_color="transparent")
    frame_p12.pack(fill="x", padx=22)
    e_p12 = ctk.CTkEntry(frame_p12, height=38, placeholder_text="Selecciona el archivo .p12")
    e_p12.pack(side="left", fill="x", expand=True)

    def seleccionar_p12():
        ruta = filedialog.askopenfilename(
            title="Seleccionar certificado .p12",
            filetypes=[("Certificado digital", "*.p12 *.pfx"), ("Todos los archivos", "*.*")],
            parent=popup
        )
        if ruta:
            e_p12.delete(0, "end")
            e_p12.insert(0, ruta)

    ctk.CTkButton(frame_p12, text="📂", width=50, height=38,
                  command=seleccionar_p12).pack(side="left", padx=(8, 0))

    e_clave     = _campo("Contraseña del certificado*", show="*")
    e_clave_sri = _campo("Clave portal SRI (sri.gob.ec)*", show="*")

    # ── CARGAR CONFIG EXISTENTE ───────────────────────────────────────────────
    try:
        con = sqlite3.connect(DB)
        cfg = con.execute("""
            SELECT ruc, razon_social, direccion_matriz, ruta_certificado,
                   clave_certificado, clave_sri,
                   apellido_paterno, apellido_materno, primer_nombre, segundo_nombre,
                   correo_electronico, telefono_conv, telefono_celular, direccion_domicilio
            FROM configuracion_sri WHERE id = 1
        """).fetchone()
        con.close()
        if cfg:
            for entry, val in [
                (e_ruc,      cfg[0]),  (e_razon,    cfg[1]),
                (e_p12,      cfg[3]),  (e_clave,    cfg[4]),
                (e_clave_sri,cfg[5]),  (e_ap_pat,   cfg[6]),
                (e_ap_mat,   cfg[7]),  (e_p_nom,    cfg[8]),
                (e_s_nom,    cfg[9]),  (e_correo_e, cfg[10]),
                (e_tel_conv, cfg[11]), (e_tel_cel,  cfg[12]),
                (e_dir_dom,  cfg[13]),
            ]:
                entry.delete(0, "end")
                entry.insert(0, str(val or ""))
    except Exception:
        pass

    lbl_resultado = ctk.CTkLabel(frame, text="", font=("Segoe UI", 13, "bold"))

    def guardar_config():
        lbl_resultado.configure(text="")
        if not e_ruc.get().strip():
            lbl_resultado.configure(text="❌ Falta el RUC del emisor", text_color="#f38ba8")
            lbl_resultado.pack(pady=(8, 4)); return
        if len(e_ruc.get().strip()) != 13:
            lbl_resultado.configure(text="❌ El RUC debe tener 13 dígitos", text_color="#f38ba8")
            lbl_resultado.pack(pady=(8, 4)); return
        if not e_razon.get().strip():
            lbl_resultado.configure(text="❌ Falta la razón social", text_color="#f38ba8")
            lbl_resultado.pack(pady=(8, 4)); return
        if not e_p12.get().strip() or not os.path.exists(e_p12.get().strip()):
            lbl_resultado.configure(text="❌ Selecciona un archivo .p12 válido", text_color="#f38ba8")
            lbl_resultado.pack(pady=(8, 4)); return
        if not e_clave.get().strip():
            lbl_resultado.configure(text="❌ Falta la clave del certificado", text_color="#f38ba8")
            lbl_resultado.pack(pady=(8, 4)); return
        if not e_clave_sri.get().strip():
            lbl_resultado.configure(text="❌ Falta la clave del portal SRI", text_color="#f38ba8")
            lbl_resultado.pack(pady=(8, 4)); return

        lbl_resultado.configure(text="⏳ Validando certificado...", text_color="#f9e2af")
        lbl_resultado.pack(pady=(8, 4))
        popup.update()

        try:
            from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
            with open(e_p12.get().strip(), "rb") as fp:
                datos_p12 = fp.read()
            load_key_and_certificates(datos_p12, e_clave.get().strip().encode("utf-8"))
        except Exception:
            lbl_resultado.configure(text="❌ Clave incorrecta o certificado inválido", text_color="#f38ba8")
            lbl_resultado.pack(pady=(8, 4)); return

        try:
            con = sqlite3.connect(DB)
            con.execute("""
                INSERT INTO configuracion_sri (
                    id, ruc, razon_social, direccion_matriz,
                    codigo_establecimiento, punto_emision, ambiente,
                    ruta_certificado, clave_certificado, clave_sri,
                    apellido_paterno, apellido_materno, primer_nombre, segundo_nombre,
                    correo_electronico, telefono_conv, telefono_celular, direccion_domicilio
                ) VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                    ruc=excluded.ruc,
                    razon_social=excluded.razon_social,
                    direccion_matriz=excluded.direccion_matriz,
                    codigo_establecimiento=excluded.codigo_establecimiento,
                    punto_emision=excluded.punto_emision,
                    ambiente=excluded.ambiente,
                    ruta_certificado=excluded.ruta_certificado,
                    clave_certificado=excluded.clave_certificado,
                    clave_sri=excluded.clave_sri,
                    apellido_paterno=excluded.apellido_paterno,
                    apellido_materno=excluded.apellido_materno,
                    primer_nombre=excluded.primer_nombre,
                    segundo_nombre=excluded.segundo_nombre,
                    correo_electronico=excluded.correo_electronico,
                    telefono_conv=excluded.telefono_conv,
                    telefono_celular=excluded.telefono_celular,
                    direccion_domicilio=excluded.direccion_domicilio
            """, (
                e_ruc.get().strip(), e_razon.get().strip(), e_dir_dom.get().strip(),
                "001", "001", 2, e_p12.get().strip(),
                e_clave.get().strip(), e_clave_sri.get().strip(),
                e_ap_pat.get().strip(), e_ap_mat.get().strip(),
                e_p_nom.get().strip(), e_s_nom.get().strip(),
                e_correo_e.get().strip(), e_tel_conv.get().strip(),
                e_tel_cel.get().strip(), e_dir_dom.get().strip()
            ))
            con.commit(); con.close()
            lbl_resultado.configure(text="✅ Configuración guardada correctamente", text_color="#a6e3a1")
            lbl_resultado.pack(pady=(8, 4))
        except Exception as ex:
            lbl_resultado.configure(text=f"❌ Error al guardar: {ex}", text_color="#f38ba8")
            lbl_resultado.pack(pady=(8, 4))

    ctk.CTkButton(frame, text="💾 Guardar configuración",
                  height=46, fg_color="#1a4731", hover_color="#166534",
                  font=("Segoe UI", 14, "bold"),
                  command=guardar_config).pack(fill="x", padx=22, pady=(20, 10))

    lbl_resultado.pack(pady=(0, 16))
