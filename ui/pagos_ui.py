import sqlite3
import os, sys

# FIX: reemplazar función _get_db_path local por rutas centralizadas
from modulos.rutas import get_db_path
DB_PATH = get_db_path()

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox

from modulos.pagos import (
    registrar_pago,
    ver_historial_pagos,
    listar_suscripciones_para_pago,
    buscar_cliente_pagos,
    eliminar_pago
)
from modulos.clientes import ver_clientes
from modulos.suscripciones import ver_suscripciones_completas, crear_suscripcion
from modulos.membresias import ver_membresias
from modulos.pdf_generador import generar_pdf_reporte_mensual


def abrir_ventana_pagos(parent):

    ventana = tb.Toplevel(parent)
    ventana.title("Gestión de Pagos")
    ventana.state("zoomed")
    ventana.resizable(True, True)
    ventana.lift()
    ventana.focus_force()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))

    contenedor_principal = tk.Frame(ventana, bg="#1e1e1e")
    contenedor_principal.pack(fill=BOTH, expand=True)

    canvas = tk.Canvas(contenedor_principal, bg="#1e1e1e", highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(contenedor_principal, orient=VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    frame_scroll = tk.Frame(canvas, bg="#1e1e1e")
    window_id = canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

    def actualizar_scrollregion(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def ajustar_ancho_frame(event):
        canvas.itemconfig(window_id, width=event.width)

    frame_scroll.bind("<Configure>", actualizar_scrollregion)
    canvas.bind("<Configure>", ajustar_ancho_frame)

    def _scroll_canvas(event):
        if not canvas.winfo_exists(): return
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind("<MouseWheel>", _scroll_canvas)
    frame_scroll.bind("<MouseWheel>", _scroll_canvas)

    contenedor = tk.Frame(frame_scroll, bg="#1e1e1e", padx=16, pady=16)
    contenedor.pack(fill=BOTH, expand=True)

    def _propagar_scroll(widget):
        if isinstance(widget, ttk.Treeview): return
        widget.bind("<MouseWheel>", _scroll_canvas)
        for hijo in widget.winfo_children():
            _propagar_scroll(hijo)

    style = ttk.Style()
    style.configure("Pagos.Treeview",         font=("Segoe UI", 10), rowheight=35)
    style.configure("Pagos.Treeview.Heading", font=("Segoe UI", 11, "bold"))

    # HEADER
    frame_header = ttk.Frame(contenedor, bootstyle="dark")
    frame_header.pack(fill=X, pady=(6, 14))
    header_inner = ttk.Frame(frame_header, padding=18)
    header_inner.pack(fill=X)
    ttk.Label(header_inner, text="Gestión de Pagos",
              font=("Segoe UI", 24, "bold")).pack(side=LEFT, padx=(8, 18))
    ttk.Label(header_inner,
              text="Administra pagos, consulta historial y crea suscripciones",
              font=("Segoe UI", 11)).pack(side=LEFT)
    ttk.Button(header_inner, text="← Volver al menú",
               bootstyle="secondary", command=ventana.destroy).pack(side=RIGHT, padx=8)

    # TARJETAS
    frame_cards = tk.Frame(contenedor, bg="#1e1e1e")
    frame_cards.pack(fill=X, pady=(0, 14))

    def hacer_card(parent, color, titulo):
        card = tk.Frame(parent, bg=color, height=130)
        card.pack(side=LEFT, fill=X, expand=True, padx=8)
        card.pack_propagate(False)
        tk.Label(card, text=titulo, font=("Segoe UI", 14, "bold"),
                 bg="#1c1c1c", fg="white", padx=10, pady=4).pack(pady=(20, 6))
        lbl = tk.Label(card, text="0", font=("Segoe UI", 30, "bold"),
                       bg="#1c1c1c", fg="white", padx=10, pady=4)
        lbl.pack()
        return lbl

    lbl_total_valor      = hacer_card(frame_cards, "#3b5f86", "Total Suscripciones")
    lbl_total_pagadas    = hacer_card(frame_cards, "#13c29a", "Pagadas")
    lbl_total_pendientes = hacer_card(frame_cards, "#3d9ad6", "Pendientes")
    lbl_total_recaudado  = hacer_card(frame_cards, "#6f42c1", "Total Recaudado ($)")

    # CLIENTES Y SUSCRIPCIONES
    frame_superior = ttk.Frame(contenedor)
    frame_superior.pack(fill=X, pady=8)
    frame_superior.columnconfigure(0, weight=1)
    frame_superior.columnconfigure(1, weight=1)

    frame_clientes = ttk.Labelframe(frame_superior, text="Clientes registrados",
                                    padding=10, bootstyle="primary")
    frame_clientes.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
    frame_cs = ttk.Frame(frame_clientes)
    frame_cs.pack(fill=BOTH, expand=YES)
    tabla_clientes = ttk.Treeview(frame_cs, columns=("ID", "Nombre"),
                                   show="headings", height=6, style="Pagos.Treeview")
    tabla_clientes.heading("ID",     text="ID")
    tabla_clientes.heading("Nombre", text="Nombre")
    tabla_clientes.column("ID",     width=100, anchor="center", minwidth=60)
    tabla_clientes.column("Nombre", width=260, anchor="w",      minwidth=100)
    tabla_clientes.pack(side=LEFT, fill=BOTH, expand=YES)
    sc = ttk.Scrollbar(frame_cs, orient=VERTICAL, command=tabla_clientes.yview)
    sc.pack(side=RIGHT, fill=Y)
    tabla_clientes.configure(yscrollcommand=sc.set)

    frame_sus = ttk.Labelframe(frame_superior, text="Suscripciones registradas",
                                padding=10, bootstyle="success")
    frame_sus.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
    frame_ss = ttk.Frame(frame_sus)
    frame_ss.pack(fill=BOTH, expand=YES)
    tabla_sus = ttk.Treeview(frame_ss, columns=("ID", "Cliente", "Plan"),
                              show="headings", height=6, style="Pagos.Treeview")
    tabla_sus.heading("ID",      text="ID Suscripción")
    tabla_sus.heading("Cliente", text="Cliente")
    tabla_sus.heading("Plan",    text="Plan")
    tabla_sus.column("ID",      anchor="center", width=50,  minwidth=40)
    tabla_sus.column("Cliente", anchor="w",      width=180, minwidth=80)
    tabla_sus.column("Plan",    anchor="w",      width=150, minwidth=80)
    tabla_sus.pack(side=LEFT, fill=BOTH, expand=YES)
    ss = ttk.Scrollbar(frame_ss, orient=VERTICAL, command=tabla_sus.yview)
    ss.pack(side=RIGHT, fill=Y)
    tabla_sus.configure(yscrollcommand=ss.set)

    def _hacer_scroll_local(treeview):
        def _on_enter(e):
            def _scroll_tv(ev):
                treeview.yview_scroll(int(-1 * (ev.delta / 120)), "units")
                return "break"
            ventana.bind("<MouseWheel>", _scroll_tv)
        def _on_leave(e):
            ventana.unbind("<MouseWheel>")
        treeview.bind("<Enter>", _on_enter)
        treeview.bind("<Leave>", _on_leave)

    _hacer_scroll_local(tabla_clientes)
    _hacer_scroll_local(tabla_sus)

    # SELECTOR MES/AÑO
    frame_mes = ttk.Frame(contenedor)
    frame_mes.pack(fill=X, pady=(0, 4))
    ttk.Label(frame_mes, text="Filtrar por:",
              font=("Segoe UI", 12, "bold")).pack(side=LEFT, padx=(0, 10))
    meses = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    combo_mes = ttk.Combobox(frame_mes, values=meses, width=14, state="readonly")
    combo_mes.set("Todos")
    combo_mes.pack(side=LEFT, padx=(0, 8))
    ttk.Label(frame_mes, text="Año:",
              font=("Segoe UI", 12, "bold")).pack(side=LEFT, padx=(0, 6))
    anios = ["Todos"] + [str(a) for a in range(2020, 2101)]
    combo_anio = ttk.Combobox(frame_mes, values=anios, width=10, state="readonly")
    combo_anio.set("Todos")
    combo_anio.pack(side=LEFT, padx=(0, 8))
    lbl_mes_info = ttk.Label(frame_mes, text="", font=("Segoe UI", 10), bootstyle="info")
    lbl_mes_info.pack(side=LEFT, padx=15)

    # TABLA PRINCIPAL
    frame_tabla = ttk.Labelframe(contenedor, text="Detalle de pagos y suscripciones",
                                  padding=10, bootstyle="info")
    frame_tabla.pack(fill=BOTH, expand=True, pady=8)
    columnas = ("ID", "Cliente", "Plan", "Total", "Pagado", "Pendiente",
                "Inicio", "Vence", "Acumulado ($)")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings",
                         height=10, style="Pagos.Treeview")
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120, anchor=CENTER, minwidth=60)
    tabla.column("Cliente",       width=220, anchor=W,      minwidth=100)
    tabla.column("Plan",          width=180, anchor=W,      minwidth=80)
    tabla.column("Acumulado ($)", width=130, anchor=CENTER, minwidth=80)
    tabla.tag_configure("pagado",  background="#b6f2c6", foreground="#0f5132")
    tabla.tag_configure("parcial", background="#fff3cd", foreground="#664d03")
    tabla.tag_configure("deuda",   background="#f8d7da", foreground="#842029")
    scroll_y = ttk.Scrollbar(frame_tabla, orient=VERTICAL,   command=tabla.yview)
    scroll_x = ttk.Scrollbar(frame_tabla, orient=HORIZONTAL, command=tabla.xview)
    tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")
    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)
    _hacer_scroll_local(tabla)

    # PANEL INFERIOR
    frame_inferior = ttk.Frame(contenedor)
    frame_inferior.pack(fill=X, pady=12)
    frame_inferior.grid_columnconfigure(0, weight=1)
    frame_inferior.grid_columnconfigure(1, weight=1)

    frame_buscar = ttk.Labelframe(frame_inferior, text="Buscar / Crear suscripción", padding=12)
    frame_buscar.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
    frame_pago = ttk.Labelframe(frame_inferior, text="Registrar pago", padding=12)
    frame_pago.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

    ttk.Label(frame_buscar, text="Buscar por ID Cliente").grid(row=0, column=0, padx=8, pady=6, sticky=W)
    entry_cliente = ttk.Entry(frame_buscar, width=18)
    entry_cliente.grid(row=0, column=1, padx=8, pady=6, sticky=W)
    ttk.Label(frame_buscar, text="ID Cliente").grid(row=1, column=0, padx=8, pady=6, sticky=W)
    entry_id_cliente = ttk.Entry(frame_buscar, width=18)
    entry_id_cliente.grid(row=1, column=1, padx=8, pady=6, sticky=W)
    ttk.Label(frame_buscar, text="ID Membresía").grid(row=2, column=0, padx=8, pady=6, sticky=W)
    entry_id_membresia = ttk.Entry(frame_buscar, width=18)
    entry_id_membresia.grid(row=2, column=1, padx=8, pady=6, sticky=W)

    ttk.Label(frame_pago, text="ID Suscripción").grid(row=0, column=0, padx=8, pady=6, sticky=W)
    entry_id = ttk.Entry(frame_pago, width=18)
    entry_id.grid(row=0, column=1, padx=8, pady=6, sticky=W)
    ttk.Label(frame_pago, text="Monto pagado").grid(row=1, column=0, padx=8, pady=6, sticky=W)
    entry_monto = ttk.Entry(frame_pago, width=18)
    entry_monto.grid(row=1, column=1, padx=8, pady=6, sticky=W)

    # PANEL CAMBIAR PLAN
    frame_cambiar = ttk.Labelframe(contenedor, text="Cambiar plan del cliente",
                                    padding=12, bootstyle="warning")
    frame_cambiar.pack(fill=X, pady=(0, 8))

    ttk.Label(frame_cambiar, text="ID Suscripcion:").grid(row=0, column=0, padx=8, pady=6, sticky=W)
    entry_sus_cambiar = ttk.Entry(frame_cambiar, width=10)
    entry_sus_cambiar.grid(row=0, column=1, padx=8, pady=6, sticky=W)
    ttk.Label(frame_cambiar, text="Nuevo plan:").grid(row=0, column=2, padx=8, pady=6, sticky=W)
    combo_nuevo_plan = ttk.Combobox(frame_cambiar, width=32, state="readonly")
    combo_nuevo_plan.grid(row=0, column=3, padx=8, pady=6, sticky=W)
    ttk.Label(frame_cambiar, text="Monto pagado:").grid(row=0, column=4, padx=8, pady=6, sticky=W)
    entry_pago_nuevo = ttk.Entry(frame_cambiar, width=10)
    entry_pago_nuevo.grid(row=0, column=5, padx=8, pady=6, sticky=W)
    ttk.Button(frame_cambiar, text="Cambiar Plan", bootstyle="warning",
               width=14, command=lambda: cambiar_plan()).grid(row=0, column=6, padx=10, pady=6)

    ttk.Label(frame_cambiar, text="Fecha inicio (YYYY-MM-DD):").grid(row=1, column=0, padx=8, pady=6, sticky=W)
    entry_fecha_inicio_nuevo = ttk.Entry(frame_cambiar, width=14)
    entry_fecha_inicio_nuevo.grid(row=1, column=1, padx=8, pady=6, sticky=W)
    ttk.Label(frame_cambiar, text="dejar vacio = hoy", foreground="gray").grid(row=1, column=2, padx=4, sticky=W)
    ttk.Label(frame_cambiar, text="Fecha vence (YYYY-MM-DD):").grid(row=1, column=3, padx=8, pady=6, sticky=W)
    entry_fecha_vence_nuevo = ttk.Entry(frame_cambiar, width=14)
    entry_fecha_vence_nuevo.grid(row=1, column=4, padx=8, pady=6, sticky=W)
    ttk.Label(frame_cambiar, text="dejar vacio = auto", foreground="gray").grid(row=1, column=5, padx=4, sticky=W)

    # FUNCIONES
    def cargar_planes_combo():
        planes = ver_membresias()
        combo_nuevo_plan["values"] = [f"{p[0]} — {p[1]} (${float(p[2]):.2f} / {p[3]} dias)" for p in planes]
        combo_nuevo_plan._planes = planes

    def cambiar_plan():
        sus_id_str = entry_sus_cambiar.get().strip()
        sel_plan   = combo_nuevo_plan.current()
        monto_str  = entry_pago_nuevo.get().strip()
        if not sus_id_str or sel_plan < 0 or not monto_str:
            messagebox.showerror("Error", "Completa: ID suscripcion, nuevo plan y monto.", parent=ventana); return
        try:
            sus_id = int(sus_id_str); monto = float(monto_str)
        except ValueError:
            messagebox.showerror("Error", "ID y monto deben ser numeros.", parent=ventana); return

        planes = combo_nuevo_plan._planes; nuevo_plan = planes[sel_plan]
        id_mem_new = nuevo_plan[0]; precio_plan = float(nuevo_plan[2]); duracion = int(nuevo_plan[3])

        if not messagebox.askyesno("Confirmar",
            f"Reemplazar suscripcion #{sus_id} con '{nuevo_plan[1]}'\n"
            f"Precio: ${precio_plan:.2f} | Pagado: ${monto:.2f}\n\nLa anterior sera eliminada.",
            parent=ventana): return

        from datetime import datetime as _dt, timedelta as _td
        hoy = _dt.now()

        fi_raw = entry_fecha_inicio_nuevo.get().strip()
        fecha_inicio = _dt.strptime(fi_raw, "%Y-%m-%d").strftime("%Y-%m-%d") if fi_raw else hoy.strftime("%Y-%m-%d")

        fv_raw = entry_fecha_vence_nuevo.get().strip()
        if fv_raw:
            fecha_vence = _dt.strptime(fv_raw, "%Y-%m-%d").strftime("%Y-%m-%d")
        else:
            fecha_vence = (_dt.strptime(fecha_inicio, "%Y-%m-%d") + _td(days=duracion)).strftime("%Y-%m-%d")

        pendiente = max(0.0, precio_plan - monto)
        con = sqlite3.connect(DB_PATH)
        fila = con.execute("SELECT cliente_id FROM suscripciones WHERE id=?", (sus_id,)).fetchone()
        if not fila:
            con.close()
            messagebox.showerror("Error", "Suscripcion no encontrada.", parent=ventana); return
        cliente_id = fila[0]
        con.execute("DELETE FROM pagos WHERE suscripcion_id=?", (sus_id,))
        con.execute("DELETE FROM suscripciones WHERE id=?", (sus_id,))
        ids_sus = set(r[0] for r in con.execute("SELECT id FROM suscripciones ORDER BY id").fetchall())
        nuevo_sus_id = 1
        while nuevo_sus_id in ids_sus: nuevo_sus_id += 1
        con.execute(
            "INSERT INTO suscripciones (id, cliente_id, membresia_id, fecha_inicio, fecha_vencimiento, precio_total, pagado, pendiente) VALUES (?,?,?,?,?,?,?,?)",
            (nuevo_sus_id, cliente_id, id_mem_new, fecha_inicio, fecha_vence, precio_plan, monto, pendiente))
        if monto > 0:
            con.execute("INSERT INTO pagos (suscripcion_id, monto, fecha_pago) VALUES (?,?,?)",
                        (nuevo_sus_id, monto, fecha_inicio))
        con.commit(); con.close()
        entry_sus_cambiar.delete(0, END); entry_pago_nuevo.delete(0, END)
        entry_fecha_inicio_nuevo.delete(0, END); entry_fecha_vence_nuevo.delete(0, END)
        combo_nuevo_plan.set("")
        cargar_suscripciones(); cargar_suscripciones_lista()
        messagebox.showinfo("Listo", f"Plan actualizado.\nNuevo vencimiento: {fecha_vence}", parent=ventana)

    def _sync_sus_cambiar(sus_id):
        entry_sus_cambiar.delete(0, END)
        entry_sus_cambiar.insert(0, str(sus_id))

    def actualizar_cards(datos=None):
        if datos is None: datos = listar_suscripciones_para_pago()
        total = len(datos); pagadas = 0; pendientes = 0; recaudado = 0.0
        for sus in datos:
            total_pago = float(sus[4]); pagado = float(sus[5])
            pendiente  = max(0.0, float(sus[6])); recaudado += pagado
            if total_pago == 0 and pagado == 0:           pendientes += 1
            elif pagado >= total_pago and total_pago > 0: pagadas    += 1
            else:                                         pendientes += 1
        lbl_total_valor.config(text=str(total))
        lbl_total_pagadas.config(text=str(pagadas))
        lbl_total_pendientes.config(text=str(pendientes))
        lbl_total_recaudado.config(text=f"${recaudado:,.2f}")

    def cargar_clientes():
        for fila in tabla_clientes.get_children(): tabla_clientes.delete(fila)
        for c in ver_clientes(): tabla_clientes.insert("", END, values=(c[0], c[1]))

    def cargar_suscripciones(mes_num=None, anio=None):
        for fila in tabla.get_children(): tabla.delete(fila)
        datos = listar_suscripciones_para_pago()
        if anio:
            datos = [s for s in datos if s[7] and str(s[7]).startswith(str(anio))]
        datos_filtrados = [s for s in datos if s[7] and str(s[7])[5:7] == f"{mes_num:02d}"] if mes_num else datos
        for sus in datos_filtrados:
            cliente = sus[1]; id_suscripcion = sus[2]; plan = sus[3]
            total   = float(sus[4]); pagado = float(sus[5])
            pendiente = max(0.0, float(sus[6])); inicio = sus[7]; vence = sus[8]
            fila = (id_suscripcion, cliente, plan,
                    f"{total:.2f}", f"{pagado:.2f}", f"{pendiente:.2f}",
                    inicio, vence, f"${pagado:.2f}")
            if total == 0 and pagado == 0:      tag = "deuda"
            elif pagado >= total and total > 0: tag = "pagado"
            elif pagado > 0:                    tag = "parcial"
            else:                               tag = "deuda"
            tabla.insert("", END, values=fila, tags=(tag,))
        actualizar_cards(datos_filtrados)
        total_rec = sum(float(s[5]) for s in datos_filtrados)
        n = len(datos_filtrados)
        filtro = []
        if mes_num: filtro.append(meses[mes_num])
        if anio:    filtro.append(str(anio))
        desc = " / ".join(filtro) if filtro else "Todos"
        lbl_mes_info.configure(text=f"{desc}  —  {n} suscripciones  |  Recaudado: ${total_rec:,.2f}")

    def buscar_cliente():
        cliente_id = entry_cliente.get().strip()
        if not cliente_id:
            messagebox.showerror("Error", "Ingrese un ID de cliente", parent=ventana); return
        try: cliente_id = int(cliente_id)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana); return
        datos = buscar_cliente_pagos(cliente_id)
        if not datos:
            messagebox.showinfo("Sin resultados", "El cliente no tiene suscripciones", parent=ventana); return
        for fila in tabla.get_children(): tabla.delete(fila)
        pagadas = pendientes_c = 0; recaudado = 0.0
        for sus in datos:
            id_s, cliente, plan, total, pagado, pendiente, inicio, vence = sus
            total = float(total); pagado = float(pagado)
            pendiente = max(0.0, float(pendiente)); recaudado += pagado
            fila = (id_s, cliente, plan,
                    f"{total:.2f}", f"{pagado:.2f}", f"{pendiente:.2f}",
                    inicio, vence, f"${pagado:.2f}")
            if total == 0 and pagado == 0:         tag = "deuda";   pendientes_c += 1
            elif pagado >= total and total > 0:    tag = "pagado";  pagadas      += 1
            elif pagado > 0:                       tag = "parcial"; pendientes_c += 1
            else:                                  tag = "deuda";   pendientes_c += 1
            tabla.insert("", END, values=fila, tags=(tag,))
        lbl_total_valor.config(text=str(len(datos)))
        lbl_total_pagadas.config(text=str(pagadas))
        lbl_total_pendientes.config(text=str(pendientes_c))
        lbl_total_recaudado.config(text=f"${recaudado:,.2f}")

    def seleccionar_fila(event):
        sel = tabla.selection()
        if not sel: return
        sus_id = tabla.item(sel[0], "values")[0]
        entry_id.delete(0, END); entry_id.insert(0, sus_id)
        _sync_sus_cambiar(sus_id)

    def seleccionar_cliente(event):
        item = tabla_clientes.selection()
        if not item: return
        entry_cliente.delete(0, END)
        entry_cliente.insert(0, tabla_clientes.item(item[0], "values")[0])

    def seleccionar_suscripcion(event):
        item = tabla_sus.selection()
        if not item: return
        entry_id.delete(0, END)
        entry_id.insert(0, tabla_sus.item(item[0], "values")[0])

    def pagar():
        suscripcion = entry_id.get().strip(); monto = entry_monto.get().strip()
        if not suscripcion or not monto:
            messagebox.showerror("Error", "Debes seleccionar una suscripción y escribir el monto", parent=ventana); return
        try: suscripcion = int(suscripcion); monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos", parent=ventana); return
        if monto <= 0:
            messagebox.showerror("Error", "El monto debe ser mayor a 0", parent=ventana); return
        registrar_pago(suscripcion, monto)
        messagebox.showinfo("Pago registrado", "El pago fue registrado correctamente", parent=ventana)
        entry_id.delete(0, END); entry_monto.delete(0, END)
        cargar_suscripciones(); cargar_suscripciones_lista()

    def ver_historial():
        suscripcion = entry_id.get().strip()
        if not suscripcion:
            messagebox.showerror("Error", "Seleccione una suscripción primero", parent=ventana); return
        try: suscripcion = int(suscripcion)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana); return
        historial = ver_historial_pagos(suscripcion)
        if not historial:
            messagebox.showinfo("Historial", "No hay pagos registrados", parent=ventana); return
        vh = tb.Toplevel(ventana)
        vh.title("Historial de Pagos"); vh.geometry("520x350")
        frame_hist = ttk.Frame(vh, padding=10)
        frame_hist.pack(fill=BOTH, expand=True)
        th = ttk.Treeview(frame_hist, columns=("ID Pago", "Monto", "Fecha"),
                          show="headings", style="Pagos.Treeview")
        th.heading("ID Pago", text="ID Pago")
        th.heading("Monto",   text="Monto")
        th.heading("Fecha",   text="Fecha")
        th.column("ID Pago", width=100, anchor=CENTER, minwidth=60)
        th.column("Monto",   width=120, anchor=CENTER, minwidth=60)
        th.column("Fecha",   width=180, anchor=CENTER, minwidth=80)
        th.pack(fill=BOTH, expand=True)
        for pago_id, monto, fecha in historial:
            th.insert("", END, values=(pago_id, monto, fecha))

    def cargar_suscripciones_lista():
        for fila in tabla_sus.get_children(): tabla_sus.delete(fila)
        for sus in ver_suscripciones_completas():
            id_s, cliente, plan, inicio, vence, pagado, deuda = sus
            tabla_sus.insert("", END, values=(id_s, cliente, plan))

    def eliminar_pago_seleccionado():
        suscripcion = entry_id.get().strip()
        if not suscripcion:
            messagebox.showerror("Error", "Selecciona una suscripción", parent=ventana); return
        try: suscripcion = int(suscripcion)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana); return
        historial = ver_historial_pagos(suscripcion)
        if not historial:
            messagebox.showinfo("Información", "No hay pagos para eliminar", parent=ventana); return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el último pago?", parent=ventana): return
        eliminar_pago(historial[-1][0])
        messagebox.showinfo("Pago eliminado", "El pago fue eliminado", parent=ventana)
        cargar_suscripciones(); cargar_suscripciones_lista()

    def crear_suscripcion_rapida():
        cliente = entry_id_cliente.get().strip(); membresia = entry_id_membresia.get().strip()
        if not cliente or not membresia:
            messagebox.showerror("Error", "Debes ingresar cliente y membresía", parent=ventana); return
        try: cliente = int(cliente); membresia = int(membresia)
        except ValueError:
            messagebox.showerror("Error", "IDs inválidos", parent=ventana); return
        crear_suscripcion(cliente, membresia)
        messagebox.showinfo("Éxito", "Suscripción creada", parent=ventana)
        cargar_suscripciones(); cargar_suscripciones_lista()

    def resetear_pago():
        suscripcion = entry_id.get().strip()
        if not suscripcion:
            messagebox.showerror("Error", "Selecciona una suscripcion primero", parent=ventana); return
        try: suscripcion = int(suscripcion)
        except ValueError:
            messagebox.showerror("Error", "ID invalido", parent=ventana); return
        if not messagebox.askyesno("Confirmar",
            "Esto pondra el monto pagado en $0 y eliminara el historial de pagos.\n¿Continuar?",
            parent=ventana): return
        con = sqlite3.connect(DB_PATH)
        con.execute("UPDATE suscripciones SET pagado=0, pendiente=precio_total WHERE id=?", (suscripcion,))
        con.execute("DELETE FROM pagos WHERE suscripcion_id=?", (suscripcion,))
        con.commit(); con.close()
        messagebox.showinfo("Listo", "Pago reiniciado a $0 correctamente.", parent=ventana)
        cargar_suscripciones(); cargar_suscripciones_lista()

    # EVENTOS
    def on_mes_change(event=None):
        sel_mes  = combo_mes.get(); sel_anio = combo_anio.get()
        mes_num  = meses.index(sel_mes) if sel_mes != "Todos" else None
        anio     = int(sel_anio) if sel_anio != "Todos" else None
        cargar_suscripciones(mes_num, anio)

    combo_mes.bind("<<ComboboxSelected>>",  on_mes_change)
    combo_anio.bind("<<ComboboxSelected>>", on_mes_change)
    tabla.bind("<<TreeviewSelect>>",          seleccionar_fila)
    tabla_clientes.bind("<<TreeviewSelect>>", seleccionar_cliente)
    tabla_sus.bind("<<TreeviewSelect>>",      seleccionar_suscripcion)

    # BOTONES
    frame_botones = ttk.Frame(contenedor)
    frame_botones.pack(fill=X, pady=12)

    ttk.Button(frame_botones, text="Buscar",            bootstyle="info",      width=12, command=buscar_cliente).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Crear Suscripción", bootstyle="primary",   width=16, command=crear_suscripcion_rapida).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Registrar Pago",    bootstyle="success",   width=14, command=pagar).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Ver Historial",     bootstyle="warning",   width=14, command=ver_historial).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Eliminar Pago",     bootstyle="danger",    width=14, command=eliminar_pago_seleccionado).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Poner Pago en $0",  bootstyle="warning",   width=16, command=resetear_pago).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="📊 Reporte PDF",    bootstyle="info",      width=16,
               command=lambda: generar_pdf_reporte_mensual(
                   ventana,
                   meses.index(combo_mes.get()) if combo_mes.get() != "Todos" else None,
                   int(combo_anio.get()) if combo_anio.get() != "Todos" else None
               )).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Actualizar",        bootstyle="secondary", width=12,
               command=lambda: [cargar_clientes(), on_mes_change(),
                                cargar_suscripciones_lista()]).pack(side="right", padx=4)

    # CARGA INICIAL
    cargar_clientes()
    cargar_suscripciones()
    cargar_suscripciones_lista()
    cargar_planes_combo()
    ventana.after(100, lambda: _propagar_scroll(contenedor))