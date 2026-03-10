import customtkinter as ctk
from tkinter import ttk, messagebox

from modulos.pagos import registrar_pago, ver_historial_pagos, listar_suscripciones_para_pago, buscar_cliente_pagos


def abrir_ventana_pagos(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Gestión de Pagos")
    ventana.geometry("800x500")

    # -------- TABLA --------

    columnas = (
        "ID",
        "Cliente",
        "ID Suscripción",
        "Plan",
        "Total",
        "Pagado",
        "Pendiente",
        "Inicio",
        "Vence")

    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=150)

    tabla.pack(pady=20, fill="both", expand=True)

    # -------- FRAME FORMULARIO --------

    frame = ctk.CTkFrame(ventana)
    frame.pack(pady=10)

    ctk.CTkLabel(frame, text="ID Suscripción").grid(row=0, column=0, padx=10)
    entry_id = ctk.CTkEntry(frame, width=120)
    entry_id.grid(row=0, column=1)

    ctk.CTkLabel(frame, text="Monto a pagar").grid(row=1, column=0, padx=10)
    entry_monto = ctk.CTkEntry(frame, width=120)
    entry_monto.grid(row=1, column=1)


    # FRAME BUSCAR CLIENTE
    
    frame_buscar = ctk.CTkFrame(ventana)
    frame_buscar.pack(pady=10)

    ctk.CTkLabel(frame_buscar, text="Buscar por ID Cliente").grid(row=0, column=0, padx=10)

    entry_cliente = ctk.CTkEntry(frame_buscar)
    entry_cliente.grid(row=0, column=1)

    # -------- CARGAR SUSCRIPCIONES --------

    def cargar_suscripciones():

        for fila in tabla.get_children():
            tabla.delete(fila)

        datos = listar_suscripciones_para_pago()

        if not datos:
            messagebox.showinfo("Información", "No hay suscripciones con deuda")
            return

        for sus in datos:
            tabla.insert("", "end", values=sus)

    # -------- SELECCIONAR FILA --------

    def seleccionar_fila(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        valores = tabla.item(seleccion[0], "values")

        entry_id.delete(0, ctk.END)
        entry_id.insert(0, valores[0])

    tabla.bind("<<TreeviewSelect>>", seleccionar_fila)

    # -------- REGISTRAR PAGO --------

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

    # -------- VER HISTORIAL --------

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

    # -------- BOTONES --------

    frame_botones = ctk.CTkFrame(ventana)
    frame_botones.pack(pady=10)

    boton_pagar = ctk.CTkButton(
        frame_botones,
        text="Registrar Pago",
        command=pagar
    )
    boton_pagar.grid(row=0, column=0, padx=10)

    boton_historial = ctk.CTkButton(
        frame_botones,
        text="Ver Historial",
        command=ver_historial
    )
    boton_historial.grid(row=0, column=1, padx=10)

    cargar_suscripciones()