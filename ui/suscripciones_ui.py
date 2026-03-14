import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
import os

from modulos.suscripciones import (
    asignar_membresia,
    ver_estado_gimnasio,
    ver_clientes_vencidos,
    ver_dias_restantes,
    clientes_por_vencer,
    ver_suscripciones_completas,
    eliminar_suscripcion,
    ingresos_por_mes
)

CLAVE_EMERGENCIA = "12345"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "gym.db")


def abrir_ventana_suscripciones(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Suscripciones")
    ventana.state("zoomed")
    ventana.resizable(True, True)
    ventana.lift()
    ventana.focus_force()

    scroll = ctk.CTkScrollableFrame(ventana)
    scroll.pack(fill="both", expand=True)

    # ---------- HEADER ----------
    frame_header = ctk.CTkFrame(scroll, corner_radius=18)
    frame_header.pack(fill="x", padx=20, pady=(20, 10))

    ctk.CTkLabel(
        frame_header,
        text="Gestion de Suscripciones",
        font=("Segoe UI", 28, "bold")
    ).pack(side="left", padx=20, pady=20)

    ctk.CTkLabel(
        frame_header,
        text="Control de pagos, vencimientos e ingresos",
        font=("Segoe UI", 14),
        text_color="gray70"
    ).pack(side="left")

    ctk.CTkButton(
        frame_header,
        text="<- Volver al menu",
        width=170, height=40,
        font=("Segoe UI", 14, "bold"),
        corner_radius=12,
        fg_color="#2A2A2A",
        hover_color="#3A3A3A",
        command=ventana.destroy
    ).pack(side="right", padx=20, pady=20)

    # ---------- GRAFICO ----------
    frame_grafico = ctk.CTkFrame(scroll, corner_radius=18)
    frame_grafico.pack(fill="x", padx=20, pady=(10, 20))

    ctk.CTkLabel(
        frame_grafico,
        text="Ingresos mensuales",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=20, pady=(15, 5))

    grafico_container = ctk.CTkFrame(frame_grafico, corner_radius=15)
    grafico_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def cargar_grafico_ingresos():
        for widget in grafico_container.winfo_children():
            widget.destroy()

        datos    = ingresos_por_mes()
        meses    = ["Ene","Feb","Mar","Abr","May","Jun",
                    "Jul","Ago","Sep","Oct","Nov","Dic"]
        ingresos = [0] * 12

        for mes, total in datos:
            ingresos[int(mes) - 1] = float(total)

        fig, ax = plt.subplots(figsize=(9, 2.5))
        fig.patch.set_facecolor("#2b2b2b")
        ax.set_facecolor("#2b2b2b")
        ax.plot(meses, ingresos, marker="o", linewidth=3, color="#00D1FF")
        ax.set_title("Ingresos por mes", color="white")
        ax.set_xlabel("Mes", color="white")
        ax.set_ylabel("Ingresos ($)", color="white")
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        for spine in ax.spines.values():
            spine.set_color("white")
        ax.grid(True, alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=grafico_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    cargar_grafico_ingresos()

    # ---------- TABLA ----------
    frame_tabla = ctk.CTkFrame(scroll, corner_radius=18)
    frame_tabla.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(
        frame_tabla,
        text="Lista de Suscripciones",
        font=("Segoe UI", 20, "bold")
    ).pack(anchor="w", padx=20, pady=(15, 5))

    tabla_container = ctk.CTkFrame(frame_tabla)
    tabla_container.pack(fill="both", expand=True, padx=15, pady=10)

    columnas = ("ID", "Cliente", "Plan", "Inicio", "Vence", "Pagado", "Pendiente", "Estado")

    tabla = ttk.Treeview(
        tabla_container,
        columns=columnas,
        show="headings",
        height=10
    )

    for col in columnas:
        tabla.heading(col, text=col)

    tabla.column("ID",        anchor="center", width=50)
    tabla.column("Cliente",   anchor="center", width=180)
    tabla.column("Plan",      anchor="center", width=150)
    tabla.column("Inicio",    anchor="center", width=110)
    tabla.column("Vence",     anchor="center", width=110)
    tabla.column("Pagado",    anchor="center", width=100)
    tabla.column("Pendiente", anchor="center", width=100)
    tabla.column("Estado",    anchor="center", width=120)

    tabla.pack(fill="both", expand=True)

    # ── Recarga la tabla con TODAS las suscripciones ─────────────────────────
    def recargar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)
        for id_sus, nombre, plan, inicio, vence, pagado, pendiente in ver_suscripciones_completas():
            estado = "Activo" if float(pendiente) == 0 else "Pendiente"
            tabla.insert("", "end", values=(
                id_sus, nombre, plan, inicio, vence,
                f"${pagado:.2f}", f"${pendiente:.2f}", estado
            ))

    recargar_tabla()

    # ---------- BOTONES ----------
    frame_botones = ctk.CTkFrame(scroll, corner_radius=18)
    frame_botones.pack(fill="x", padx=20, pady=15)

    def limpiar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)

    def estado_gimnasio():
        limpiar_tabla()
        for id_sus, nombre, plan, vence, pagado, deuda in ver_estado_gimnasio():
            estado = "Activo" if deuda == 0 else "Pendiente"
            tabla.insert("", "end", values=(id_sus, nombre, plan, "", vence, pagado, "", estado))

    def ver_vencidos():
        limpiar_tabla()
        for nombre, fecha in ver_clientes_vencidos():
            tabla.insert("", "end", values=("", nombre, "", "", fecha, "", "", "Vencido"))

    def ver_dias():
        limpiar_tabla()
        for nombre, plan, estado in ver_dias_restantes():
            tabla.insert("", "end", values=("", nombre, plan, "", "", "", "", estado))

    def eliminar_seleccionada():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin seleccion", "Selecciona una suscripcion de la tabla primero.")
            return

        fila   = tabla.item(seleccion[0])["values"]
        id_sus = fila[0]
        nombre = fila[1]

        if not id_sus:
            messagebox.showwarning("Sin ID", "Esta fila no tiene un ID valido para eliminar.")
            return

        if messagebox.askyesno("Confirmar", f"Eliminar suscripcion #{id_sus} de '{nombre}'?"):
            eliminar_suscripcion(int(id_sus))
            recargar_tabla()
            cargar_grafico_ingresos()
            messagebox.showinfo("Eliminado", f"Suscripcion #{id_sus} eliminada correctamente.")

    # ── Popup agregar suscripcion ─────────────────────────────────────────────
    def abrir_popup_agregar():
        popup = ctk.CTkToplevel(ventana)
        popup.title("Nueva suscripcion")
        popup.geometry("420x440")
        popup.resizable(False, False)
        popup.lift()
        popup.focus_force()
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="Nueva suscripcion",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(20, 10))

        frame_form = ctk.CTkFrame(popup, corner_radius=12)
        frame_form.pack(fill="x", padx=20, pady=10)

        campos = [
            ("ID Cliente",                "Ej: 1"),
            ("ID Membresia",              "Ej: 1"),
            ("Precio total",              "Ej: 30.00"),
            ("Monto pagado",              "Ej: 30.00"),
            ("Fecha inicio (YYYY-MM-DD)", "Dejar vacio = hoy"),
        ]

        entries_popup = []
        for i, (label, placeholder) in enumerate(campos):
            ctk.CTkLabel(frame_form, text=label, font=("Segoe UI", 12)).grid(
                row=i, column=0, padx=15, pady=7, sticky="w"
            )
            entry = ctk.CTkEntry(frame_form, width=190, placeholder_text=placeholder)
            entry.grid(row=i, column=1, padx=15, pady=7)
            entries_popup.append(entry)

        e_cliente, e_membresia, e_precio, e_pagado, e_fecha = entries_popup

        def guardar():
            try:
                cliente   = int(e_cliente.get())
                membresia = int(e_membresia.get())
                precio    = float(e_precio.get())
                pagado    = float(e_pagado.get())
            except Exception:
                messagebox.showerror("Error", "Verifica que ID, precio y monto sean numeros validos.")
                return

            fecha = e_fecha.get().strip()
            if fecha == "":
                asignar_membresia(cliente, membresia, precio, pagado)
            else:
                asignar_membresia(cliente, membresia, precio, pagado, fecha)

            recargar_tabla()
            cargar_grafico_ingresos()
            popup.destroy()
            messagebox.showinfo(
                "Exito",
                "Suscripcion agregada.\nPresiona 'Actualizar' en el dashboard para ver el contador actualizado."
            )

        ctk.CTkButton(
            popup,
            text="Guardar suscripcion",
            height=42,
            font=("Segoe UI", 13, "bold"),
            fg_color="#1a7a1a",
            hover_color="#145214",
            command=guardar
        ).pack(pady=18)

    # Fila de botones de vista
    botones_vista = [
        ("Estado del gimnasio", estado_gimnasio),
        ("Clientes vencidos",   ver_vencidos),
        ("Dias restantes",      ver_dias),
        ("Ver todas",           recargar_tabla),
    ]

    for i, (txt, cmd) in enumerate(botones_vista):
        ctk.CTkButton(
            frame_botones, text=txt,
            width=165, height=40, command=cmd
        ).grid(row=0, column=i, padx=6, pady=10)

    # Agregar (verde)
    ctk.CTkButton(
        frame_botones,
        text="+ Agregar suscripcion",
        width=185, height=40,
        fg_color="#1a7a1a",
        hover_color="#145214",
        command=abrir_popup_agregar
    ).grid(row=0, column=len(botones_vista), padx=6, pady=10)

    # Eliminar (rojo)
    ctk.CTkButton(
        frame_botones,
        text="Eliminar suscripcion",
        width=185, height=40,
        fg_color="#C0392B",
        hover_color="#922B21",
        command=eliminar_seleccionada
    ).grid(row=0, column=len(botones_vista) + 1, padx=6, pady=10)

    # ---------- FORMULARIO FIJO (mantenido) ----------
    frame_asignar = ctk.CTkFrame(scroll, corner_radius=18)
    frame_asignar.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(
        frame_asignar,
        text="Asignar nueva membresia",
        font=("Segoe UI", 20, "bold")
    ).grid(row=0, column=0, columnspan=2, pady=(15, 10))

    labels = ["ID Cliente", "ID Membresia", "Precio", "Pagado", "Fecha inicio (YYYY-MM-DD)"]
    entries = []

    for i, texto in enumerate(labels):
        ctk.CTkLabel(frame_asignar, text=texto).grid(row=i+1, column=0, padx=15, pady=8)
        entry = ctk.CTkEntry(frame_asignar, width=200)
        entry.grid(row=i+1, column=1, padx=15, pady=8)
        entries.append(entry)

    entry_cliente, entry_membresia, entry_precio, entry_pagado, entry_fecha = entries

    def asignar():
        try:
            cliente   = int(entry_cliente.get())
            membresia = int(entry_membresia.get())
            precio    = float(entry_precio.get())
            pagado    = float(entry_pagado.get())
        except Exception:
            messagebox.showerror("Error", "Datos invalidos")
            return

        fecha = entry_fecha.get().strip()
        if fecha == "":
            asignar_membresia(cliente, membresia, precio, pagado)
        else:
            asignar_membresia(cliente, membresia, precio, pagado, fecha)

        for e in entries:
            e.delete(0, ctk.END)

        recargar_tabla()
        cargar_grafico_ingresos()
        messagebox.showinfo("Exito", "Membresia asignada correctamente.")

    ctk.CTkButton(
        frame_asignar,
        text="Asignar membresia",
        height=40,
        command=asignar
    ).grid(row=6, column=0, columnspan=2, pady=15)

    # ---------- ZONA DE PELIGRO ----------
    frame_emergencia = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#1a0000")
    frame_emergencia.pack(fill="x", padx=20, pady=(10, 30))

    ctk.CTkLabel(
        frame_emergencia,
        text="Zona de peligro",
        font=("Segoe UI", 16, "bold"),
        text_color="#FF4444"
    ).pack(anchor="w", padx=20, pady=(15, 2))

    ctk.CTkLabel(
        frame_emergencia,
        text="Esta accion borra TODOS los clientes, suscripciones y pagos. No se puede deshacer.",
        font=("Segoe UI", 12),
        text_color="gray60"
    ).pack(anchor="w", padx=20, pady=(0, 10))

    def borrar_todo():
        if not messagebox.askyesno(
            "Borrar toda la base de datos",
            "Estas seguro? Se eliminaran clientes, suscripciones, pagos y alertas.\nEsta accion NO se puede deshacer."
        ):
            return

        clave = simpledialog.askstring(
            "Contrasena de administrador",
            "Ingresa la contrasena para continuar:",
            show="*",
            parent=ventana
        )

        if clave is None:
            return

        if clave != CLAVE_EMERGENCIA:
            messagebox.showerror("Contrasena incorrecta", "La contrasena ingresada no es correcta.")
            return

        try:
            con = sqlite3.connect(DB_PATH)
            for t in ["pagos", "suscripciones", "alertas_enviadas", "membresias", "clientes"]:
                try:
                    con.execute(f"DELETE FROM {t}")
                    con.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}'")
                except sqlite3.OperationalError:
                    pass
            con.commit()
            con.close()

            recargar_tabla()
            cargar_grafico_ingresos()
            messagebox.showinfo("Listo", "Base de datos limpiada. IDs reiniciados desde 1.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo limpiar:\n{e}")

    ctk.CTkButton(
        frame_emergencia,
        text="BORRAR TODA LA BASE DE DATOS",
        height=45,
        font=("Segoe UI", 14, "bold"),
        fg_color="#8B0000",
        hover_color="#FF0000",
        command=borrar_todo
    ).pack(padx=20, pady=(0, 20))