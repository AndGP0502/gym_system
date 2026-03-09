import customtkinter as ctk

from ui.clientes_ui import abrir_ventana_clientes
from ui.pagos_ui import abrir_ventana_pagos
from ui.suscripciones_ui import abrir_ventana_suscripciones
from ui.membresias_ui import abrir_ventana_membresias

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def iniciar_ventana():

    ventana = ctk.CTk()
    ventana.title("Sistema de Gimnasio")
    ventana.geometry("700x500")

    titulo = ctk.CTkLabel(
        ventana,
        text="Sistema de Gestión de Gimnasio",
        font=("Arial", 26)
    )
    titulo.pack(pady=40)

    # -------- CLIENTES --------

    boton_clientes = ctk.CTkButton(
        ventana,
        text="Clientes",
        width=200,
        height=40,
        command=lambda: abrir_ventana_clientes(ventana)
    )
    boton_clientes.pack(pady=10)

    # -------- MEMBRESIAS --------

    boton_membresias = ctk.CTkButton(
        ventana,
        text="Membresías",
        width=200,
        height=40,
        command=lambda: abrir_ventana_membresias(ventana)
    )
    boton_membresias.pack(pady=10)

    # -------- SUSCRIPCIONES --------

    boton_suscripciones = ctk.CTkButton(
        ventana,
        text="Suscripciones",
        width=200,
        height=40,
        command=lambda: abrir_ventana_suscripciones(ventana)
    )
    boton_suscripciones.pack(pady=10)

    # -------- PAGOS --------

    boton_pagos = ctk.CTkButton(
        ventana,
        text="Pagos",
        width=200,
        height=40,
        command=lambda: abrir_ventana_pagos(ventana)
    )
    boton_pagos.pack(pady=10)

    # -------- SALIR --------

    boton_salir = ctk.CTkButton(
        ventana,
        text="Salir",
        width=200,
        height=40,
        command=ventana.destroy
    )
    boton_salir.pack(pady=40)

    ventana.mainloop()

    

