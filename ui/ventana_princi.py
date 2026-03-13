import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ui.clientes_ui import abrir_ventana_clientes
from ui.pagos_ui import abrir_ventana_pagos
from ui.suscripciones_ui import abrir_ventana_suscripciones
from ui.membresias_ui import abrir_ventana_membresias

from modulos.clientes import contar_clientes
from modulos.membresias import contar_membresias
from modulos.suscripciones import contar_suscripciones_vencidas, contar_clientes_activos
from modulos.backup_db import crear_backup, restaurar_backup
from modulos.graficas import grafica_clientes
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter import messagebox
from PIL import Image, ImageTk
import os


def iniciar_ventana():

    ventana = ttk.Window(themename="darkly")
    ventana.title("Sistema de Gestión de Gimnasio")
    ventana.state("zoomed")

# ---------------- FUNCIONES ----------------

    def actualizar_dashboard():
        numero_clientes.config(text=str(contar_clientes()))
        numero_membresias.config(text=str(contar_membresias()))
        numero_vencidas.config(text=str(contar_suscripciones_vencidas()))
        numero_activos.config(text=str(contar_clientes_activos()))

        # limpiar gráfica anterior
        for widget in frame_grafica.winfo_children():
            widget.destroy()

        # volver a dibujar la grafica
        grafica_clientes(frame_grafica)

    def hacer_backup():
        try:
            ruta = crear_backup()
            messagebox.showinfo("Backup creado", f"Backup guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el backup:\n{e}")

    def hacer_restauracion():

        try:
            archivo = restaurar_backup()

            if archivo:
                messagebox.showinfo(
                    "Backup restaurado",
                    "Base restaurada correctamente.\nReinicia el sistema."
                )
                ventana.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo restaurar:\n{e}")

# ---------------- LAYOUT PRINCIPAL ----------------

    contenedor = ttk.Frame(ventana)
    contenedor.pack(fill="both", expand=True)

    contenedor.columnconfigure(1, weight=1)

# ---------------- SIDEBAR ----------------

    sidebar = ttk.Frame(contenedor, padding=30)
    sidebar.grid(row=0, column=0, sticky="ns")

    ttk.Label(
        sidebar,
        text="Panel de Control",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=(0,25))

    boton_style = {"width":22, "padding":10}

    ttk.Button(
        sidebar,
        text="👥 Clientes",
        bootstyle="primary-outline",
        command=lambda: abrir_ventana_clientes(ventana),
        **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar,
        text="🏷 Membresías",
        bootstyle="primary-outline",
        command=lambda: abrir_ventana_membresias(ventana),
        **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar,
        text="📋 Suscripciones",
        bootstyle="primary-outline",
        command=lambda: abrir_ventana_suscripciones(ventana),
        **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar,
        text="💳 Pagos",
        bootstyle="primary-outline",
        command=lambda: abrir_ventana_pagos(ventana),
        **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar,
        text="💾 Crear Backup",
        bootstyle="success",
        command=hacer_backup,
        **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar,
        text="♻ Restaurar Backup",
        bootstyle="warning",
        command=hacer_restauracion,
        **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar,
        text="❌ Salir",
        command=ventana.destroy,
        **boton_style
    ).pack(pady=6)

    # ---------- LOGO DEL GYM ABAJO DEL PANEL ----------
    ruta_logo = os.path.join("assets", "logo_gym.jpg")
    
    if os.path.exists(ruta_logo):
        
        imagen_logo = Image.open(ruta_logo)
        
        imagen_logo = imagen_logo.resize((160, 80))
        
        logo = ImageTk.PhotoImage(imagen_logo)
        
        label_logo = ttk.Label(sidebar, image=logo)
        label_logo.image = logo
        label_logo.pack(pady=(40, 10))

# ---------------- AREA PRINCIPAL ----------------

    area = ttk.Frame(contenedor, padding=(60,40))
    area.grid(row=0, column=1, sticky="nsew")

# ---------------- HEADER ----------------

    header = ttk.Frame(area)
    header.pack(fill="x", pady=(0,30))

    ttk.Label(
        header,
        text="Dashboard del Gimnasio",
        font=("Segoe UI",34,"bold"),
    ).pack(side="left")

    ttk.Button(
        header,
        text="Actualizar",
        bootstyle="info",
        command=actualizar_dashboard
    ).pack(side="right")

# ---------------- DASHBOARD CARDS ----------------

    dashboard = ttk.Frame(area)
    dashboard.pack(expand=True)

    dashboard.columnconfigure((0,1,2,3), weight=1)
    dashboard.rowconfigure(0, weight=1)

# -------- FUNCION CREAR TARJETAS --------

    def crear_card(parent, icono, titulo, valor):

        frame = ttk.Frame(
            parent,
            padding=35,
            
        )

        frame.grid_propagate(False)

        ttk.Label(
            frame,
            text=icono,
            font=("Segoe UI",34)
        ).pack(pady=(0,8))

        ttk.Label(
            frame,
            text=titulo,
            font=("Segoe UI",13)
        ).pack()

        numero = ttk.Label(
            frame,
            text=valor,
            font=("Segoe UI",42,"bold"),
            bootstyle="info"
        )
        numero.pack(pady=(10,0))

        return frame, numero

# -------- CARDS --------

    card_clientes, numero_clientes = crear_card(
        dashboard,"👥","Clientes Registrados",str(contar_clientes())
    )
    card_clientes.grid(row=0,column=0,padx=30,pady=60,sticky="nsew")

    card_membresias, numero_membresias = crear_card(
        dashboard,"🏷","Membresías Activas",str(contar_membresias())
    )
    card_membresias.grid(row=0,column=1,padx=30,pady=60,sticky="nsew")

    card_vencidas, numero_vencidas = crear_card(
        dashboard,"⚠","Suscripciones Vencidas",str(contar_suscripciones_vencidas())
    )
    card_vencidas.grid(row=0,column=2,padx=30,pady=60,sticky="nsew")


# -------- CARD CLIENTES ACTIVOS --------

    card_activos, numero_activos = crear_card(
        dashboard,
        "🔥",
        "Clientes Activos",
        str(contar_clientes_activos())
    )

    card_activos.grid(row=0, column=3, padx=30, pady=60, sticky="nsew")

# ---------------- ACTIVIDAD ----------------

    contenido_inferior = ttk.Frame(area)
    contenido_inferior.pack(fill="both", expand=True, pady=30)

    contenido_inferior.columnconfigure(0, weight=1)
    contenido_inferior.columnconfigure(1, weight=1)

    contenido_inferior.rowconfigure(0, weight=1)
    contenido_inferior.rowconfigure(1, weight=1)

    frame_grafica = ttk.Frame(
    contenido_inferior,
    padding=20,
    bootstyle="secondary"
    )
    
    frame_grafica.grid(row=0, column=1, sticky="n", padx=20)

    grafica_clientes(frame_grafica)

# -------- ACTIVIDAD --------

    actividad = ttk.Frame(contenido_inferior, padding=30)
    actividad.grid(row=0,column=0,rowspan=2, sticky="nw")

    frame_grafica = ttk.Frame(
    contenido_inferior,
    padding=20,
    bootstyle="secondary"
    )
    frame_grafica.grid(row=0, column=1, sticky="n", padx=20, pady=10)
    
    grafica_clientes(frame_grafica)

    ttk.Label(
        actividad,
        text="Actividad reciente",
        font=("Segoe UI",18,"bold")
    ).pack(anchor="w", pady=(0,20))

    ttk.Label(actividad,text="• Sistema iniciado").pack(anchor="w", pady=6)
    ttk.Label(actividad,text="• Clientes registrados").pack(anchor="w", pady=6)
    ttk.Label(actividad,text="• Membresías cargadas").pack(anchor="w", pady=6)
    ttk.Label(actividad,text="• Base de datos conectada").pack(anchor="w", pady=6)

# -------- FOTO DEL GIMNASIO --------

    ruta_gym = os.path.join("assets","gym.jpg")

    if os.path.exists(ruta_gym):

        imagen = Image.open(ruta_gym)
        imagen = imagen.resize((450,260), Image.LANCZOS)

        img_gym = ImageTk.PhotoImage(imagen)

        frame_gym = ttk.Frame(
            contenido_inferior,
            padding=20,
        )

        frame_gym.grid(row=1,column=1,sticky="n",padx=20, pady=20)

        ttk.Label(
            frame_gym,
            text="Nuestro Gimnasio",
            font=("Segoe UI",16,"bold")
        ).pack(pady=(0,10))

        label_gym = ttk.Label(frame_gym,image=img_gym)
        label_gym.image = img_gym
        label_gym.pack()

# ---------------- LOOP ----------------

    ventana.mainloop()