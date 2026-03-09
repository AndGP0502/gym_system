import customtkinter as ctk
from tkinter import ttk, messagebox

from modulos.pagos import registrar_pago, ver_historial_pagos, listar_suscripciones_para_pago


def abrir_ventana_pagos(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Pagos")
    ventana.geometry("700x500")

    # -------- TABLA DE SUSCRIPCIONES --------

    columnas = ("ID", "Cliente", "Pendiente")

    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)

    tabla.pack(pady=20, fill="both", expand=True)

    # -------- FRAME FORMULARIO --------

    frame = ctk.CTkFrame(ventana)
    frame.pack(pady=10)

    ctk.CTkLabel(frame, text="ID Suscripción").grid(row=0, column=0, padx=10)
    entry_id = ctk.CTkEntry(frame)
    entry_id.grid(row=0, column=1)

    ctk.CTkLabel(frame, text="Monto a pagar").grid(row=1, column=0, padx=10)
    entry_monto = ctk.CTkEntry(frame)
    entry_monto.grid(row=1, column=1)

    # -------- FUNCION CARGAR SUSCRIPCIONES --------

    def cargar_suscripciones():

        for fila in tabla.get_children():
            tabla.delete(fila)

        datos = listar_suscripciones_para_pago()

        for sus in datos:
            tabla.insert("", "end", values=sus)

    # -------- FUNCION SELECCIONAR FILA --------

    def seleccionar_fila(event):

        item = tabla.selection()

        if not item:
            return

        valores = tabla.item(item, "values")

        entry_id.delete(0, ctk.END)
        entry_id.insert(0, valores[0])

    tabla.bind("<<TreeviewSelect>>", seleccionar_fila)

    # -------- FUNCION REGISTRAR PAGO --------

    def pagar():

        suscripcion = entry_id.get()
        monto = entry_monto.get()

        if suscripcion == "" or monto == "":
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            suscripcion = int(suscripcion)
            monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos")
            return

        registrar_pago(suscripcion, monto)

        messagebox.showinfo("Éxito", "Pago registrado correctamente")

        entry_id.delete(0, ctk.END)
        entry_monto.delete(0, ctk.END)

        cargar_suscripciones()

    # -------- BOTON --------

    boton_pagar = ctk.CTkButton(
        ventana,
        text="Registrar Pago",
        command=pagar
    )

    boton_pagar.pack(pady=10)

    cargar_suscripciones()