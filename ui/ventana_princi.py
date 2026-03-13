import customtkinter as ctk

from ui.clientes_ui import abrir_ventana_clientes
from ui.pagos_ui import abrir_ventana_pagos
from ui.suscripciones_ui import abrir_ventana_suscripciones
from ui.membresias_ui import abrir_ventana_membresias
from modulos.clientes import contar_clientes
from modulos.membresias import contar_membresias
from modulos.suscripciones import contar_suscripciones_vencidas
from modulos.backup_db import crear_backup, restaurar_backup
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def iniciar_ventana():
    ventana = ctk.CTk()
    ventana.title("Sistema de Gestión de Gimnasio")

    ancho = ventana.winfo_screenwidth()
    alto = ventana.winfo_screenheight()
    ventana.geometry(f"{ancho}x{alto}+0+0")

    ventana.update_idletasks()
    ventana.state("zoomed")
    ventana.resizable(True, True)

    # -------- FUNCION ACTUALIZAR DASHBOARD --------
    def actualizar_dashboard():
       numero_clientes.configure(text=str(contar_clientes()))
       numero_membresias.configure(text=str(contar_membresias()))
       numero_vencidas.configure(text=str(contar_suscripciones_vencidas()))

    #-------- FUNCIÓN DE BACKUP--------
    def hacer_backup():

        try:
            
            ruta = crear_backup()
            
            messagebox.showinfo(
                "Backup creado",
                f"Se guardó una copia en:\n{ruta}"
            )
        except Exception as e:
            
            messagebox.showerror(
                "Error",
                f"No se pudo crear el backup:\n{e}"
            )

    #----- RESTAURACIÓN DE BACKUP-----
    def hacer_restauracion():
        
        try:
            
            archivo = restaurar_backup()
            
            if archivo:
                
                messagebox.showinfo(
                    "Backup restaurado",
                    "La base de datos fue restaurada correctamente.\n\nReinicia el sistema."
                )

                ventana.destroy()
                
        except Exception as e:
            
            messagebox.showerror(
                "Error",
                f"No se pudo restaurar el backup:\n{e}"
            )
    # -------- BARRA SUPERIOR --------
    frame_superior = ctk.CTkFrame(ventana, fg_color="transparent")
    frame_superior.pack(fill="x", padx=20, pady=20)

    # columnas para distribuir espacio
    frame_superior.grid_columnconfigure(0, weight=1)
    frame_superior.grid_columnconfigure(1, weight=1)
    frame_superior.grid_columnconfigure(2, weight=1)

    # titulo centrado
    titulo = ctk.CTkLabel(
    frame_superior,
    text="Sistema de Gestión de Gimnasio",
    font=("Arial", 26)
)
    titulo.place(relx=0.5, rely=0.5, anchor="center")

    # boton actualizar a la derecha
    boton_actualizar = ctk.CTkButton(
    frame_superior,
    text="Actualizar",
    width=120,
    height=35,
    command=actualizar_dashboard
)
    boton_actualizar.grid(row=0, column=2, sticky="e", padx=20)

    # -------- DASHBOARD --------
    frame_dashboard = ctk.CTkFrame(ventana)
    frame_dashboard.pack(pady=20)

    # -------- TOTAL CLIENTES --------
    frame_clientes = ctk.CTkFrame(frame_dashboard, width=200, height=100)
    frame_clientes.grid(row=0, column=0, padx=20, pady=10)

    label_clientes = ctk.CTkLabel(
        frame_clientes,
        text="Total de Clientes",
        font=("Arial", 16)
    )
    label_clientes.pack(pady=10)

    numero_clientes = ctk.CTkLabel(
        frame_clientes,
        text=str(contar_clientes()),
        font=("Arial", 24, "bold")
    )
    numero_clientes.pack()

    # -------- MEMBRESIAS ACTIVAS --------
    frame_membresias = ctk.CTkFrame(frame_dashboard, width=200, height=100)
    frame_membresias.grid(row=0, column=1, padx=20, pady=10)

    label_membresias = ctk.CTkLabel(
        frame_membresias,
        text="Membresías Activas",
        font=("Arial", 16)
    )
    label_membresias.pack(pady=10)

    numero_membresias = ctk.CTkLabel(
        frame_membresias,
        text=str(contar_membresias()),
        font=("Arial", 24, "bold")
    )
    numero_membresias.pack()

    # -------- PAGOS DEL DIA --------
    frame_pagos = ctk.CTkFrame(frame_dashboard, width=200, height=100)
    frame_pagos.grid(row=0, column=2, padx=20, pady=10)

    label_pagos = ctk.CTkLabel(
        frame_pagos,
        text="Pagos del Día",
        font=("Arial", 16)
    )
    label_pagos.pack(pady=10)

    numero_pagos = ctk.CTkLabel(
        frame_pagos,
        text="0",
        font=("Arial", 24, "bold")
    )
    numero_pagos.pack()

    # -------- SUSCRIPCIONES VENCIDAS --------
    frame_vencidas = ctk.CTkFrame(frame_dashboard, width=200, height=100)
    frame_vencidas.grid(row=0, column=3, padx=20, pady=10)

    label_vencidas = ctk.CTkLabel(
        frame_vencidas,
        text="Suscripciones Vencidas",
        font=("Arial", 16)
    )
    label_vencidas.pack(pady=10)

    numero_vencidas = ctk.CTkLabel(
        frame_vencidas,
        text=str(contar_suscripciones_vencidas()),
        font=("Arial", 24, "bold")
    )
    numero_vencidas.pack()

    # -------- BOTONES DEL SISTEMA --------

    boton_clientes = ctk.CTkButton(
        ventana,
        text="Clientes",
        width=200,
        height=40,
        command=lambda: abrir_ventana_clientes(ventana)
    )
    boton_clientes.pack(pady=10)

    boton_membresias = ctk.CTkButton(
        ventana,
        text="Membresías",
        width=200,
        height=40,
        command=lambda: abrir_ventana_membresias(ventana)
    )
    boton_membresias.pack(pady=10)

    boton_suscripciones = ctk.CTkButton(
        ventana,
        text="Suscripciones",
        width=200,
        height=40,
        command=lambda: abrir_ventana_suscripciones(ventana)
    )
    boton_suscripciones.pack(pady=10)

    boton_pagos = ctk.CTkButton(
        ventana,
        text="Pagos",
        width=200,
        height=40,
        command=lambda: abrir_ventana_pagos(ventana)
    )
    boton_pagos.pack(pady=10)
    
    #---BOTON DE BACKUP---
    ctk.CTkButton(
        ventana,
        text="Crear Backup",
        width=200,
        height=40,
        command=hacer_backup
    ).pack(pady=10)

    #----BOTÓN DE RECUPERAR BACKUP---

    ctk.CTkButton(
        ventana,
        text="Restaurar Backup",
        width=200,
        height=40,
        command=hacer_restauracion
    ).pack(pady=10)

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
    

