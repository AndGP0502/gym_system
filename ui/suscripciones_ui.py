import customtkinter as ctk
from tkinter import ttk, messagebox

from modulos.clientes import ver_clientes
from modulos.membresias import ver_membresias

from modulos.suscripciones import (
    asignar_membresia,
    ver_estado_gimnasio,
    ver_clientes_vencidos,
    ver_dias_restantes,
    clientes_por_vencer,
    ver_suscripciones_completas
)


def abrir_ventana_suscripciones(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Suscripciones")
    ventana.geometry("900x500")

    ventana.transient(parent)
    ventana.grab_set()
    ventana.lift()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))
    ventana.focus_force()

    # -------- TABLA --------

    columnas = ("ID", "Cliente", "Plan", "Estado")

    tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)

    tabla.pack(pady=20, fill="both", expand=True)

    # -------- FRAME BOTONES --------

    frame_botones = ctk.CTkFrame(ventana)
    frame_botones.pack(pady=10)

    # -------- FUNCIONES --------

    def limpiar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)

    def estado_gimnasio():

        limpiar_tabla()

        datos = ver_estado_gimnasio()

        for id_sus, nombre, plan, vence, pagado, deuda in datos:
            estado = f"Vence: {vence} | Deuda: {deuda}"
            tabla.insert("", "end", values=(id_sus, nombre, plan, estado))

    def ver_vencidos():

        limpiar_tabla()

        datos = ver_clientes_vencidos()

        for nombre, fecha in datos:
            tabla.insert("", "end", values=("", nombre, "Vencido", fecha))

    def ver_por_vencer():

        limpiar_tabla()

        datos = clientes_por_vencer()

        for nombre, plan, dias in datos:
            estado = f"Vence en {dias} días"
            tabla.insert("", "end", values=("", nombre, plan, estado))

    def ver_dias():

        limpiar_tabla()

        datos = ver_dias_restantes()

        for nombre, plan, estado in datos:
            tabla.insert("", "end", values=("", nombre, plan, estado))

    def ver_completas():

        limpiar_tabla()

        datos = ver_suscripciones_completas()

        for id_s, cliente, plan, inicio, vence, pagado, deuda in datos:
            estado = f"{inicio} → {vence} | Pagado: {pagado} | Deuda: {deuda}"
            tabla.insert("", "end", values=(id_s, cliente, plan, estado))

    # -------- BOTONES --------

    boton_estado = ctk.CTkButton(
        frame_botones,
        text="Estado del gimnasio",
        command=estado_gimnasio
    )
    boton_estado.grid(row=0, column=0, padx=10, pady=5)

    boton_vencidos = ctk.CTkButton(
        frame_botones,
        text="Clientes vencidos",
        command=ver_vencidos
    )
    boton_vencidos.grid(row=0, column=1, padx=10)

    boton_por_vencer = ctk.CTkButton(
        frame_botones,
        text="Clientes por vencer",
        command=ver_por_vencer
    )
    boton_por_vencer.grid(row=0, column=2, padx=10)

    boton_dias = ctk.CTkButton(
        frame_botones,
        text="Días restantes",
        command=ver_dias
    )
    boton_dias.grid(row=1, column=0, padx=10, pady=5)

    boton_completas = ctk.CTkButton(
        frame_botones,
        text="Suscripciones completas",
        command=ver_completas
    )
    boton_completas.grid(row=1, column=1, padx=10)

    # -------- ASIGNAR MEMBRESIA --------

    frame_asignar = ctk.CTkFrame(ventana)
    frame_asignar.pack(pady=15)

    ctk.CTkLabel(frame_asignar, text="ID Cliente").grid(row=0, column=0)
    entry_cliente = ctk.CTkEntry(frame_asignar)
    entry_cliente.grid(row=0, column=1)

    ctk.CTkLabel(frame_asignar, text="ID Membresía").grid(row=1, column=0)
    entry_membresia = ctk.CTkEntry(frame_asignar)
    entry_membresia.grid(row=1, column=1)

    ctk.CTkLabel(frame_asignar, text="Precio").grid(row=2, column=0)
    entry_precio = ctk.CTkEntry(frame_asignar)
    entry_precio.grid(row=2, column=1)

    ctk.CTkLabel(frame_asignar, text="Pagado").grid(row=3, column=0)
    entry_pagado = ctk.CTkEntry(frame_asignar)
    entry_pagado.grid(row=3, column=1)

    def asignar():

        try:

            cliente = int(entry_cliente.get())
            membresia = int(entry_membresia.get())
            precio = float(entry_precio.get())
            pagado = float(entry_pagado.get())

        except ValueError:
            messagebox.showerror("Error", "Datos inválidos")
            return

        asignar_membresia(cliente, membresia, precio, pagado)

        messagebox.showinfo("Éxito", "Membresía asignada")

        entry_cliente.delete(0, ctk.END)
        entry_membresia.delete(0, ctk.END)
        entry_precio.delete(0, ctk.END)
        entry_pagado.delete(0, ctk.END)

    boton_asignar = ctk.CTkButton(
        frame_asignar,
        text="Asignar membresía",
        command=asignar
    )

    boton_asignar.grid(row=4, column=0, columnspan=2, pady=10)

    import sqlite3
    from datetime import date
