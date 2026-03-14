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

    # ---------- CONTENEDOR CON SCROLL ----------
    contenedor_principal = tk.Frame(ventana, bg="#1e1e1e")
    contenedor_principal.pack(fill=BOTH, expand=True)

    canvas = tk.Canvas(
        contenedor_principal,
        bg="#1e1e1e",
        highlightthickness=0,
        bd=0
    )
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
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _on_mousewheel_linux_up(event):
        canvas.yview_scroll(-1, "units")
        return "break"

    def _on_mousewheel_linux_down(event):
        canvas.yview_scroll(1, "units")
        return "break"

    ventana.bind_all("<MouseWheel>", _on_mousewheel_principal)
    ventana.bind_all("<Button-4>", _on_mousewheel_linux_up)
    ventana.bind_all("<Button-5>", _on_mousewheel_linux_down)

    # ---------- ESTILOS ----------
    style = ttk.Style()

    style.configure(
        "Treeview",
        font=("Segoe UI", 10),
        rowheight=35
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 12, "bold")
    )

    # ---------- CONTENEDOR INTERNO ----------
    contenedor = tk.Frame(frame_scroll, bg="#1e1e1e", padx=16, pady=16)
    contenedor.pack(fill=BOTH, expand=True)

    # ---------- HEADER ----------
    frame_header = ttk.Frame(contenedor, bootstyle="dark")
    frame_header.pack(fill=X, pady=(6, 14))

    header_inner = ttk.Frame(frame_header, padding=18)
    header_inner.pack(fill=X)

    ttk.Label(
        header_inner,
        text="Gestión de Pagos",
        font=("Segoe UI", 24, "bold")
    ).pack(side=LEFT, padx=(8, 18))

    ttk.Label(
        header_inner,
        text="Administra pagos, consulta historial y crea suscripciones",
        font=("Segoe UI", 11)
    ).pack(side=LEFT)

    ttk.Button(
        header_inner,
        text="← Volver al menú",
        bootstyle="secondary",
        command=ventana.destroy
    ).pack(side=RIGHT, padx=8)

    # ---------- TARJETAS ----------
    frame_cards = tk.Frame(contenedor, bg="#1e1e1e")
    frame_cards.pack(fill=X, pady=(0, 14))

    card_total = tk.Frame(frame_cards, bg="#3b5f86", height=130)
    card_total.pack(side=LEFT, fill=X, expand=True, padx=8)
    card_total.pack_propagate(False)

    card_pagadas = tk.Frame(frame_cards, bg="#13c29a", height=130)
    card_pagadas.pack(side=LEFT, fill=X, expand=True, padx=8)
    card_pagadas.pack_propagate(False)

    card_pendientes = tk.Frame(frame_cards, bg="#3d9ad6", height=130)
    card_pendientes.pack(side=LEFT, fill=X, expand=True, padx=8)
    card_pendientes.pack_propagate(False)

    tk.Label(
        card_total,
        text="Total Suscripciones",
        font=("Segoe UI", 14, "bold"),
        bg="#1c1c1c",
        fg="white",
        padx=10,
        pady=4
    ).pack(pady=(20, 6))

    lbl_total_valor = tk.Label(
        card_total,
        text="0",
        font=("Segoe UI", 30, "bold"),
        bg="#1c1c1c",
        fg="white",
        padx=10,
        pady=4
    )
    lbl_total_valor.pack()

    tk.Label(
        card_pagadas,
        text="Pagadas",
        font=("Segoe UI", 14, "bold"),
        bg="#1c1c1c",
        fg="white",
        padx=10,
        pady=4
    ).pack(pady=(20, 6))

    lbl_total_pagadas = tk.Label(
        card_pagadas,
        text="0",
        font=("Segoe UI", 30, "bold"),
        bg="#1c1c1c",
        fg="white",
        padx=10,
        pady=4
    )
    lbl_total_pagadas.pack()

    tk.Label(
        card_pendientes,
        text="Pendientes",
        font=("Segoe UI", 14, "bold"),
        bg="#1c1c1c",
        fg="white",
        padx=10,
        pady=4
    ).pack(pady=(20, 6))

    lbl_total_pendientes = tk.Label(
        card_pendientes,
        text="0",
        font=("Segoe UI", 30, "bold"),
        bg="#1c1c1c",
        fg="white",
        padx=10,
        pady=4
    )
    lbl_total_pendientes.pack()

    # ---------- CLIENTES Y SUSCRIPCIONES LADO A LADO ----------
    frame_superior = ttk.Frame(contenedor)
    frame_superior.pack(fill=X, pady=8)

    frame_superior.columnconfigure(0, weight=1)
    frame_superior.columnconfigure(1, weight=1)

    # ---------- CLIENTES ----------
    frame_clientes = ttk.Labelframe(
        frame_superior,
        text="Clientes registrados",
        padding=10,
        bootstyle="primary"
    )
    frame_clientes.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

    frame_clientes_scroll = ttk.Frame(frame_clientes)
    frame_clientes_scroll.pack(fill=BOTH, expand=YES)

    tabla_clientes = ttk.Treeview(
        frame_clientes_scroll,
        columns=("ID", "Nombre"),
        show="headings",
        height=6,
        style="Treeview"
    )

    tabla_clientes.heading("ID", text="ID")
    tabla_clientes.heading("Nombre", text="Nombre")

    tabla_clientes.column("ID", width=100, anchor="center")
    tabla_clientes.column("Nombre", width=260, anchor="center")

    tabla_clientes.pack(side=LEFT, fill=BOTH, expand=YES)

    scroll_clientes = ttk.Scrollbar(
        frame_clientes_scroll,
        orient=VERTICAL,
        command=tabla_clientes.yview
    )
    scroll_clientes.pack(side=RIGHT, fill=Y)

    tabla_clientes.configure(yscrollcommand=scroll_clientes.set)

    # ---------- SUSCRIPCIONES ----------
    frame_sus = ttk.Labelframe(
        frame_superior,
        text="Suscripciones registradas",
        padding=10,
        bootstyle="success"
    )
    frame_sus.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

    frame_sus_scroll = ttk.Frame(frame_sus)
    frame_sus_scroll.pack(fill=BOTH, expand=YES)

    tabla_sus = ttk.Treeview(
        frame_sus_scroll,
        columns=("ID", "Cliente", "Plan"),
        show="headings",
        height=6,
        style="Treeview"
    )

    tabla_sus.heading("ID", text="ID Suscripción")
    tabla_sus.heading("Cliente", text="Cliente")
    tabla_sus.heading("Plan", text="Plan")

    
    tabla_sus.column("ID",        anchor="center", width=50)
    tabla_sus.column("Cliente",   anchor="center", width=180)
    tabla_sus.column("Plan",      anchor="center", width=150)

    tabla_sus.pack(side=LEFT, fill=BOTH, expand=YES)

    scroll_sus = ttk.Scrollbar(
        frame_sus_scroll,
        orient=VERTICAL,
        command=tabla_sus.yview
    )
    scroll_sus.pack(side=RIGHT, fill=Y)

    tabla_sus.configure(yscrollcommand=scroll_sus.set)

    # ---------- SCROLL DEL MOUSE EN CLIENTES Y SUSCRIPCIONES ----------
    def scroll_clientes_mouse(event):
        tabla_clientes.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def scroll_sus_mouse(event):
        tabla_sus.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def activar_scroll_clientes(event):
        ventana.bind_all("<MouseWheel>", scroll_clientes_mouse)

    def activar_scroll_sus(event):
        ventana.bind_all("<MouseWheel>", scroll_sus_mouse)

    def restaurar_scroll_principal(event=None):
        ventana.bind_all("<MouseWheel>", _on_mousewheel_principal)

    tabla_clientes.bind("<Enter>", activar_scroll_clientes)
    tabla_clientes.bind("<Leave>", restaurar_scroll_principal)

    tabla_sus.bind("<Enter>", activar_scroll_sus)
    tabla_sus.bind("<Leave>", restaurar_scroll_principal)

    # ---------- TABLA PRINCIPAL ----------
    frame_tabla = ttk.Labelframe(
        contenedor,
        text="Detalle de pagos y suscripciones",
        padding=10,
        bootstyle="info"
    )
    frame_tabla.pack(fill=BOTH, expand=True, pady=8)

    columnas = ("ID", "Cliente", "Plan", "Total", "Pagado", "Pendiente", "Inicio", "Vence")
    tabla = ttk.Treeview(
        frame_tabla,
        columns=columnas,
        show="headings",
        height=10,
        style="Treeview"
    )

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120, anchor=CENTER)

    tabla.column("Cliente", width=220, anchor=W)
    tabla.column("Plan", width=180, anchor=W)

    tabla.tag_configure("pagado", background="#b6f2c6", foreground="#0f5132")
    tabla.tag_configure("parcial", background="#fff3cd", foreground="#664d03")
    tabla.tag_configure("deuda", background="#f8d7da", foreground="#842029")

    scroll_y = ttk.Scrollbar(frame_tabla, orient=VERTICAL, command=tabla.yview)
    scroll_x = ttk.Scrollbar(frame_tabla, orient=HORIZONTAL, command=tabla.xview)

    tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    def _on_mousewheel_principal(event):
        if not canvas.winfo_exists():
            return "break"

        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except:
            return "break"

        return "break"
    
    def _on_mousewheel_tabla(event):
        tabla.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def activar_scroll_tabla(event):
        ventana.bind_all("<MouseWheel>", _on_mousewheel_tabla)

    def restaurar_scroll_principal(event):
       ventana.bind_all("<MouseWheel>", _on_mousewheel_principal)

    tabla.bind("<Enter>", activar_scroll_tabla)
    tabla.bind("<Leave>", restaurar_scroll_principal)

    for col in columnas:
        tabla.heading(col, text=col)

    tabla.column("ID",        anchor="center", width=50)
    tabla.column("Cliente",   anchor="center", width=180)
    tabla.column("Plan",      anchor="center", width=150)
    tabla.column("Pagado",    anchor="center", width=100)
    tabla.column("Pendiente", anchor="center", width=100)
    tabla.column("Inicio",    anchor="center", width=110)
    tabla.column("Vence",     anchor="center", width=110)

    # ---------- PANEL INFERIOR ----------
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

    # ---------- FUNCIONES ----------
    def actualizar_cards(datos=None):
        if datos is None:
            datos = listar_suscripciones_para_pago()

        total = len(datos)
        pagadas = 0
        pendientes = 0

        for sus in datos:
            total_pago = float(sus[4])
            pagado = float(sus[5])
            pendiente = float(sus[6])

            if pendiente < 0:
                pendiente = 0.0

            if pagado >= total_pago or pendiente <= 0:
                pagadas += 1
            else:
                pendientes += 1

        lbl_total_valor.config(text=str(total))
        lbl_total_pagadas.config(text=str(pagadas))
        lbl_total_pendientes.config(text=str(pendientes))

    def cargar_clientes():
        for fila in tabla_clientes.get_children():
            tabla_clientes.delete(fila)

        clientes = ver_clientes()

        for cliente in clientes:
            id_cliente = cliente[0]
            nombre = cliente[1]
            tabla_clientes.insert("", END, values=(id_cliente, nombre))

    def cargar_suscripciones():
        for fila in tabla.get_children():
            tabla.delete(fila)

        datos = listar_suscripciones_para_pago()

        for sus in datos:
            cliente = sus[1]
            id_suscripcion = sus[2]
            plan = sus[3]
            total = float(sus[4])
            pagado = float(sus[5])
            pendiente = float(sus[6])
            inicio = sus[7]
            vence = sus[8]

            if pendiente < 0:
                pendiente = 0.0

            fila = (
                id_suscripcion,
                cliente,
                plan,
                f"{total:.2f}",
                f"{pagado:.2f}",
                f"{pendiente:.2f}",
                inicio,
                vence
            )

            if pagado >= total or pendiente <= 0:
                tag = "pagado"
            elif pagado > 0:
                tag = "parcial"
            else:
                tag = "deuda"

            tabla.insert("", END, values=fila, tags=(tag,))

        actualizar_cards(datos)

    def buscar_cliente():
        cliente_id = entry_cliente.get()

        if cliente_id == "":
            messagebox.showerror("Error", "Ingrese un ID de cliente", parent=ventana)
            return

        try:
            cliente_id = int(cliente_id)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana)
            return

        datos = buscar_cliente_pagos(cliente_id)

        if not datos:
            messagebox.showinfo("Sin resultados", "El cliente no tiene suscripciones", parent=ventana)
            return

        for fila in tabla.get_children():
            tabla.delete(fila)

        for sus in datos:
            id_suscripcion, cliente, plan, total, pagado, pendiente, inicio, vence = sus

            total = float(total)
            pagado = float(pagado)
            pendiente = float(pendiente)

            if pendiente < 0:
                pendiente = 0.0

            fila = (
                id_suscripcion,
                cliente,
                plan,
                f"{total:.2f}",
                f"{pagado:.2f}",
                f"{pendiente:.2f}",
                inicio,
                vence
            )

            if pagado >= total or pendiente <= 0:
                tag = "pagado"
            elif pagado > 0:
                tag = "parcial"
            else:
                tag = "deuda"

            tabla.insert("", END, values=fila, tags=(tag,))

        total_registros = len(datos)
        pagadas = 0
        pendientes_count = 0

        for sus in datos:
            total_pago = float(sus[3])
            pagado = float(sus[4])
            pendiente = float(sus[5])

            if pendiente < 0:
                pendiente = 0.0

            if pagado >= total_pago or pendiente <= 0:
                pagadas += 1
            else:
                pendientes_count += 1

        lbl_total_valor.config(text=str(total_registros))
        lbl_total_pagadas.config(text=str(pagadas))
        lbl_total_pendientes.config(text=str(pendientes_count))

    def seleccionar_fila(event):
        seleccion = tabla.selection()
        if not seleccion:
            return

        valores = tabla.item(seleccion[0], "values")
        entry_id.delete(0, END)
        entry_id.insert(0, valores[0])

    def seleccionar_cliente(event):
        item = tabla_clientes.selection()
        if not item:
            return

        valores = tabla_clientes.item(item[0], "values")
        entry_cliente.delete(0, END)
        entry_cliente.insert(0, valores[0])

    def seleccionar_suscripcion(event):
        item = tabla_sus.selection()
        if not item:
            return

        valores = tabla_sus.item(item[0], "values")
        entry_id.delete(0, END)
        entry_id.insert(0, valores[0])

    def pagar():
        suscripcion = entry_id.get()
        monto = entry_monto.get()

        if suscripcion == "" or monto == "":
            messagebox.showerror("Error", "Debes seleccionar una suscripción y escribir el monto", parent=ventana)
            return

        try:
            suscripcion = int(suscripcion)
            monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos", parent=ventana)
            return

        if monto <= 0:
            messagebox.showerror("Error", "El monto debe ser mayor a 0", parent=ventana)
            return

        registrar_pago(suscripcion, monto)
        messagebox.showinfo("Pago registrado", "El pago fue registrado correctamente", parent=ventana)

        entry_id.delete(0, END)
        entry_monto.delete(0, END)

        cargar_suscripciones()
        cargar_suscripciones_lista()

    def ver_historial():
        suscripcion = entry_id.get()

        if suscripcion == "":
            messagebox.showerror("Error", "Seleccione una suscripción primero", parent=ventana)
            return

        try:
            suscripcion = int(suscripcion)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana)
            return

        historial = ver_historial_pagos(suscripcion)

        if not historial:
            messagebox.showinfo("Historial", "No hay pagos registrados", parent=ventana)
            return

        ventana_historial = tb.Toplevel(ventana)
        ventana_historial.title("Historial de Pagos")
        ventana_historial.geometry("520x350")

        frame_hist = ttk.Frame(ventana_historial, padding=10)
        frame_hist.pack(fill=BOTH, expand=True)

        tabla_historial = ttk.Treeview(
            frame_hist,
            columns=("ID Pago", "Monto", "Fecha"),
            show="headings",
            style="Treeview"
        )

        tabla_historial.heading("ID Pago", text="ID Pago")
        tabla_historial.heading("Monto", text="Monto")
        tabla_historial.heading("Fecha", text="Fecha")

        tabla_historial.column("ID Pago", width=100, anchor=CENTER)
        tabla_historial.column("Monto", width=120, anchor=CENTER)
        tabla_historial.column("Fecha", width=180, anchor=CENTER)

        tabla_historial.pack(fill=BOTH, expand=True)

        for pago_id, monto, fecha in historial:
            tabla_historial.insert("", END, values=(pago_id, monto, fecha))

    def cargar_suscripciones_lista():
        for fila in tabla_sus.get_children():
            tabla_sus.delete(fila)

        datos = ver_suscripciones_completas()

        for sus in datos:
            id_s, cliente, plan, inicio, vence, pagado, deuda = sus
            tabla_sus.insert("", END, values=(id_s, cliente, plan))

    def eliminar_pago_seleccionado():
        suscripcion = entry_id.get()

        if suscripcion == "":
            messagebox.showerror("Error", "Selecciona una suscripción", parent=ventana)
            return

        try:
            suscripcion = int(suscripcion)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana)
            return

        historial = ver_historial_pagos(suscripcion)

        if not historial:
            messagebox.showinfo("Información", "No hay pagos para eliminar", parent=ventana)
            return

        confirmar = messagebox.askyesno("Confirmar", "¿Eliminar el último pago?", parent=ventana)

        if not confirmar:
            return

        pago_id = historial[-1][0]
        eliminar_pago(pago_id)

        messagebox.showinfo("Pago eliminado", "El pago fue eliminado", parent=ventana)
        cargar_suscripciones()
        cargar_suscripciones_lista()

    def crear_suscripcion_rapida():
        cliente = entry_id_cliente.get()
        membresia = entry_id_membresia.get()

        if cliente == "" or membresia == "":
            messagebox.showerror("Error", "Debes ingresar cliente y membresía", parent=ventana)
            return

        try:
            cliente = int(cliente)
            membresia = int(membresia)
        except ValueError:
            messagebox.showerror("Error", "IDs inválidos", parent=ventana)
            return

        crear_suscripcion(cliente, membresia)
        messagebox.showinfo("Éxito", "Suscripción creada", parent=ventana)

        cargar_suscripciones()
        cargar_suscripciones_lista()

    # ---------- EVENTOS ----------
    tabla.bind("<<TreeviewSelect>>", seleccionar_fila)
    tabla_clientes.bind("<<TreeviewSelect>>", seleccionar_cliente)
    tabla_sus.bind("<<TreeviewSelect>>", seleccionar_suscripcion)

    # ---------- BOTONES ----------
    frame_botones = ttk.Frame(contenedor)
    frame_botones.pack(fill=X, pady=12)

    frame_buscar_btn = ttk.Frame(frame_botones)
    frame_buscar_btn.pack(side="left", padx=10)

    ttk.Button(
        frame_buscar_btn,
        text="Buscar",
        bootstyle="info",
        width=12,
        command=buscar_cliente
    ).pack(side="left", padx=4)

    frame_sus_btn = ttk.Frame(frame_botones)
    frame_sus_btn.pack(side="left", padx=25)

    ttk.Button(
        frame_sus_btn,
        text="Crear Suscripción",
        bootstyle="primary",
        width=16,
        command=crear_suscripcion_rapida
    ).pack(side="left", padx=4)

    frame_pago_btn = ttk.Frame(frame_botones)
    frame_pago_btn.pack(side="left", padx=25)

    ttk.Button(
        frame_pago_btn,
        text="Registrar Pago",
        bootstyle="success",
        width=14,
        command=pagar
    ).pack(side="left", padx=4)

    ttk.Button(
        frame_pago_btn,
        text="Ver Historial",
        bootstyle="warning",
        width=14,
        command=ver_historial
    ).pack(side="left", padx=4)

    ttk.Button(
        frame_pago_btn,
        text="Eliminar Pago",
        bootstyle="danger",
        width=14,
        command=eliminar_pago_seleccionado
    ).pack(side="left", padx=4)

    frame_sistema_btn = ttk.Frame(frame_botones)
    frame_sistema_btn.pack(side="right", padx=10)

    ttk.Button(
        frame_sistema_btn,
        text="Actualizar",
        bootstyle="secondary",
        width=12,
        command=lambda: [cargar_clientes(), cargar_suscripciones(), cargar_suscripciones_lista()]
    ).pack(side="right", padx=4)

    # ---------- CARGA INICIAL ----------
    cargar_clientes()
    cargar_suscripciones()
    cargar_suscripciones_lista()