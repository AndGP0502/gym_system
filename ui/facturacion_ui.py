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
    ventana.state("zoomed")
    ventana.resizable(True, True)
    ventana.attributes("-topmost", True)
    ventana.after(300, lambda: ventana.attributes("-topmost", False))
    ventana.lift()
    ventana.focus_force()

    # ── Scroll principal ──────────────────────────────────────────────────────
    canvas_p = tk.Canvas(ventana, highlightthickness=0, bg="#1e1e2e")
    sb_p     = ttk.Scrollbar(ventana, orient="vertical", command=canvas_p.yview)
    canvas_p.configure(yscrollcommand=sb_p.set)
    sb_p.pack(side="right", fill="y")
    canvas_p.pack(side="left", fill="both", expand=True)

    scroll = ctk.CTkFrame(canvas_p, fg_color="#1e1e2e")
    sid    = canvas_p.create_window((0, 0), window=scroll, anchor="nw")

    scroll.bind("<Configure>", lambda e: canvas_p.configure(
        scrollregion=canvas_p.bbox("all")))
    canvas_p.bind("<Configure>", lambda e: canvas_p.itemconfig(sid, width=e.width))
    canvas_p.bind("<MouseWheel>", lambda e: canvas_p.yview_scroll(
        int(-1 * (e.delta / 120)), "units"))

    # ── HEADER ────────────────────────────────────────────────────────────────
    header = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    header.pack(fill="x", padx=20, pady=(20, 10))

    ctk.CTkLabel(header, text="🧾 Facturación Electrónica",
                 font=("Segoe UI", 26, "bold"),
                 text_color="#cba6f7").pack(side="left", padx=20, pady=18)
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

    # ── TARJETAS RESUMEN ──────────────────────────────────────────────────────
    frame_cards = ctk.CTkFrame(scroll, fg_color="transparent")
    frame_cards.pack(fill="x", padx=20, pady=10)

    lbl_emitidas = lbl_autorizadas = lbl_mes = lbl_total_mes = None

    def _card(parent, color, icono, titulo, col):
        f = ctk.CTkFrame(parent, corner_radius=14, fg_color=color, height=100)
        f.grid(row=0, column=col, padx=8, sticky="ew")
        f.grid_propagate(False)
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(f, text=icono, font=("Segoe UI", 24)).pack(pady=(12, 2))
        ctk.CTkLabel(f, text=titulo, font=("Segoe UI", 11),
                     text_color="#cdd6f4").pack()
        lbl = ctk.CTkLabel(f, text="0", font=("Segoe UI", 22, "bold"),
                           text_color="white")
        lbl.pack(pady=(2, 10))
        return lbl

    lbl_emitidas   = _card(frame_cards, "#1e3a5f", "📄", "Emitidas hoy",     0)
    lbl_autorizadas= _card(frame_cards, "#1a4731", "✅", "Autorizadas",       1)
    lbl_mes        = _card(frame_cards, "#3d1f5c", "📅", "Este mes",          2)
    lbl_total_mes  = _card(frame_cards, "#4a1c1c", "💰", "Recaudado ($)",     3)

    def actualizar_cards():
        con = sqlite3.connect(DB_PATH)
        hoy = datetime.now().strftime("%Y-%m-%d")
        mes = datetime.now().strftime("%Y-%m")
        e  = con.execute("SELECT COUNT(*) FROM facturas WHERE fecha_emision=?", (hoy,)).fetchone()[0]
        a  = con.execute("SELECT COUNT(*) FROM facturas WHERE estado='AUTORIZADO'").fetchone()[0]
        m  = con.execute("SELECT COUNT(*) FROM facturas WHERE fecha_emision LIKE ?", (f"{mes}%",)).fetchone()[0]
        t  = con.execute("SELECT COALESCE(SUM(total),0) FROM facturas WHERE fecha_emision LIKE ? AND estado='AUTORIZADO'", (f"{mes}%",)).fetchone()[0]
        con.close()
        lbl_emitidas.configure(text=str(e))
        lbl_autorizadas.configure(text=str(a))
        lbl_mes.configure(text=str(m))
        lbl_total_mes.configure(text=f"${t:,.2f}")

    # ── FORMULARIO EMISIÓN ────────────────────────────────────────────────────
    frame_form = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_form.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_form, text="Nueva Factura",
                 font=("Segoe UI", 18, "bold"),
                 text_color="#89b4fa").pack(anchor="w", padx=20, pady=(16, 4))
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
                 font=("Segoe UI", 12), text_color="#cdd6f4").grid(
        row=2, column=2, sticky="w", padx=8)
    combo_tipo_id.grid(row=3, column=2, padx=8, pady=(2, 10), sticky="w")
    combo_tipo_id.set("05 - Cédula")

    # Autocompletado desde BD
    def buscar_cliente_por_id(event=None):
        cedula = entry_id.get().strip()
        if len(cedula) < 5:
            return
        con = sqlite3.connect(DB_PATH)
        c = con.execute(
            "SELECT nombre, telefono FROM clientes WHERE cedula=? LIMIT 1",
            (cedula,)
        ).fetchone()
        con.close()
        if c:
            entry_nombre.delete(0, "end"); entry_nombre.insert(0, c[0])
            entry_telefono.delete(0, "end"); entry_telefono.insert(0, c[1] or "")

    entry_id.bind("<FocusOut>", buscar_cliente_por_id)

    # ── DETALLE DE FACTURA ────────────────────────────────────────────────────
    frame_detalle = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_detalle.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_detalle, text="Detalle de Servicios",
                 font=("Segoe UI", 18, "bold"),
                 text_color="#89b4fa").pack(anchor="w", padx=20, pady=(16, 4))

    # Fila de entrada de items
    frame_item = ctk.CTkFrame(frame_detalle, fg_color="#313244", corner_radius=10)
    frame_item.pack(fill="x", padx=20, pady=(0, 10))

    ctk.CTkLabel(frame_item, text="Descripción",
                 font=("Segoe UI", 11), text_color="#cdd6f4").grid(
        row=0, column=0, padx=8, pady=(8,2), sticky="w")
    entry_desc = ctk.CTkEntry(frame_item, width=280, height=34)
    entry_desc.grid(row=1, column=0, padx=8, pady=(0,10))

    ctk.CTkLabel(frame_item, text="Cantidad",
                 font=("Segoe UI", 11), text_color="#cdd6f4").grid(
        row=0, column=1, padx=8, pady=(8,2), sticky="w")
    entry_cant = ctk.CTkEntry(frame_item, width=80, height=34)
    entry_cant.insert(0, "1")
    entry_cant.grid(row=1, column=1, padx=8, pady=(0,10))

    ctk.CTkLabel(frame_item, text="Precio Unit.",
                 font=("Segoe UI", 11), text_color="#cdd6f4").grid(
        row=0, column=2, padx=8, pady=(8,2), sticky="w")
    entry_precio = ctk.CTkEntry(frame_item, width=100, height=34)
    entry_precio.grid(row=1, column=2, padx=8, pady=(0,10))

    ctk.CTkLabel(frame_item, text="Descuento",
                 font=("Segoe UI", 11), text_color="#cdd6f4").grid(
        row=0, column=3, padx=8, pady=(8,2), sticky="w")
    entry_desc_val = ctk.CTkEntry(frame_item, width=80, height=34)
    entry_desc_val.insert(0, "0")
    entry_desc_val.grid(row=1, column=3, padx=8, pady=(0,10))

    ctk.CTkLabel(frame_item, text="IVA",
                 font=("Segoe UI", 11), text_color="#cdd6f4").grid(
        row=0, column=4, padx=8, pady=(8,2), sticky="w")
    combo_iva = ctk.CTkComboBox(frame_item, width=100,
                                values=["15%", "0%"], state="readonly")
    combo_iva.set("15%")
    combo_iva.grid(row=1, column=4, padx=8, pady=(0,10))

    ctk.CTkButton(frame_item, text="+ Agregar", width=110, height=34,
                  fg_color="#1e3a5f", hover_color="#2d5a8e",
                  font=("Segoe UI", 12, "bold"),
                  command=lambda: agregar_item()).grid(
        row=1, column=5, padx=12, pady=(0,10))

    # Tabla de items
    style = ttk.Style()
    style.configure("Fact.Treeview",         font=("Segoe UI", 10), rowheight=30)
    style.configure("Fact.Treeview.Heading", font=("Segoe UI", 10, "bold"))

    cols_tabla = ("Descripción", "Cant.", "Precio", "Desc.", "IVA%", "Subtotal", "IVA", "Total")
    tabla_items = ttk.Treeview(frame_detalle, columns=cols_tabla,
                               show="headings", height=6, style="Fact.Treeview")
    for col in cols_tabla:
        tabla_items.heading(col, text=col)
        tabla_items.column(col, width=110, anchor="center", minwidth=60)
    tabla_items.column("Descripción", width=220, anchor="w")
    tabla_items.pack(fill="x", padx=20, pady=(0, 6))

    ctk.CTkButton(frame_detalle, text="🗑 Eliminar seleccionado",
                  width=180, height=32, fg_color="#4a1c1c",
                  hover_color="#7f1d1d", font=("Segoe UI", 11),
                  command=lambda: eliminar_item()).pack(anchor="e", padx=20, pady=(0, 12))

    items = []  # lista de dicts con los items agregados

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
            item = {
                "descripcion":    desc,
                "cantidad":       cant,
                "precio_unitario":precio,
                "descuento":      desc_v,
                "porcentaje_iva": pct_iva,
                "subtotal":       subtotal,
                "iva":            iva,
                "total":          total,
            }
            items.append(item)
            tabla_items.insert("", "end", values=(
                desc, cant, f"${precio:.2f}", f"${desc_v:.2f}",
                f"{pct_iva:.0f}%", f"${subtotal:.2f}",
                f"${iva:.2f}", f"${total:.2f}"
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

    lbl_sub0    = _tot_row("Subtotal IVA 0%:")
    lbl_sub15   = _tot_row("Subtotal IVA 15%:")
    lbl_desc    = _tot_row("Descuento total:")
    lbl_iva15   = _tot_row("IVA 15%:")
    lbl_total   = _tot_row("TOTAL:", bold=True)

    def calcular_totales():
        sub0  = sum(i["subtotal"] for i in items if i["porcentaje_iva"] == 0)
        sub15 = sum(i["subtotal"] for i in items if i["porcentaje_iva"] == 15)
        desc  = sum(i["descuento"] * i["cantidad"] for i in items)
        iva15 = sum(i["iva"]      for i in items if i["porcentaje_iva"] == 15)
        tot   = sub0 + sub15 + iva15
        lbl_sub0.configure(text=f"${sub0:.2f}")
        lbl_sub15.configure(text=f"${sub15:.2f}")
        lbl_desc.configure(text=f"${desc:.2f}")
        lbl_iva15.configure(text=f"${iva15:.2f}")
        lbl_total.configure(text=f"${tot:.2f}")

    # ── BOTONES DE ACCIÓN ─────────────────────────────────────────────────────
    frame_acciones = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_acciones.pack(fill="x", padx=20, pady=(10, 20))

    frame_btns = ctk.CTkFrame(frame_acciones, fg_color="transparent")
    frame_btns.pack(pady=16, padx=20)

    def _btn(texto, color, hover, cmd):
        return ctk.CTkButton(frame_btns, text=texto, width=170, height=44,
                             fg_color=color, hover_color=hover,
                             font=("Segoe UI", 13, "bold"),
                             command=cmd)

    def guardar_borrador():
        if not items:
            messagebox.showwarning("Sin items", "Agrega al menos un servicio.", parent=ventana)
            return
        config = obtener_config_sri()
        if not config:
            messagebox.showerror("Sin configuración",
                "Configura los datos del SRI primero.", parent=ventana)
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
        if not config:
            messagebox.showerror("Sin configuración",
                "Configura los datos del SRI primero.", parent=ventana)
            return
        if not config.get("ruta_certificado") or not os.path.exists(config["ruta_certificado"]):
            messagebox.showerror("Sin certificado",
                "Configura la ruta al archivo .p12 en la configuración SRI.", parent=ventana)
            return

        factura = _construir_factura(config)
        fid     = guardar_factura(factura, items)

        messagebox.showinfo("Procesando",
            "Enviando al SRI...\nEsto puede tomar unos segundos.", parent=ventana)

        resultado = procesar_factura_completa(fid)

        if resultado["ok"]:
            messagebox.showinfo("✅ Autorizada",
                f"Factura AUTORIZADA\n\n"
                f"Clave de acceso: {resultado['clave_acceso']}\n"
                f"Autorización: {resultado['numero_autorizacion']}",
                parent=ventana)
            limpiar_formulario()
        else:
            messagebox.showerror("❌ Error SRI",
                f"Estado: {resultado.get('estado', 'ERROR')}\n"
                f"{resultado.get('error', '')}",
                parent=ventana)

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
            "establecimiento":     config["codigo_establecimiento"],
            "punto_emision":       config["punto_emision"],
            "secuencial":          str(config["siguiente_secuencial"]).zfill(9),
            "ambiente":            config["ambiente"],
            "ruc_emisor":          config["ruc"],
            "razon_social_emisor": config["razon_social"],
        }

    def limpiar_formulario():
        for e in [entry_id, entry_nombre, entry_correo,
                  entry_telefono, entry_direccion]:
            e.delete(0, "end")
        for row in tabla_items.get_children():
            tabla_items.delete(row)
        items.clear()
        calcular_totales()

    _btn("💾 Guardar Borrador", "#1e3a5f", "#2d5a8e", guardar_borrador).pack(side="left", padx=8)
    _btn("🚀 Emitir al SRI",    "#1a4731", "#166534", emitir_factura).pack(side="left", padx=8)
    _btn("🗑 Limpiar",          "#3d1f00", "#78350f", limpiar_formulario).pack(side="left", padx=8)

    # ── HISTORIAL ─────────────────────────────────────────────────────────────
    frame_hist = ctk.CTkFrame(scroll, corner_radius=16, fg_color="#181825")
    frame_hist.pack(fill="x", padx=20, pady=(0, 20))

    ctk.CTkLabel(frame_hist, text="Historial de Facturas",
                 font=("Segoe UI", 18, "bold"),
                 text_color="#89b4fa").pack(anchor="w", padx=20, pady=(16, 8))

    cols_h = ("ID", "Fecha", "Cliente", "Total", "Estado", "Autorización")
    tabla_hist = ttk.Treeview(frame_hist, columns=cols_h,
                              show="headings", height=8, style="Fact.Treeview")
    for col in cols_h:
        tabla_hist.heading(col, text=col)
        tabla_hist.column(col, width=130, anchor="center", minwidth=60)
    tabla_hist.column("Cliente",       width=220, anchor="w")
    tabla_hist.column("Autorización",  width=180, anchor="center")

    tabla_hist.tag_configure("AUTORIZADO", foreground="#a6e3a1")
    tabla_hist.tag_configure("RECHAZADA",  foreground="#f38ba8")
    tabla_hist.tag_configure("PENDIENTE",  foreground="#f9e2af")
    tabla_hist.tag_configure("BORRADOR",   foreground="#89b4fa")

    sb_hist = ttk.Scrollbar(frame_hist, orient="vertical", command=tabla_hist.yview)
    tabla_hist.configure(yscrollcommand=sb_hist.set)
    tabla_hist.pack(side="left", fill="x", expand=True, padx=(20, 0), pady=(0, 16))
    sb_hist.pack(side="right", fill="y", pady=(0, 16), padx=(0, 10))

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

    cargar_historial()
    actualizar_cards()


# ── VENTANA CONFIGURACIÓN SRI ─────────────────────────────────────────────────

def abrir_config_sri(parent):
    from modulos.rutas import get_db_path
    DB = get_db_path()

    popup = ctk.CTkToplevel(parent)
    popup.title("Configuración SRI")
    popup.geometry("620x780")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.after(300, lambda: popup.attributes("-topmost", False))
    popup.lift(); popup.focus_force()

    ctk.CTkLabel(popup, text="⚙ Configuración SRI Ecuador",
                 font=("Segoe UI", 18, "bold"),
                 text_color="#cba6f7").pack(pady=(20, 4))
    ctk.CTkLabel(popup, text="Datos del emisor y certificado digital",
                 font=("Segoe UI", 11), text_color="#6c7086").pack(pady=(0, 16))

    frame = ctk.CTkScrollableFrame(popup, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=20)

    def _campo(label, row, placeholder=""):
        ctk.CTkLabel(frame, text=label, font=("Segoe UI", 12),
                     text_color="#cdd6f4").grid(row=row*2, column=0, sticky="w", pady=(6,0))
        e = ctk.CTkEntry(frame, width=480, height=36, placeholder_text=placeholder)
        e.grid(row=row*2+1, column=0, pady=(2, 4))
        return e

    e_ruc          = _campo("RUC del emisor",             0, "1234567890001")
    e_razon        = _campo("Razón social",                1, "NOMBRE DEL GIMNASIO")
    e_comercial    = _campo("Nombre comercial",            2, "FIVGYM")
    e_dir_matriz   = _campo("Dirección matriz",            3)
    e_dir_sucursal = _campo("Dirección sucursal",          4)
    e_estab        = _campo("Código establecimiento",      5, "001")
    e_pto          = _campo("Punto de emisión",            6, "001")
    e_correo       = _campo("Correo remitente",            7)
    e_smtp         = _campo("SMTP host",                   8, "smtp.gmail.com")
    e_smtp_port    = _campo("SMTP puerto",                 9, "587")
    e_smtp_user    = _campo("SMTP usuario",               10)
    e_smtp_pass    = _campo("SMTP contraseña",            11)

    # Ambiente
    ctk.CTkLabel(frame, text="Ambiente", font=("Segoe UI", 12),
                 text_color="#cdd6f4").grid(row=24, column=0, sticky="w", pady=(6,0))
    combo_amb = ctk.CTkComboBox(frame, width=480,
                                values=["1 - Pruebas", "2 - Producción"],
                                state="readonly")
    combo_amb.set("2 - Producción")
    combo_amb.grid(row=25, column=0, pady=(2, 4))

    # Certificado .p12
    ctk.CTkLabel(frame, text="Archivo certificado (.p12)",
                 font=("Segoe UI", 12), text_color="#cdd6f4").grid(
        row=26, column=0, sticky="w", pady=(6,0))
    frame_p12 = ctk.CTkFrame(frame, fg_color="transparent")
    frame_p12.grid(row=27, column=0, pady=(2,4), sticky="w")
    e_p12 = ctk.CTkEntry(frame_p12, width=380, height=36)
    e_p12.pack(side="left")
    ctk.CTkButton(frame_p12, text="📂", width=50, height=36,
                  command=lambda: [e_p12.delete(0,"end"),
                                   e_p12.insert(0, filedialog.askopenfilename(
                                       filetypes=[("Certificado", "*.p12 *.pfx")],
                                       parent=popup) or "")]
                  ).pack(side="left", padx=4)

    e_clave_p12 = _campo("Contraseña del certificado", 14)
    e_clave_p12.configure(show="*")

    # Cargar config existente
    con = sqlite3.connect(DB)
    cfg = con.execute("SELECT * FROM configuracion_sri WHERE id=1").fetchone()
    con.close()

    if cfg:
        cols = ["id","ruc","razon_social","nombre_comercial","direccion_matriz",
                "direccion_sucursal","codigo_establecimiento","punto_emision",
                "ambiente","tipo_emision","ruta_certificado","clave_certificado",
                "siguiente_secuencial","correo_remitente","smtp_host","smtp_port",
                "smtp_usuario","smtp_clave","ruta_xmls","ruta_rides"]
        d = dict(zip(cols, cfg))
        for entry, key in [
            (e_ruc, "ruc"), (e_razon, "razon_social"),
            (e_comercial, "nombre_comercial"), (e_dir_matriz, "direccion_matriz"),
            (e_dir_sucursal, "direccion_sucursal"),
            (e_estab, "codigo_establecimiento"), (e_pto, "punto_emision"),
            (e_correo, "correo_remitente"), (e_smtp, "smtp_host"),
            (e_smtp_port, "smtp_port"), (e_smtp_user, "smtp_usuario"),
            (e_smtp_pass, "smtp_clave"), (e_p12, "ruta_certificado"),
            (e_clave_p12, "clave_certificado"),
        ]:
            entry.delete(0, "end")
            entry.insert(0, str(d.get(key, "") or ""))
        amb = d.get("ambiente", 2)
        combo_amb.set("1 - Pruebas" if amb == 1 else "2 - Producción")

    def guardar_config():
        amb = 1 if combo_amb.get().startswith("1") else 2
        con = sqlite3.connect(DB)
        con.execute("""
            INSERT INTO configuracion_sri (
                id, ruc, razon_social, nombre_comercial,
                direccion_matriz, direccion_sucursal,
                codigo_establecimiento, punto_emision, ambiente,
                ruta_certificado, clave_certificado,
                correo_remitente, smtp_host, smtp_port,
                smtp_usuario, smtp_clave
            ) VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                ruc=excluded.ruc,
                razon_social=excluded.razon_social,
                nombre_comercial=excluded.nombre_comercial,
                direccion_matriz=excluded.direccion_matriz,
                direccion_sucursal=excluded.direccion_sucursal,
                codigo_establecimiento=excluded.codigo_establecimiento,
                punto_emision=excluded.punto_emision,
                ambiente=excluded.ambiente,
                ruta_certificado=excluded.ruta_certificado,
                clave_certificado=excluded.clave_certificado,
                correo_remitente=excluded.correo_remitente,
                smtp_host=excluded.smtp_host,
                smtp_port=excluded.smtp_port,
                smtp_usuario=excluded.smtp_usuario,
                smtp_clave=excluded.smtp_clave
        """, (
            e_ruc.get().strip(), e_razon.get().strip(),
            e_comercial.get().strip(), e_dir_matriz.get().strip(),
            e_dir_sucursal.get().strip(), e_estab.get().strip() or "001",
            e_pto.get().strip() or "001", amb,
            e_p12.get().strip(), e_clave_p12.get().strip(),
            e_correo.get().strip(), e_smtp.get().strip(),
            int(e_smtp_port.get() or 587), e_smtp_user.get().strip(),
            e_smtp_pass.get().strip()
        ))
        con.commit(); con.close()
        messagebox.showinfo("Guardado", "Configuración SRI guardada correctamente.", parent=popup)
        popup.destroy()

    ctk.CTkButton(frame, text="💾 Guardar configuración",
                  width=480, height=42, fg_color="#1a4731",
                  hover_color="#166534", font=("Segoe UI", 13, "bold"),
                  command=guardar_config).grid(row=30, column=0, pady=20)