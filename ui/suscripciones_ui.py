import customtkinter as ctk
from tkinter import ttk, messagebox

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

    # ventana maximizada
    ventana.state("zoomed")

    # permitir controles del sistema
    ventana.resizable(True, True)

    # traer al frente
    ventana.lift()
    ventana.focus_force()

    # ---------- FRAME PRINCIPAL ----------
    scroll = ctk.CTkScrollableFrame(ventana)
    scroll.pack(fill="both", expand=True)

    # ---------- TABLA ----------
    columnas = ("ID", "Cliente", "Plan", "Vence", "Pagado", "Estado")

    frame_tabla = ctk.CTkFrame(scroll)
    frame_tabla.pack(fill="both", expand=True)

    style = ttk.Style()

    style.configure(
        "Treeview",
        font=("Segoe UI", 12),
        rowheight=35
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 15, "bold")
    )

    tabla = ttk.Treeview(
        frame_tabla,
        columns=columnas,
        show="headings"
    )

    tabla.heading("ID", text="ID")
    tabla.heading("Cliente", text="Cliente")
    tabla.heading("Plan", text="Plan")
    tabla.heading("Vence", text="Vence")
    tabla.heading("Pagado", text="Pagado")
    tabla.heading("Estado", text="Estado")

    tabla.column("ID", width=80, anchor="center")
    tabla.column("Cliente", width=220, anchor="center")
    tabla.column("Plan", width=180, anchor="center")
    tabla.column("Vence", width=140, anchor="center")
    tabla.column("Pagado", width=120, anchor="center")
    tabla.column("Estado", width=180, anchor="center")

    # COLORES DE ESTADO
    tabla.tag_configure("activo", foreground="#2ecc71")
    tabla.tag_configure("vencido", foreground="#e74c3c")
    tabla.tag_configure("por_vencer", foreground="#f1c40f")

    # ---------- SCROLLBARS ----------
    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)

    tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    # ---------- FRAME BOTONES ----------
    frame_botones = ctk.CTkFrame(scroll)
    frame_botones.pack(pady=10)

    # ---------- FUNCIONES ----------
    def limpiar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)

    def estado_gimnasio():
        limpiar_tabla()
        datos = ver_estado_gimnasio()

        for id_sus, nombre, plan, vence, pagado, deuda in datos:
            if deuda > 0:
                estado = "Pendiente"
                tag = "vencido"
            else:
                estado = "Activo"
                tag = "activo"

            tabla.insert(
                "",
                "end",
                values=(
                    id_sus,
                    nombre,
                    plan,
                    vence,
                    f"${float(pagado):.2f}",
                    estado
                ),
                tags=(tag,)
            )

    def ver_vencidos():
        limpiar_tabla()
        datos = ver_clientes_vencidos()

        for nombre, fecha in datos:
            tabla.insert(
                "",
                "end",
                values=(
                    "",
                    nombre,
                    "",
                    fecha,
                    "",
                    "Vencido"
                ),
                tags=("vencido",)
            )

    def ver_por_vencer():
        limpiar_tabla()
        datos = clientes_por_vencer()

        for nombre, plan, dias in datos:
            estado = f"Vence en {dias} días"

            tabla.insert(
                "",
                "end",
                values=(
                    "",
                    nombre,
                    plan,
                    "",
                    "",
                    estado
                ),
                tags=("por_vencer",)
            )

    def ver_dias():
        limpiar_tabla()
        datos = ver_dias_restantes()

        for nombre, plan, estado in datos:
            if "Vencido" in estado:
                tag = "vencido"
            elif "Vence en" in estado:
                tag = "por_vencer"
            else:
                tag = "activo"

            tabla.insert(
                "",
                "end",
                values=(
                    "",
                    nombre,
                    plan,
                    "",
                    "",
                    estado
                ),
                tags=(tag,)
            )

    def ver_completas():
        limpiar_tabla()
        datos = ver_suscripciones_completas()

        for id_s, cliente, plan, inicio, vence, pagado, deuda in datos:
            if deuda > 0:
                estado = "Pendiente"
                tag = "vencido"
            else:
                estado = "Completa"
                tag = "activo"

            tabla.insert(
                "",
                "end",
                values=(
                    id_s,
                    cliente,
                    plan,
                    vence,
                    f"${float(pagado):.2f}",
                    estado
                ),
                tags=(tag,)
            )

    # ---------- BOTONES ----------
    ctk.CTkButton(
        frame_botones,
        text="Estado del gimnasio",
        command=estado_gimnasio
    ).grid(row=0, column=0, padx=10, pady=5)

    ctk.CTkButton(
        frame_botones,
        text="Clientes vencidos",
        command=ver_vencidos
    ).grid(row=0, column=1, padx=10)

    ctk.CTkButton(
        frame_botones,
        text="Clientes por vencer",
        command=ver_por_vencer
    ).grid(row=0, column=2, padx=10)

    ctk.CTkButton(
        frame_botones,
        text="Días restantes",
        command=ver_dias
    ).grid(row=1, column=0, padx=10, pady=5)

    ctk.CTkButton(
        frame_botones,
        text="Suscripciones completas",
        command=ver_completas
    ).grid(row=1, column=1, padx=10)

    # ---------- ASIGNAR MEMBRESIA ----------
    frame_asignar = ctk.CTkFrame(scroll)
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

    ctk.CTkButton(
        frame_asignar,
        text="Asignar membresía",
        command=asignar
    ).grid(row=4, column=0, columnspan=2, pady=10)