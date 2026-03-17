import sqlite3
from datetime import datetime, timedelta
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "gym.db")


def _con():
    """Devuelve siempre una conexión a la BD correcta."""
    return sqlite3.connect(DB_PATH)


# -------- ASIGNAR MEMBRESIA A CLIENTE --------

def asignar_membresia(cliente_id, membresia_id, precio_total, pagado, fecha_inicio=None):
    """
    Asigna una membresía a un cliente.
    fecha_inicio puede ser:
      - None  → se usa datetime.now() automáticamente
      - str   → fecha en formato YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY
    """
    con = _con()
    cur = con.cursor()

    cur.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,))
    if cur.fetchone() is None:
        con.close()
        print("El cliente no existe")
        return

    cur.execute("SELECT id, duracion_dias FROM membresias WHERE id = ?", (membresia_id,))
    resultado = cur.fetchone()
    if resultado is None:
        con.close()
        print("La membresía no existe")
        return

    duracion = resultado[1]

    if fecha_inicio is None:
        fecha_inicio_dt = datetime.now()
    else:
        fecha_inicio_dt = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio.strip(), fmt)
                break
            except ValueError:
                continue
        if fecha_inicio_dt is None:
            con.close()
            print(f"Formato de fecha invalido: '{fecha_inicio}'. Use YYYY-MM-DD o DD/MM/YYYY")
            return

    fecha_inicio_str  = fecha_inicio_dt.strftime("%Y-%m-%d")
    fecha_vencimiento = (fecha_inicio_dt + timedelta(days=duracion)).strftime("%Y-%m-%d")
    pendiente         = max(0, precio_total - pagado)

    cur.execute("""
        INSERT INTO suscripciones(
            cliente_id, membresia_id, fecha_inicio, fecha_vencimiento,
            precio_total, pagado, pendiente
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cliente_id, membresia_id, fecha_inicio_str, fecha_vencimiento,
          precio_total, pagado, pendiente))

    con.commit()
    con.close()
    print("Membresía asignada correctamente")


# -------- VER SUSCRIPCIONES --------
def ver_suscripciones():
    con = _con()
    cur = con.cursor()
    cur.execute("SELECT * FROM suscripciones")
    datos = cur.fetchall()
    con.close()
    return datos


# -------- ESTADO GENERAL DEL GIMNASIO --------
def ver_estado_gimnasio():
    con = _con()
    cur = con.cursor()
    cur.execute("""
        SELECT suscripciones.id,
               clientes.nombre,
               membresias.nombre_plan,
               suscripciones.fecha_vencimiento,
               suscripciones.pagado,
               suscripciones.pendiente
        FROM suscripciones
        JOIN clientes   ON suscripciones.cliente_id   = clientes.id
        JOIN membresias ON suscripciones.membresia_id = membresias.id
    """)
    datos = cur.fetchall()
    con.close()
    return datos


# -------- CLIENTES VENCIDOS --------
def ver_clientes_vencidos():
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT clientes.nombre, suscripciones.fecha_vencimiento
        FROM suscripciones
        JOIN clientes ON suscripciones.cliente_id = clientes.id
        WHERE suscripciones.fecha_vencimiento < ?
    """, (hoy,))
    datos = cur.fetchall()
    con.close()
    return datos


# -------- REGISTRAR PAGO --------
def registrar_pago(suscripcion_id, monto):
    con = _con()
    cur = con.cursor()

    cur.execute("SELECT precio_total, pagado FROM suscripciones WHERE id = ?", (suscripcion_id,))
    datos = cur.fetchone()

    if datos is None:
        con.close()
        print("La suscripción no existe")
        return

    if monto <= 0:
        con.close()
        print("Monto inválido")
        return

    precio_total, pagado_actual = datos
    nuevo_pagado = min(pagado_actual + monto, precio_total)
    pendiente    = precio_total - nuevo_pagado

    cur.execute("""
        UPDATE suscripciones SET pagado = ?, pendiente = ? WHERE id = ?
    """, (nuevo_pagado, pendiente, suscripcion_id))

    con.commit()
    con.close()
    print("Pago registrado correctamente")


# -------- DIAS RESTANTES --------
def ver_dias_restantes():
    con = _con()
    cur = con.cursor()
    cur.execute("""
        SELECT clientes.nombre, membresias.nombre_plan, suscripciones.fecha_vencimiento
        FROM suscripciones
        JOIN clientes   ON suscripciones.cliente_id   = clientes.id
        JOIN membresias ON suscripciones.membresia_id = membresias.id
    """)
    datos = cur.fetchall()
    con.close()

    hoy = datetime.now()
    resultados = []
    for nombre, plan, fecha_vencimiento in datos:
        fecha_v        = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        dias_restantes = (fecha_v - hoy).days
        estado         = "VENCIDO" if dias_restantes < 0 else f"{dias_restantes} dias"
        resultados.append((nombre, plan, estado))
    return resultados


# -------- CLIENTES POR VENCER --------
def clientes_por_vencer():
    con = _con()
    cur = con.cursor()
    hoy = datetime.now()
    cur.execute("""
        SELECT clientes.nombre, suscripciones.fecha_vencimiento
        FROM suscripciones
        JOIN clientes ON suscripciones.cliente_id = clientes.id
    """)
    datos = cur.fetchall()
    con.close()

    resultados = []
    for nombre, fecha_vencimiento in datos:
        fecha_v        = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        dias_restantes = (fecha_v - hoy).days
        if 0 <= dias_restantes <= 5:
            resultados.append((nombre, dias_restantes))
    return resultados


# -------- VER SUSCRIPCIONES COMPLETAS --------
def ver_suscripciones_completas():
    con = _con()
    cur = con.cursor()
    cur.execute("""
        SELECT suscripciones.id,
               clientes.nombre,
               membresias.nombre_plan,
               suscripciones.fecha_inicio,
               suscripciones.fecha_vencimiento,
               suscripciones.pagado,
               suscripciones.pendiente
        FROM suscripciones
        JOIN clientes   ON suscripciones.cliente_id   = clientes.id
        JOIN membresias ON suscripciones.membresia_id = membresias.id
    """)
    datos = cur.fetchall()
    con.close()
    return datos


# -------- CONTAR SUSCRIPCIONES VENCIDAS --------
def contar_suscripciones_vencidas():
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM suscripciones WHERE fecha_vencimiento < ?", (hoy,))
    total = cur.fetchone()[0]
    con.close()
    return total


# -------- CREAR SUSCRIPCION --------
def crear_suscripcion(cliente_id, membresia_id):
    con = _con()
    cur = con.cursor()

    cur.execute("SELECT precio, duracion_dias FROM membresias WHERE id = ?", (membresia_id,))
    datos = cur.fetchone()

    if not datos:
        con.close()
        print("La membresía no existe")
        return

    precio, duracion    = datos
    fecha_inicio        = datetime.now().date()
    fecha_vencimiento   = fecha_inicio + timedelta(days=duracion)

    cur.execute("""
        INSERT INTO suscripciones (
            cliente_id, membresia_id, fecha_inicio, fecha_vencimiento,
            precio_total, pagado, pendiente
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cliente_id, membresia_id, fecha_inicio, fecha_vencimiento, precio, 0, precio))

    con.commit()
    con.close()
    print("Suscripción creada correctamente")


# -------- ELIMINAR SUSCRIPCION --------
def eliminar_suscripcion(suscripcion_id):
    con = _con()
    con.execute("DELETE FROM suscripciones WHERE id = ?", (suscripcion_id,))
    con.commit()
    con.close()


# -------- CONTAR CLIENTES ACTIVOS --------
def contar_clientes_activos():
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM suscripciones WHERE fecha_vencimiento >= ?", (hoy,))
    total = cur.fetchone()[0]
    con.close()
    return total


# -------- INGRESOS POR MES --------
def ingresos_por_mes():
    con = _con()
    cur = con.cursor()
    anio_actual = datetime.now().strftime("%Y")
    cur.execute("""
        SELECT strftime('%m', fecha_inicio) AS mes,
               COALESCE(SUM(pagado), 0)    AS total
        FROM suscripciones
        WHERE strftime('%Y', fecha_inicio) = ?
        GROUP BY strftime('%m', fecha_inicio)
        ORDER BY strftime('%m', fecha_inicio)
    """, (anio_actual,))
    datos = cur.fetchall()
    con.close()
    return datos

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


def abrir_ventana_pagos(parent):

    ventana = tb.Toplevel(parent)
    ventana.title("Gestión de Pagos")
    ventana.state("zoomed")
    ventana.resizable(True, True)
    ventana.lift()
    ventana.focus_force()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))

    # ---------- SCROLL ----------
    contenedor_principal = tk.Frame(ventana, bg="#1e1e1e")
    contenedor_principal.pack(fill=BOTH, expand=True)

    canvas = tk.Canvas(contenedor_principal, bg="#1e1e1e", highlightthickness=0, bd=0)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(contenedor_principal, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    frame_scroll = tk.Frame(canvas, bg="#1e1e1e")
    window_id = canvas.create_window((0, 0), window=frame_scroll, anchor="nw")

    def actualizar_scrollregion(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def ajustar_ancho_frame(event):
        canvas.itemconfig(window_id, width=event.width)

    frame_scroll.bind("<Configure>", actualizar_scrollregion)
    canvas.bind("<Configure>", ajustar_ancho_frame)

    def _on_mousewheel_principal(event):
        if not canvas.winfo_exists():
            return "break"
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass
        return "break"

    ventana.bind_all("<MouseWheel>", _on_mousewheel_principal)
    ventana.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    ventana.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    # ---------- ESTILOS ----------
    style = ttk.Style()
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=35)
    style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

    # ---------- CONTENEDOR ----------
    contenedor = tk.Frame(frame_scroll, bg="#1e1e1e", padx=16, pady=16)
    contenedor.pack(fill=BOTH, expand=True)

    # ---------- HEADER ----------
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

    # ---------- TARJETAS ----------
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
    # NUEVO: card de total recaudado en dinero
    lbl_total_recaudado  = hacer_card(frame_cards, "#6f42c1", "Total Recaudado ($)")

    # ---------- CLIENTES Y SUSCRIPCIONES ----------
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
                                   show="headings", height=6)
    tabla_clientes.heading("ID",     text="ID")
    tabla_clientes.heading("Nombre", text="Nombre")
    tabla_clientes.column("ID",     width=100, anchor="center")
    tabla_clientes.column("Nombre", width=260, anchor="center")
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
                              show="headings", height=6)
    tabla_sus.heading("ID",      text="ID Suscripción")
    tabla_sus.heading("Cliente", text="Cliente")
    tabla_sus.heading("Plan",    text="Plan")
    tabla_sus.column("ID",      anchor="center", width=50)
    tabla_sus.column("Cliente", anchor="center", width=180)
    tabla_sus.column("Plan",    anchor="center", width=150)
    tabla_sus.pack(side=LEFT, fill=BOTH, expand=YES)
    ss = ttk.Scrollbar(frame_ss, orient=VERTICAL, command=tabla_sus.yview)
    ss.pack(side=RIGHT, fill=Y)
    tabla_sus.configure(yscrollcommand=ss.set)

    def scroll_clientes_mouse(event):
        tabla_clientes.yview_scroll(int(-1*(event.delta/120)), "units"); return "break"
    def scroll_sus_mouse(event):
        tabla_sus.yview_scroll(int(-1*(event.delta/120)), "units"); return "break"
    def restaurar_scroll(event=None):
        ventana.bind_all("<MouseWheel>", _on_mousewheel_principal)
    tabla_clientes.bind("<Enter>", lambda e: ventana.bind_all("<MouseWheel>", scroll_clientes_mouse))
    tabla_clientes.bind("<Leave>", restaurar_scroll)
    tabla_sus.bind("<Enter>",     lambda e: ventana.bind_all("<MouseWheel>", scroll_sus_mouse))
    tabla_sus.bind("<Leave>",     restaurar_scroll)

    # ---------- TABLA PRINCIPAL ----------
    frame_tabla = ttk.Labelframe(contenedor, text="Detalle de pagos y suscripciones",
                                  padding=10, bootstyle="info")
    frame_tabla.pack(fill=BOTH, expand=True, pady=8)

    # NUEVO: columna "Acumulado ($)" al final muestra la suma total pagada
    columnas = ("ID", "Cliente", "Plan", "Total", "Pagado", "Pendiente",
                "Inicio", "Vence", "Acumulado ($)")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120, anchor=CENTER)

    tabla.column("Cliente",       width=220, anchor=W)
    tabla.column("Plan",          width=180, anchor=W)
    tabla.column("Acumulado ($)", width=130, anchor=CENTER)

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

    def _on_mousewheel_tabla(event):
        tabla.yview_scroll(int(-1*(event.delta/120)), "units"); return "break"
    tabla.bind("<Enter>", lambda e: ventana.bind_all("<MouseWheel>", _on_mousewheel_tabla))
    tabla.bind("<Leave>", restaurar_scroll)

    # ---------- PANEL INFERIOR ----------
    frame_inferior = ttk.Frame(contenedor)
    frame_inferior.pack(fill=X, pady=12)
    frame_inferior.grid_columnconfigure(0, weight=1)
    frame_inferior.grid_columnconfigure(1, weight=1)

    frame_buscar = ttk.Labelframe(frame_inferior, text="Buscar / Crear suscripción", padding=12)
    frame_buscar.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
    frame_pago   = ttk.Labelframe(frame_inferior, text="Registrar pago", padding=12)
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

    # ---------- FUNCIONES ----------
    def actualizar_cards(datos=None):
        if datos is None:
            datos = listar_suscripciones_para_pago()
        total      = len(datos)
        pagadas    = 0
        pendientes = 0
        recaudado  = 0.0
        for sus in datos:
            total_pago = float(sus[4])
            pagado     = float(sus[5])
            pendiente  = max(0.0, float(sus[6]))
            recaudado += pagado
            if pagado >= total_pago or pendiente <= 0:
                pagadas += 1
            else:
                pendientes += 1
        lbl_total_valor.config(text=str(total))
        lbl_total_pagadas.config(text=str(pagadas))
        lbl_total_pendientes.config(text=str(pendientes))
        lbl_total_recaudado.config(text=f"${recaudado:,.2f}")

    def cargar_clientes():
        for fila in tabla_clientes.get_children():
            tabla_clientes.delete(fila)
        for c in ver_clientes():
            tabla_clientes.insert("", END, values=(c[0], c[1]))

    def cargar_suscripciones():
        for fila in tabla.get_children():
            tabla.delete(fila)
        datos = listar_suscripciones_para_pago()
        for sus in datos:
            cliente        = sus[1]
            id_suscripcion = sus[2]
            plan           = sus[3]
            total          = float(sus[4])
            pagado         = float(sus[5])
            pendiente      = max(0.0, float(sus[6]))
            inicio         = sus[7]
            vence          = sus[8]
            fila = (id_suscripcion, cliente, plan,
                    f"{total:.2f}", f"{pagado:.2f}", f"{pendiente:.2f}",
                    inicio, vence, f"${pagado:.2f}")
            if pagado >= total or pendiente <= 0:   tag = "pagado"
            elif pagado > 0:                        tag = "parcial"
            else:                                   tag = "deuda"
            tabla.insert("", END, values=fila, tags=(tag,))
        actualizar_cards(datos)

    def buscar_cliente():
        cliente_id = entry_cliente.get().strip()
        if not cliente_id:
            messagebox.showerror("Error", "Ingrese un ID de cliente", parent=ventana); return
        try:
            cliente_id = int(cliente_id)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana); return
        datos = buscar_cliente_pagos(cliente_id)
        if not datos:
            messagebox.showinfo("Sin resultados", "El cliente no tiene suscripciones", parent=ventana); return
        for fila in tabla.get_children():
            tabla.delete(fila)
        pagadas = pendientes_c = 0
        recaudado = 0.0
        for sus in datos:
            id_s, cliente, plan, total, pagado, pendiente, inicio, vence = sus
            total    = float(total)
            pagado   = float(pagado)
            pendiente = max(0.0, float(pendiente))
            recaudado += pagado
            fila = (id_s, cliente, plan,
                    f"{total:.2f}", f"{pagado:.2f}", f"{pendiente:.2f}",
                    inicio, vence, f"${pagado:.2f}")
            if pagado >= total or pendiente <= 0:  tag = "pagado";  pagadas += 1
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
        entry_id.delete(0, END)
        entry_id.insert(0, tabla.item(sel[0], "values")[0])

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
        suscripcion = entry_id.get().strip()
        monto       = entry_monto.get().strip()
        if not suscripcion or not monto:
            messagebox.showerror("Error", "Debes seleccionar una suscripción y escribir el monto", parent=ventana); return
        try:
            suscripcion = int(suscripcion); monto = float(monto)
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
        try:
            suscripcion = int(suscripcion)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana); return
        historial = ver_historial_pagos(suscripcion)
        if not historial:
            messagebox.showinfo("Historial", "No hay pagos registrados", parent=ventana); return
        vh = tb.Toplevel(ventana)
        vh.title("Historial de Pagos"); vh.geometry("520x350")
        frame_hist = ttk.Frame(vh, padding=10)
        frame_hist.pack(fill=BOTH, expand=True)
        th = ttk.Treeview(frame_hist, columns=("ID Pago", "Monto", "Fecha"), show="headings")
        th.heading("ID Pago", text="ID Pago")
        th.heading("Monto",   text="Monto")
        th.heading("Fecha",   text="Fecha")
        th.column("ID Pago", width=100, anchor=CENTER)
        th.column("Monto",   width=120, anchor=CENTER)
        th.column("Fecha",   width=180, anchor=CENTER)
        th.pack(fill=BOTH, expand=True)
        for pago_id, monto, fecha in historial:
            th.insert("", END, values=(pago_id, monto, fecha))

    def cargar_suscripciones_lista():
        for fila in tabla_sus.get_children():
            tabla_sus.delete(fila)
        for sus in ver_suscripciones_completas():
            id_s, cliente, plan, inicio, vence, pagado, deuda = sus
            tabla_sus.insert("", END, values=(id_s, cliente, plan))

    def eliminar_pago_seleccionado():
        suscripcion = entry_id.get().strip()
        if not suscripcion:
            messagebox.showerror("Error", "Selecciona una suscripción", parent=ventana); return
        try:
            suscripcion = int(suscripcion)
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
        cliente   = entry_id_cliente.get().strip()
        membresia = entry_id_membresia.get().strip()
        if not cliente or not membresia:
            messagebox.showerror("Error", "Debes ingresar cliente y membresía", parent=ventana); return
        try:
            cliente = int(cliente); membresia = int(membresia)
        except ValueError:
            messagebox.showerror("Error", "IDs inválidos", parent=ventana); return
        crear_suscripcion(cliente, membresia)
        messagebox.showinfo("Éxito", "Suscripción creada", parent=ventana)
        cargar_suscripciones(); cargar_suscripciones_lista()

    # ---------- EVENTOS ----------
    tabla.bind("<<TreeviewSelect>>",          seleccionar_fila)
    tabla_clientes.bind("<<TreeviewSelect>>", seleccionar_cliente)
    tabla_sus.bind("<<TreeviewSelect>>",      seleccionar_suscripcion)

    # ---------- BOTONES ----------
    frame_botones = ttk.Frame(contenedor)
    frame_botones.pack(fill=X, pady=12)

    ttk.Button(frame_botones, text="Buscar", bootstyle="info",
               width=12, command=buscar_cliente).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Crear Suscripción", bootstyle="primary",
               width=16, command=crear_suscripcion_rapida).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Registrar Pago", bootstyle="success",
               width=14, command=pagar).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Ver Historial", bootstyle="warning",
               width=14, command=ver_historial).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Eliminar Pago", bootstyle="danger",
               width=14, command=eliminar_pago_seleccionado).pack(side="left", padx=4)
    ttk.Button(frame_botones, text="Actualizar", bootstyle="secondary", width=12,
               command=lambda: [cargar_clientes(), cargar_suscripciones(),
                                cargar_suscripciones_lista()]).pack(side="right", padx=4)

    # ---------- CARGA INICIAL ----------
    cargar_clientes()
    cargar_suscripciones()
    cargar_suscripciones_lista()

    # -------- CLIENTES ACTIVOS CON DETALLE --------
def ver_clientes_activos_detalle():
    """
    Retorna todas las suscripciones activas (fecha_vencimiento >= hoy)
    con detalle completo para la ventana de clientes activos.
    """
    con = _con()
    cur = con.cursor()
    hoy = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT suscripciones.id,
               clientes.nombre,
               membresias.nombre_plan,
               suscripciones.fecha_inicio,
               suscripciones.fecha_vencimiento,
               suscripciones.pagado,
               suscripciones.pendiente
        FROM suscripciones
        JOIN clientes   ON suscripciones.cliente_id   = clientes.id
        JOIN membresias ON suscripciones.membresia_id = membresias.id
        WHERE suscripciones.fecha_vencimiento >= ?
        ORDER BY suscripciones.fecha_vencimiento ASC
    """, (hoy,))
    datos = cur.fetchall()
    con.close()
    return datos

# -------- RENOVAR SUSCRIPCION DE UN CLIENTE (+30 dias) --------
def renovar_suscripcion_cliente(cliente_id: int, dias: int = 30) -> str:
    """
    Extiende la fecha_vencimiento de la suscripcion mas reciente del cliente.
    Devuelve: 'ok' | 'sin_suscripcion' | 'fecha_invalida'
    """
    con = _con()
    cur = con.cursor()

    cur.execute("""
        SELECT id, fecha_vencimiento
        FROM suscripciones
        WHERE cliente_id = ?
        ORDER BY fecha_vencimiento DESC
        LIMIT 1
    """, (cliente_id,))

    fila = cur.fetchone()
    if fila is None:
        con.close()
        return "sin_suscripcion"

    sus_id, fecha_venc_str = fila

    fecha_venc = None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            fecha_venc = datetime.strptime(fecha_venc_str, fmt)
            break
        except ValueError:
            continue

    if fecha_venc is None:
        con.close()
        return "fecha_invalida"

    nueva_fecha = (fecha_venc + timedelta(days=dias)).strftime("%Y-%m-%d")

    cur.execute("UPDATE suscripciones SET fecha_vencimiento = ? WHERE id = ?",
                (nueva_fecha, sus_id))
    con.commit()
    con.close()
    return "ok"