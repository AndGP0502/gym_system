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

        for widget in frame_grafica.winfo_children():
            widget.destroy()

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
    contenedor.rowconfigure(0, weight=1)

    # ---------------- SIDEBAR ----------------

    sidebar = ttk.Frame(contenedor, padding=30)
    sidebar.grid(row=0, column=0, sticky="ns")

    ttk.Label(
        sidebar,
        text="Software de Control A&D",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(0, 25))

    boton_style = {"width": 22, "padding": 10}

    ttk.Button(
        sidebar, text="👥 Clientes", bootstyle="primary-outline",
        command=lambda: abrir_ventana_clientes(ventana), **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="🏷 Membresías", bootstyle="primary-outline",
        command=lambda: abrir_ventana_membresias(ventana), **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="📋 Suscripciones", bootstyle="primary-outline",
        command=lambda: abrir_ventana_suscripciones(ventana), **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="💳 Pagos", bootstyle="primary-outline",
        command=lambda: abrir_ventana_pagos(ventana), **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar, text="💾 Crear Backup", bootstyle="success",
        command=hacer_backup, **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="♻ Restaurar Backup", bootstyle="warning",
        command=hacer_restauracion, **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar, text="❌ Salir",
        command=ventana.destroy, **boton_style
    ).pack(pady=6)

    # Logo del gym
    ruta_logo = os.path.join("assets", "logo_gym.jpg")
    if os.path.exists(ruta_logo):
        imagen_logo = Image.open(ruta_logo).resize((200, 200))
        logo = ImageTk.PhotoImage(imagen_logo)
        label_logo = ttk.Label(sidebar, image=logo)
        label_logo.image = logo
        label_logo.pack(pady=(30, 10))

    # ---------------- ÁREA PRINCIPAL CON SCROLL ----------------

    contenedor_scroll = ttk.Frame(contenedor)
    contenedor_scroll.grid(row=0, column=1, sticky="nsew")
    contenedor_scroll.rowconfigure(0, weight=1)
    contenedor_scroll.columnconfigure(0, weight=1)

    canvas = ttk.Canvas(contenedor_scroll)
    canvas.grid(row=0, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    area = ttk.Frame(canvas, padding=(40, 30))
    canvas.create_window((0, 0), window=area, anchor="nw")

    def actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    area.bind("<Configure>", actualizar_scroll)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ---------------- HEADER ----------------

    header = ttk.Frame(area)
    header.pack(fill="x", pady=(0, 20))

    ttk.Label(
        header,
        text="Dashboard del Gimnasio",
        font=("Segoe UI", 28, "bold"),
    ).pack(side="left")

    ttk.Button(
        header, text="🔄 Actualizar",
        bootstyle="info", command=actualizar_dashboard
    ).pack(side="right", padx=5)

    # ---------------- CARDS ----------------
    # Usamos pack + Frame de fila para que las 4 cards siempre quepan

    fila_cards = ttk.Frame(area)
    fila_cards.pack(fill="x", pady=(0, 30))

    # Las 4 columnas se expanden igual
    for i in range(4):
        fila_cards.columnconfigure(i, weight=1, uniform="card")

    def crear_card(parent, icono, titulo, valor, col):
        frame = ttk.Frame(parent, padding=25,)
        frame.grid(row=0, column=col, padx=12, pady=10, sticky="nsew")

        ttk.Label(frame, text=icono, font=("Segoe UI", 28)).pack(pady=(0, 6))
        ttk.Label(frame, text=titulo, font=("Segoe UI", 11)).pack()
        numero = ttk.Label(
            frame, text=valor,
            font=("Segoe UI", 36, "bold"),
            bootstyle="info"
        )
        numero.pack(pady=(8, 0))
        return frame, numero

    _, numero_clientes   = crear_card(fila_cards, "👥", "Clientes Registrados",   str(contar_clientes()),              0)
    _, numero_membresias = crear_card(fila_cards, "🏷", "Membresías Activas",     str(contar_membresias()),            1)
    _, numero_vencidas   = crear_card(fila_cards, "⚠️",  "Suscripciones Vencidas", str(contar_suscripciones_vencidas()), 2)
    _, numero_activos    = crear_card(fila_cards, "🔥", "Clientes Activos",        str(contar_clientes_activos()),      3)

    # ---------------- CONTENIDO INFERIOR ----------------

    contenido_inferior = ttk.Frame(area)
    contenido_inferior.pack(fill="both", expand=True, pady=10)
    contenido_inferior.columnconfigure(0, weight=1)
    contenido_inferior.columnconfigure(1, weight=1)

    # ---- Actividad reciente (izquierda) ----
    actividad = ttk.Frame(contenido_inferior, padding=30,)
    actividad.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

    ttk.Label(
        actividad,
        text="Actividad reciente",
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", pady=(0, 16))

    for item in [
        "✅ Sistema iniciado",
        "✅ Clientes registrados",
        "✅ Membresías cargadas",
        "✅ Base de datos conectada",
    ]:
        ttk.Label(actividad, text=item, font=("Segoe UI", 11)).pack(anchor="w", pady=5)

    # ---- Gráfica (derecha) ----
    frame_grafica = ttk.Frame(contenido_inferior, padding=20, bootstyle="secondary")
    frame_grafica.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

    grafica_clientes(frame_grafica)

    # ---- Foto del gimnasio (fila inferior, centrada) ----
    ruta_gym = os.path.join("assets", "gym.jpg")
    if os.path.exists(ruta_gym):
        imagen = Image.open(ruta_gym).resize((450, 260), Image.LANCZOS)
        img_gym = ImageTk.PhotoImage(imagen)

        frame_gym = ttk.Frame(area, padding=20)
        frame_gym.pack(pady=20)

        ttk.Label(
            frame_gym,
            text="Nuestro Gimnasio",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 10))

        label_gym = ttk.Label(frame_gym, image=img_gym)
        label_gym.image = img_gym
        label_gym.pack()

    # ---------------- LOOP ----------------
    ventana.mainloop()