import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from modulos.suscripciones import (
    asignar_membresia,
    ver_estado_gimnasio,
    ver_clientes_vencidos,
    ver_dias_restantes,
    clientes_por_vencer,
    ver_suscripciones_completas,
    ingresos_por_mes
)

def abrir_ventana_suscripciones(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Suscripciones")
    ventana.state("zoomed")
    ventana.resizable(True, True)
    ventana.configure(fg_color="#2d2d2d")

    ventana.lift()
    ventana.focus_force()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))
    ventana.grab_set()

    # ---------- SCROLL PRINCIPAL ----------
    scroll = ctk.CTkScrollableFrame(
        ventana,
        fg_color="#3f3f3f"
    )
    scroll.pack(fill="both", expand=True)

    # ---------- HEADER ----------
    frame_header = ctk.CTkFrame(
        scroll,
        fg_color="#343434",
        corner_radius=18,
        height=90
    )
    frame_header.pack(fill="x", padx=20, pady=(15, 10))

    titulo = ctk.CTkLabel(
        frame_header,
        text="GESTIÓN DE SUSCRIPCIONES",
        font=("Segoe UI", 30, "bold"),
        text_color="#00D1FF"
    )
    titulo.pack(side="left", padx=25, pady=20)

    subtitulo = ctk.CTkLabel(
        frame_header,
        text="Consulta estados, vencimientos y asigna membresías",
        font=("Segoe UI", 14),
        text_color="#B0B0B0"
    )
    subtitulo.pack(side="left", padx=(0, 10), pady=20)

    boton_volver = ctk.CTkButton(
        frame_header,
        text="← Volver al menú",
        width=170,
        height=40,
        corner_radius=12,
        fg_color="#2A2A2A",
        hover_color="#3A3A3A",
        font=("Segoe UI", 14, "bold"),
        command=ventana.destroy
    )
    boton_volver.pack(side="right", padx=20, pady=20)

    # ---------- CONTENEDOR PRINCIPAL ----------
    contenedor = ctk.CTkFrame(
        scroll,
        fg_color="#343434",
        corner_radius=18
    )
    contenedor.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ---------- BOTONES CONSULTA ----------
    frame_botones = ctk.CTkFrame(
        contenedor,
        fg_color="#3f3f3f",
        corner_radius=15
    )
    frame_botones.pack(fill="x", padx=20, pady=(20, 10))

    label_botones = ctk.CTkLabel(
        frame_botones,
        text="Consultas rápidas",
        font=("Segoe UI", 20, "bold"),
        text_color="white"
    )
    label_botones.pack(anchor="w", padx=20, pady=(15, 10))

    botones_grid = ctk.CTkFrame(frame_botones, fg_color="transparent")
    botones_grid.pack(padx=10, pady=(0, 15))

    # ---------- TABLA ----------
    frame_tabla = ctk.CTkFrame(
        contenedor,
        fg_color="#3f3f3f",
        corner_radius=15
    )
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

    label_tabla = ctk.CTkLabel(
        frame_tabla,
        text="Listado de suscripciones",
        font=("Segoe UI", 20, "bold"),
        text_color="white"
    )
    label_tabla.pack(anchor="w", padx=20, pady=(15, 10))

    tabla_container = ctk.CTkFrame(frame_tabla, fg_color="transparent")
    tabla_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    columnas = ("ID", "Cliente", "Plan", "Vence", "Pagado", "Estado")

    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background="#3a3a3a",
        foreground="white",
        fieldbackground="#3a3a3a",
        borderwidth=0,
        rowheight=34,
        font=("Segoe UI", 12)
    )

    style.configure(
        "Treeview.Heading",
        background="#111111",
        foreground="white",
        font=("Segoe UI", 13, "bold"),
        relief="flat"
    )

    style.map(
        "Treeview",
        background=[("selected", "#0A84FF")],
        foreground=[("selected", "white")]
    )

    tabla = ttk.Treeview(
        tabla_container,
        columns=columnas,
        show="headings",
        height=16
    )

    tabla.heading("ID", text="ID")
    tabla.heading("Cliente", text="Cliente")
    tabla.heading("Plan", text="Plan")
    tabla.heading("Vence", text="Vence")
    tabla.heading("Pagado", text="Pagado")
    tabla.heading("Estado", text="Estado")

    tabla.column("ID", width=80, anchor="center")
    tabla.column("Cliente", width=260, anchor="center")
    tabla.column("Plan", width=180, anchor="center")
    tabla.column("Vence", width=160, anchor="center")
    tabla.column("Pagado", width=130, anchor="center")
    tabla.column("Estado", width=180, anchor="center")

    tabla.tag_configure("activo", foreground="#00E676")
    tabla.tag_configure("vencido", foreground="#FF5252")
    tabla.tag_configure("por_vencer", foreground="#FFD600")
    tabla.tag_configure("par", background="#3a3a3a")
    tabla.tag_configure("impar", background="#444444")

    scroll_y = ttk.Scrollbar(tabla_container, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll_y.set)

    tabla.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    # ---------- FORMULARIO + GRÁFICO ----------
    frame_asignar = ctk.CTkFrame(
        contenedor,
        fg_color="#3f3f3f",
        corner_radius=15
    )
    frame_asignar.pack(fill="x", padx=20, pady=(10, 20))

    # columnas del formulario
    for col in range(6):
        frame_asignar.grid_columnconfigure(col, weight=1)

    titulo_form = ctk.CTkLabel(
        frame_asignar,
        text="Asignar membresía",
        font=("Segoe UI", 20, "bold"),
        text_color="white"
    )
    titulo_form.grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 20))

    ctk.CTkLabel(frame_asignar, text="ID Cliente", font=("Segoe UI", 14, "bold")).grid(
        row=1, column=0, padx=20, pady=10, sticky="w"
    )
    entry_cliente = ctk.CTkEntry(
        frame_asignar,
        width=220,
        height=38,
        placeholder_text="Ingrese ID del cliente"
    )
    entry_cliente.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(frame_asignar, text="ID Membresía", font=("Segoe UI", 14, "bold")).grid(
        row=1, column=2, padx=20, pady=10, sticky="w"
    )
    entry_membresia = ctk.CTkEntry(
        frame_asignar,
        width=220,
        height=38,
        placeholder_text="Ingrese ID de membresía"
    )
    entry_membresia.grid(row=1, column=3, padx=10, pady=10)

    ctk.CTkLabel(frame_asignar, text="Precio", font=("Segoe UI", 14, "bold")).grid(
        row=2, column=0, padx=20, pady=10, sticky="w"
    )
    entry_precio = ctk.CTkEntry(
        frame_asignar,
        width=220,
        height=38,
        placeholder_text="Ingrese precio total"
    )
    entry_precio.grid(row=2, column=1, padx=10, pady=10)

    ctk.CTkLabel(frame_asignar, text="Pagado", font=("Segoe UI", 14, "bold")).grid(
        row=2, column=2, padx=20, pady=10, sticky="w"
    )
    entry_pagado = ctk.CTkEntry(
        frame_asignar,
        width=220,
        height=38,
        placeholder_text="Ingrese valor pagado"
    )
    entry_pagado.grid(row=2, column=3, padx=10, pady=10)

    # ---------- PANEL DERECHO DEL GRÁFICO ----------
    frame_grafico = ctk.CTkFrame(
        frame_asignar,
        fg_color="#343434",
        corner_radius=12
    )
    frame_grafico.grid(row=0, column=4, rowspan=4, columnspan=2, padx=(20, 20), pady=20, sticky="nsew")

    titulo_grafico = ctk.CTkLabel(
        frame_grafico,
        text="Ingresos mensuales",
        font=("Segoe UI", 18, "bold"),
        text_color="white"
    )
    titulo_grafico.pack(anchor="w", padx=15, pady=(12, 8))

    grafico_container = ctk.CTkFrame(frame_grafico, fg_color="transparent")
    grafico_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    canvas_grafico = None

    # ---------- FUNCIONES ----------
    def limpiar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)

    def insertar_filas(datos_procesados):
        limpiar_tabla()
        for i, fila in enumerate(datos_procesados):
            tags = list(fila["tags"])
            tags.append("par" if i % 2 == 0 else "impar")

            tabla.insert(
                "",
                "end",
                values=fila["values"],
                tags=tuple(tags)
            )

    def estado_gimnasio():
        datos = ver_estado_gimnasio()
        filas = []

        for id_sus, nombre, plan, vence, pagado, deuda in datos:
            if deuda > 0:
                estado = "Pendiente"
                tag = "vencido"
            else:
                estado = "Activo"
                tag = "activo"

            filas.append({
                "values": (id_sus, nombre, plan, vence, f"${float(pagado):.2f}", estado),
                "tags": (tag,)
            })

        insertar_filas(filas)

    def ver_vencidos():
        datos = ver_clientes_vencidos()
        filas = []

        for nombre, fecha in datos:
            filas.append({
                "values": ("", nombre, "", fecha, "", "Vencido"),
                "tags": ("vencido",)
            })

        insertar_filas(filas)

    def ver_por_vencer():
        datos = clientes_por_vencer()
        filas = []

        for nombre, plan, dias in datos:
            filas.append({
                "values": ("", nombre, plan, "", "", f"Vence en {dias} días"),
                "tags": ("por_vencer",)
            })

        insertar_filas(filas)

    def ver_dias():
        datos = ver_dias_restantes()
        filas = []

        for nombre, plan, estado in datos:
            if "Vencido" in estado:
                tag = "vencido"
            elif "Vence en" in estado:
                tag = "por_vencer"
            else:
                tag = "activo"

            filas.append({
                "values": ("", nombre, plan, "", "", estado),
                "tags": (tag,)
            })

        insertar_filas(filas)

    def ver_completas():
        datos = ver_suscripciones_completas()
        filas = []

        for id_s, cliente, plan, inicio, vence, pagado, deuda in datos:
            if deuda > 0:
                estado = "Pendiente"
                tag = "vencido"
            else:
                estado = "Completa"
                tag = "activo"

            filas.append({
                "values": (id_s, cliente, plan, vence, f"${float(pagado):.2f}", estado),
                "tags": (tag,)
            })

        insertar_filas(filas)

    botones = [
        ("Estado del gimnasio", estado_gimnasio, "#0A84FF"),
        ("Clientes vencidos", ver_vencidos, "#FF3B30"),
        ("Clientes por vencer", ver_por_vencer, "#3B82F6"),
        ("Días restantes", ver_dias, "#A855F7"),
        ("Suscripciones completas", ver_completas, "#22C55E")
    ]

    for i, (texto, funcion, color) in enumerate(botones):
        ctk.CTkButton(
            botones_grid,
            text=texto,
            width=190,
            height=42,
            corner_radius=12,
            fg_color=color,
            hover_color="#333333",
            font=("Segoe UI", 13, "bold"),
            command=funcion
        ).grid(row=0, column=i, padx=8, pady=8)

    def cargar_grafico_ingresos():
        nonlocal canvas_grafico

        meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

        ingresos_mes = [0] * 12

        try:
            conexion = sqlite3.connect("gym.db")
            cursor = conexion.cursor()

            # Ajustado para trabajar con una tabla pagos que tenga:
            # fecha_pago y monto
            cursor.execute("""
                SELECT strftime('%m', fecha_pago) AS mes, SUM(monto) 
                FROM pagos
                GROUP BY strftime('%m', fecha_pago)
                ORDER BY mes
            """)
            datos = cursor.fetchall()
            conexion.close()

            for mes, total in datos:
                if mes is not None:
                    ingresos_mes[int(mes) - 1] = float(total)

        except Exception:
            pass

        if canvas_grafico is not None:
            canvas_grafico.get_tk_widget().destroy()

        fig = Figure(figsize=(5.5, 3.2), dpi=100)
        ax = fig.add_subplot(111)

        fig.patch.set_facecolor("#343434")
        ax.set_facecolor("#343434")

        ax.plot(meses_nombres, ingresos_mes, marker="o", linewidth=2)

        ax.set_title("Línea de ingresos", color="white", fontsize=12, pad=10)
        ax.set_xlabel("Mes", color="white")
        ax.set_ylabel("Ingresos ($)", color="white")

        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")

        for spine in ax.spines.values():
            spine.set_color("white")

        ax.grid(True, alpha=0.3)

        fig.tight_layout()

        canvas_grafico = FigureCanvasTkAgg(fig, master=grafico_container)
        canvas_grafico.draw()
        canvas_grafico.get_tk_widget().pack(fill="both", expand=True)

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

        messagebox.showinfo("Éxito", "Membresía asignada correctamente")

        entry_cliente.delete(0, ctk.END)
        entry_membresia.delete(0, ctk.END)
        entry_precio.delete(0, ctk.END)
        entry_pagado.delete(0, ctk.END)

        cargar_grafico_ingresos()

    ctk.CTkButton(
        frame_asignar,
        text="Asignar membresía",
        width=220,
        height=42,
        corner_radius=12,
        fg_color="#00BCD4",
        hover_color="#0097A7",
        font=("Segoe UI", 14, "bold"),
        command=asignar
    ).grid(row=3, column=0, columnspan=4, pady=20)

    # cargar gráfico al abrir
    cargar_grafico_ingresos()