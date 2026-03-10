import customtkinter as ctk
from tkinter import ttk, messagebox

from modulos.pagos import registrar_pago, ver_historial_pagos, listar_suscripciones_para_pago, buscar_cliente_pagos
from modulos.clientes import ver_clientes
from modulos.suscripciones import ver_suscripciones_completas


def abrir_ventana_pagos(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Gestión de Pagos")
    ventana.geometry("900x600")

    ventana.transient(parent)
    ventana.grab_set()
    ventana.lift()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))
    ventana.focus_force()

    # -------- TABLA CLIENTES --------

    frame_clientes = ctk.CTkFrame(ventana)
    frame_clientes.pack(pady=10, fill="x")

    ctk.CTkLabel(frame_clientes, text="Clientes registrados").pack(pady=5)

    tabla_clientes = ttk.Treeview(
        frame_clientes,
        columns=("ID", "Nombre"),
        show="headings",
        height=5
    )

    tabla_clientes.heading("ID", text="ID")
    tabla_clientes.heading("Nombre", text="Nombre")

    tabla_clientes.column("ID", width=80, anchor="center")
    tabla_clientes.column("Nombre", width=250, anchor="w")

    tabla_clientes.pack(fill="x", padx=10, pady=5)

    # -------- TABLA SUSCRIPCIONES RAPIDAS --------

    frame_sus = ctk.CTkFrame(ventana)
    frame_sus.pack(pady=10, fill="x")

    ctk.CTkLabel(frame_sus, text="Suscripciones registradas").pack(pady=5)

    tabla_sus = ttk.Treeview(
        frame_sus,
        columns=("ID", "Cliente", "Plan"),
        show="headings",
        height=5
    )

    tabla_sus.heading("ID", text="ID Suscripción")
    tabla_sus.heading("Cliente", text="Cliente")
    tabla_sus.heading("Plan", text="Plan")

    tabla_sus.column("ID", width=100, anchor="center")
    tabla_sus.column("Cliente", width=200)
    tabla_sus.column("Plan", width=150)

    tabla_sus.pack(fill="x", padx=10)

    # -------- TABLA ESTADO DE PAGOS --------

    columnas = (
        "ID",
        "Cliente",
        "Plan",
        "Total",
        "Pagado",
        "Pendiente",
        "Inicio",
        "Vence"
    )

    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=110, anchor="center")

    tabla.pack(pady=15, fill="both", expand=True, padx=10)

    # -------- COLORES DE ESTADO --------

    tabla.tag_configure("pagado", background="#baf7b0", foreground="black")
    tabla.tag_configure("parcial", background="#fff3a6", foreground="black")
    tabla.tag_configure("deuda", background="#f5b7b1", foreground="black")

    # -------- FRAME BUSCAR CLIENTE --------

    frame_buscar = ctk.CTkFrame(ventana)
    frame_buscar.pack(pady=10)

    ctk.CTkLabel(frame_buscar, text="Buscar por ID Cliente").grid(row=0, column=0, padx=10)

    entry_cliente = ctk.CTkEntry(frame_buscar, width=120)
    entry_cliente.grid(row=0, column=1, padx=10)

    # -------- FRAME FORMULARIO --------

    frame = ctk.CTkFrame(ventana)
    frame.pack(pady=10)

    ctk.CTkLabel(frame, text="ID Suscripción").grid(row=0, column=0, padx=10)
    entry_id = ctk.CTkEntry(frame, width=120)
    entry_id.grid(row=0, column=1, padx=10)

    ctk.CTkLabel(frame, text="Monto a pagar").grid(row=1, column=0, padx=10)
    entry_monto = ctk.CTkEntry(frame, width=120)
    entry_monto.grid(row=1, column=1, padx=10)

    # -------- FUNCIONES --------

    def cargar_clientes():

        for fila in tabla_clientes.get_children():
            tabla_clientes.delete(fila)

        clientes = ver_clientes()

        for cliente in clientes:
            id_cliente, nombre, telefono, fecha = cliente
            tabla_clientes.insert("", "end", values=(id_cliente, nombre))


    def cargar_suscripciones():

        for fila in tabla.get_children():
            tabla.delete(fila)

        datos = listar_suscripciones_para_pago()

        for sus in datos:

            pagado = float(sus[4])
            pendiente = float(sus[5])

            if pendiente == 0:
                tag = "pagado"
            elif pagado > 0:
                tag = "parcial"
            else:
                tag = "deuda"

            tabla.insert("", "end", values=sus, tags=(tag,))


    def buscar_cliente():

        cliente_id = entry_cliente.get()

        if cliente_id == "":
            messagebox.showerror("Error", "Ingrese un ID de cliente")
            return

        try:
            cliente_id = int(cliente_id)
        except ValueError:
            messagebox.showerror("Error", "ID inválido")
            return

        datos = buscar_cliente_pagos(cliente_id)

        for fila in tabla.get_children():
            tabla.delete(fila)

        if not datos:
            messagebox.showinfo("Información", "Este cliente no tiene suscripciones")
            return

        for fila in datos:
            tabla.insert("", "end", values=fila)


    def seleccionar_fila(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        valores = tabla.item(seleccion[0], "values")

        entry_id.delete(0, ctk.END)
        entry_id.insert(0, valores[0])


    def seleccionar_cliente(event):

        item = tabla_clientes.selection()

        if not item:
            return

        valores = tabla_clientes.item(item[0], "values")

        entry_cliente.delete(0, ctk.END)
        entry_cliente.insert(0, valores[0])


    def pagar():

        suscripcion = entry_id.get()
        monto = entry_monto.get()

        if suscripcion == "" or monto == "":
            messagebox.showerror("Error", "Debes seleccionar una suscripción y escribir el monto")
            return

        try:
            suscripcion = int(suscripcion)
            monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos")
            return

        if monto <= 0:
            messagebox.showerror("Error", "El monto debe ser mayor a 0")
            return

        registrar_pago(suscripcion, monto)

        messagebox.showinfo("Pago registrado", "El pago fue registrado correctamente")

        entry_id.delete(0, ctk.END)
        entry_monto.delete(0, ctk.END)

        cargar_suscripciones()
        cargar_suscripciones_lista()


    def ver_historial():

        suscripcion = entry_id.get()

        if suscripcion == "":
            messagebox.showerror("Error", "Seleccione una suscripción primero")
            return

        historial = ver_historial_pagos(int(suscripcion))

        if not historial:
            messagebox.showinfo("Historial", "No hay pagos registrados")
            return

        texto = ""

        for monto, fecha in historial:
            texto += f"{fecha}  |  ${monto}\n"

        messagebox.showinfo("Historial de pagos", texto)


    def cargar_suscripciones_lista():

        for fila in tabla_sus.get_children():
            tabla_sus.delete(fila)

        datos = ver_suscripciones_completas()

        for sus in datos:
            id_s, cliente, plan, inicio, vence, pagado, deuda = sus
            tabla_sus.insert("", "end", values=(id_s, cliente, plan))


    def seleccionar_suscripcion(event):

        item = tabla_sus.selection()

        if not item:
            return

        valores = tabla_sus.item(item[0], "values")

        entry_id.delete(0, ctk.END)
        entry_id.insert(0, valores[0])


    # -------- EVENTOS --------

    tabla.bind("<<TreeviewSelect>>", seleccionar_fila)
    tabla_clientes.bind("<<TreeviewSelect>>", seleccionar_cliente)
    tabla_sus.bind("<<TreeviewSelect>>", seleccionar_suscripcion)

    # -------- BOTONES --------

    frame_botones = ctk.CTkFrame(ventana)
    frame_botones.pack(pady=15)

    boton_buscar = ctk.CTkButton(
        frame_buscar,
        text="Buscar",
        command=buscar_cliente
    )
    boton_buscar.grid(row=0, column=2, padx=10)

    boton_pagar = ctk.CTkButton(
        frame_botones,
        text="Registrar Pago",
        command=pagar
    )
    boton_pagar.grid(row=0, column=0, padx=15)

    boton_historial = ctk.CTkButton(
        frame_botones,
        text="Ver Historial",
        command=ver_historial
    )
    boton_historial.grid(row=0, column=1, padx=15)

    boton_actualizar = ctk.CTkButton(
        frame_botones,
        text="Actualizar",
        command=lambda: [cargar_suscripciones(), cargar_suscripciones_lista()]
    )
    boton_actualizar.grid(row=0, column=2, padx=15)

    # -------- CARGA INICIAL --------

    cargar_clientes()
    cargar_suscripciones()
    cargar_suscripciones_lista()