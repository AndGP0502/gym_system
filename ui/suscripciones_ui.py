import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
import json
import os
from datetime import datetime

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

import sys as _sys

def _get_db_path():
    if getattr(_sys, 'frozen', False):
        return os.path.join(os.path.dirname(_sys.executable), "gym.db")
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, "..", "gym.db")
    return os.path.normpath(candidate)

def _get_config_path():
    if getattr(_sys, 'frozen', False):
        return os.path.join(os.path.dirname(_sys.executable), "config.json")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "config.json"))

DB_PATH     = _get_db_path()
CONFIG_PATH = _get_config_path()


def leer_clave() -> str:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("clave_emergencia", "12345")
    except Exception:
        return "12345"


def guardar_clave(nueva_clave: str):
    config = {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        pass
    config["clave_emergencia"] = nueva_clave
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def validar_fecha(fecha_str: str) -> str | None:
    fecha_str = fecha_str.strip()
    if not fecha_str:
        return None
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
    for fmt in formatos:
        try:
            dt = datetime.strptime(fecha_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return False


def abrir_ventana_suscripciones(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Suscripciones")
    ventana.state("zoomed")
    ventana.resizable(True, True)

    ventana.attributes("-topmost", True)
    ventana.after(300, lambda: ventana.attributes("-topmost", False))
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    def traer_al_frente():
        ventana.attributes("-topmost", True)
        ventana.lift()
        ventana.focus_force()
        ventana.after(200, lambda: ventana.attributes("-topmost", False))

    # FIX: reemplazar CTkScrollableFrame por Canvas + Scrollbar nativo.
    # CTkScrollableFrame interfiere con ttk.Treeview causando distorsión
    # de columnas y letras cortadas al hacer scroll rápido.
    canvas_principal = tk.Canvas(ventana, highlightthickness=0, bg="#2b2b2b")
    scrollbar_principal = ttk.Scrollbar(ventana, orient="vertical",
                                        command=canvas_principal.yview)
    canvas_principal.configure(yscrollcommand=scrollbar_principal.set)

    scrollbar_principal.pack(side="right", fill="y")
    canvas_principal.pack(side="left", fill="both", expand=True)

    scroll = ctk.CTkFrame(canvas_principal, fg_color="#2b2b2b")
    scroll_id = canvas_principal.create_window((0, 0), window=scroll, anchor="nw")

    def _ajustar_scroll(event=None):
        canvas_principal.configure(scrollregion=canvas_principal.bbox("all"))

    def _ajustar_ancho(event):
        canvas_principal.itemconfig(scroll_id, width=event.width)

    scroll.bind("<Configure>", _ajustar_scroll)
    canvas_principal.bind("<Configure>", _ajustar_ancho)

    # FIX SCROLL: scroll localizado al canvas, no bind_all
    def _scroll_principal(event):
        if canvas_principal.winfo_exists():
            canvas_principal.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas_principal.bind("<MouseWheel>", _scroll_principal)
    scroll.bind("<MouseWheel>", _scroll_principal)

    # FIX: helper reutilizable para dar scroll local a cada Treeview
    def _scroll_local_treeview(treeview):
        def _on_enter(e):
            def _tv_scroll(ev):
                treeview.yview_scroll(int(-1 * (ev.delta / 120)), "units")
                return "break"
            ventana.bind("<MouseWheel>", _tv_scroll)
        def _on_leave(e):
            ventana.unbind("<MouseWheel>")
        treeview.bind("<Enter>", _on_enter)
        treeview.bind("<Leave>", _on_leave)

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

    # FIX: estilo con nombre propio para no contaminar otras ventanas
    style = ttk.Style()
    style.configure("Sus.Treeview",         font=("Segoe UI", 11), rowheight=34)
    style.configure("Sus.Treeview.Heading", font=("Segoe UI", 11, "bold"))

    columnas = ("ID", "Cliente", "Plan", "Inicio", "Vence", "Pagado", "Pendiente", "Estado")

    tabla = ttk.Treeview(
        tabla_container,
        columns=columnas,
        show="headings",
        height=10,
        style="Sus.Treeview"
    )

    for col in columnas:
        tabla.heading(col, text=col)

    tabla.column("ID",        anchor="center", width=50,  minwidth=40)
    tabla.column("Cliente",   anchor="w",      width=180, minwidth=80)
    tabla.column("Plan",      anchor="w",      width=150, minwidth=80)
    tabla.column("Inicio",    anchor="center", width=110, minwidth=80)
    tabla.column("Vence",     anchor="center", width=110, minwidth=80)
    tabla.column("Pagado",    anchor="center", width=100, minwidth=60)
    tabla.column("Pendiente", anchor="center", width=100, minwidth=60)
    tabla.column("Estado",    anchor="center", width=120, minwidth=60)

    sb_tabla = ttk.Scrollbar(tabla_container, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=sb_tabla.set)
    tabla.pack(side="left", fill="both", expand=True)
    sb_tabla.pack(side="right", fill="y")

    _scroll_local_treeview(tabla)

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
            messagebox.showwarning("Sin seleccion", "Selecciona una suscripcion de la tabla primero.", parent=ventana)
            traer_al_frente()
            return
        fila   = tabla.item(seleccion[0])["values"]
        id_sus = fila[0]
        nombre = fila[1]
        if not id_sus:
            messagebox.showwarning("Sin ID", "Esta fila no tiene un ID valido para eliminar.", parent=ventana)
            traer_al_frente()
            return
        if messagebox.askyesno("Confirmar", f"Eliminar suscripcion #{id_sus} de '{nombre}'?", parent=ventana):
            eliminar_suscripcion(int(id_sus))
            recargar_tabla()
            cargar_grafico_ingresos()
            messagebox.showinfo("Eliminado", f"Suscripcion #{id_sus} eliminada correctamente.", parent=ventana)
        traer_al_frente()

    def abrir_popup_agregar():
        popup = ctk.CTkToplevel(ventana)
        popup.title("Nueva suscripcion")
        popup.geometry("420x460")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.after(300, lambda: popup.attributes("-topmost", False))
        popup.lift()
        popup.focus_force()

        ctk.CTkLabel(popup, text="Nueva suscripcion", font=("Segoe UI", 20, "bold")).pack(pady=(20, 10))

        frame_form = ctk.CTkFrame(popup, corner_radius=12)
        frame_form.pack(fill="x", padx=20, pady=10)

        campos = [
            "ID Cliente",
            "ID Membresia",
            "Precio total",
            "Monto pagado",
            "Fecha inicio (YYYY-MM-DD, vacio=hoy)",
        ]

        entries_popup = []
        for i, label in enumerate(campos):
            ctk.CTkLabel(frame_form, text=label, font=("Segoe UI", 12)).grid(
                row=i, column=0, padx=15, pady=7, sticky="w"
            )
            entry = ctk.CTkEntry(frame_form, width=190)
            entry.grid(row=i, column=1, padx=15, pady=7)
            entries_popup.append(entry)

        e_cliente, e_membresia, e_precio, e_pagado, e_fecha = entries_popup

        lbl_error = ctk.CTkLabel(popup, text="", text_color="#FF4444", font=("Segoe UI", 12))
        lbl_error.pack(pady=(0, 5))

        def guardar():
            val_cliente   = e_cliente.get().strip()
            val_membresia = e_membresia.get().strip()
            val_precio    = e_precio.get().strip()
            val_pagado    = e_pagado.get().strip()
            val_fecha     = e_fecha.get().strip()

            if not val_cliente or not val_membresia or not val_precio or not val_pagado:
                lbl_error.configure(text="Completa todos los campos obligatorios.")
                return
            try:
                cliente   = int(val_cliente)
                membresia = int(val_membresia)
                precio    = float(val_precio)
                pagado    = float(val_pagado)
            except ValueError:
                lbl_error.configure(text="ID debe ser entero, precio y pagado deben ser numeros.")
                return

            fecha_validada = validar_fecha(val_fecha)
            if fecha_validada is False:
                lbl_error.configure(
                    text="Formato de fecha inválido. Usa YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY."
                )
                return

            asignar_membresia(cliente, membresia, precio, pagado, fecha_validada)
            recargar_tabla()
            cargar_grafico_ingresos()
            popup.destroy()
            traer_al_frente()
            messagebox.showinfo(
                "Exito",
                "Suscripcion agregada correctamente.\nPresiona 'Actualizar' en el dashboard para ver el contador.",
                parent=ventana
            )

        ctk.CTkButton(
            popup,
            text="Guardar suscripcion",
            height=42,
            font=("Segoe UI", 13, "bold"),
            fg_color="#1a7a1a",
            hover_color="#145214",
            command=guardar
        ).pack(pady=15)

    def abrir_popup_editar_fechas():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin seleccion",
                "Selecciona una suscripcion de la tabla primero.", parent=ventana)
            traer_al_frente()
            return
        fila   = tabla.item(seleccion[0])["values"]
        id_sus = fila[0]
        nombre = fila[1]
        inicio_actual = fila[3]
        vence_actual  = fila[4]
        if not id_sus:
            messagebox.showwarning("Sin ID", "Esta fila no tiene ID valido.", parent=ventana)
            traer_al_frente()
            return

        popup = ctk.CTkToplevel(ventana)
        popup.title("Editar fechas")
        popup.geometry("460x260")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.after(300, lambda: popup.attributes("-topmost", False))
        popup.lift()
        popup.focus_force()

        ctk.CTkLabel(popup, text=f"Editar fechas — Suscripcion #{id_sus}",
                     font=("Segoe UI", 16, "bold")).pack(pady=(20, 4))
        ctk.CTkLabel(popup, text=nombre,
                     font=("Segoe UI", 13), text_color="gray70").pack(pady=(0, 14))

        frame_f = ctk.CTkFrame(popup, corner_radius=12)
        frame_f.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(frame_f, text="Fecha inicio (YYYY-MM-DD):",
                     font=("Segoe UI", 12)).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        entry_inicio = ctk.CTkEntry(frame_f, width=180)
        entry_inicio.grid(row=0, column=1, padx=15, pady=10)
        entry_inicio.insert(0, inicio_actual)

        ctk.CTkLabel(frame_f, text="Fecha vence (YYYY-MM-DD):",
                     font=("Segoe UI", 12)).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        entry_vence = ctk.CTkEntry(frame_f, width=180)
        entry_vence.grid(row=1, column=1, padx=15, pady=10)
        entry_vence.insert(0, vence_actual)

        lbl_err = ctk.CTkLabel(popup, text="", text_color="#FF4444", font=("Segoe UI", 11))
        lbl_err.pack()

        def guardar_fechas():
            fi = validar_fecha(entry_inicio.get().strip())
            fv = validar_fecha(entry_vence.get().strip())
            if fi is False or fv is False:
                lbl_err.configure(
                    text="Formato invalido. Usa YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY.")
                return
            if not fi or not fv:
                lbl_err.configure(text="Ambas fechas son obligatorias.")
                return
            con = sqlite3.connect(DB_PATH)
            con.execute(
                "UPDATE suscripciones SET fecha_inicio=?, fecha_vencimiento=? WHERE id=?",
                (fi, fv, int(id_sus))
            )
            con.commit()
            con.close()
            popup.destroy()
            recargar_tabla()
            cargar_grafico_ingresos()
            traer_al_frente()
            messagebox.showinfo("Guardado", "Fechas actualizadas correctamente.", parent=ventana)

        ctk.CTkButton(
            popup, text="Guardar fechas", height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color="#0d6efd", hover_color="#0b5ed7",
            command=guardar_fechas
        ).pack(pady=12)

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
        ).grid(row=0, column=i, padx=6, pady=(10, 4))

    ctk.CTkButton(
        frame_botones,
        text="+ Agregar suscripcion",
        width=185, height=40,
        fg_color="#1a7a1a",
        hover_color="#145214",
        command=abrir_popup_agregar
    ).grid(row=1, column=0, padx=6, pady=(4, 10))

    ctk.CTkButton(
        frame_botones,
        text="Eliminar suscripcion",
        width=185, height=40,
        fg_color="#C0392B",
        hover_color="#922B21",
        command=eliminar_seleccionada
    ).grid(row=1, column=1, padx=6, pady=(4, 10))

    ctk.CTkButton(
        frame_botones,
        text="Editar fechas",
        width=185, height=40,
        fg_color="#0d6efd",
        hover_color="#0b5ed7",
        command=abrir_popup_editar_fechas
    ).grid(row=1, column=2, padx=6, pady=(4, 10))

    # ---------- FORMULARIO FIJO ----------
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
        val_c  = entry_cliente.get().strip()
        val_m  = entry_membresia.get().strip()
        val_p  = entry_precio.get().strip()
        val_pa = entry_pagado.get().strip()

        if not val_c or not val_m or not val_p or not val_pa:
            messagebox.showerror("Error", "Completa todos los campos obligatorios.", parent=ventana)
            traer_al_frente()
            return
        try:
            cliente   = int(val_c)
            membresia = int(val_m)
            precio    = float(val_p)
            pagado    = float(val_pa)
        except ValueError:
            messagebox.showerror("Error", "ID debe ser entero, precio y pagado deben ser numeros.", parent=ventana)
            traer_al_frente()
            return

        val_fecha_raw  = entry_fecha.get().strip()
        fecha_validada = validar_fecha(val_fecha_raw)
        if fecha_validada is False:
            messagebox.showerror(
                "Error",
                "Formato de fecha inválido.\nUsa YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY.",
                parent=ventana
            )
            traer_al_frente()
            return

        asignar_membresia(cliente, membresia, precio, pagado, fecha_validada)
        for e in entries:
            e.delete(0, ctk.END)
        recargar_tabla()
        cargar_grafico_ingresos()
        traer_al_frente()
        messagebox.showinfo("Exito", "Membresia asignada correctamente.", parent=ventana)

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
    ).pack(anchor="w", padx=20, pady=(0, 15))

    ctk.CTkLabel(
        frame_emergencia,
        text="Cambiar contraseña de administrador",
        font=("Segoe UI", 13, "bold"),
        text_color="#FF8888"
    ).pack(anchor="w", padx=20, pady=(0, 8))

    frame_clave = ctk.CTkFrame(frame_emergencia, fg_color="transparent")
    frame_clave.pack(fill="x", padx=20, pady=(0, 20))

    entry_clave_actual = ctk.CTkEntry(
        frame_clave, width=200, height=38,
        placeholder_text="Contraseña actual", show="*"
    )
    entry_clave_actual.pack(side="left", padx=(0, 8))

    entry_clave_nueva = ctk.CTkEntry(
        frame_clave, width=200, height=38,
        placeholder_text="Nueva contraseña", show="*"
    )
    entry_clave_nueva.pack(side="left", padx=(0, 8))

    entry_clave_confirmar = ctk.CTkEntry(
        frame_clave, width=200, height=38,
        placeholder_text="Confirmar nueva contraseña", show="*"
    )
    entry_clave_confirmar.pack(side="left", padx=(0, 8))

    def cambiar_clave():
        actual     = entry_clave_actual.get().strip()
        nueva      = entry_clave_nueva.get().strip()
        confirmar  = entry_clave_confirmar.get().strip()
        clave_real = leer_clave()
        if actual != clave_real:
            messagebox.showerror("Error", "La contraseña actual es incorrecta.", parent=ventana)
            traer_al_frente(); return
        if not nueva:
            messagebox.showwarning("Advertencia", "La nueva contraseña no puede estar vacía.", parent=ventana)
            traer_al_frente(); return
        if nueva != confirmar:
            messagebox.showerror("Error", "La nueva contraseña y la confirmación no coinciden.", parent=ventana)
            traer_al_frente(); return
        guardar_clave(nueva)
        entry_clave_actual.delete(0, ctk.END)
        entry_clave_nueva.delete(0, ctk.END)
        entry_clave_confirmar.delete(0, ctk.END)
        messagebox.showinfo("Éxito", "Contraseña actualizada y guardada correctamente.", parent=ventana)
        traer_al_frente()

    ctk.CTkButton(
        frame_clave,
        text="Cambiar",
        width=110, height=38,
        fg_color="#8B4500",
        hover_color="#A05200",
        command=cambiar_clave
    ).pack(side="left")

    def borrar_todo():
        if not messagebox.askyesno(
            "Borrar toda la base de datos",
            "Estas seguro? Se eliminaran clientes, suscripciones, pagos y alertas.\nEsta accion NO se puede deshacer.",
            parent=ventana
        ):
            traer_al_frente(); return

        clave = simpledialog.askstring(
            "Contrasena de administrador",
            "Ingresa la contrasena para continuar:",
            show="*", parent=ventana
        )
        if clave is None:
            traer_al_frente(); return
        if clave != leer_clave():
            messagebox.showerror("Contrasena incorrecta", "La contrasena ingresada no es correcta.", parent=ventana)
            traer_al_frente(); return

        try:
            con = sqlite3.connect(DB_PATH)
            con.execute("PRAGMA foreign_keys = OFF")
            for t in ["pagos", "alertas_enviadas", "suscripciones", "membresias", "clientes"]:
                try:
                    con.execute(f"DELETE FROM {t}")
                    con.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}'")
                except sqlite3.OperationalError:
                    pass
            con.execute("PRAGMA foreign_keys = ON")
            con.commit()
            con.close()
            recargar_tabla()
            cargar_grafico_ingresos()
            traer_al_frente()
            messagebox.showinfo("Listo", "Base de datos limpiada. IDs reiniciados desde 1.", parent=ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo limpiar:\n{e}", parent=ventana)
            traer_al_frente()

    ctk.CTkButton(
        frame_emergencia,
        text="BORRAR TODA LA BASE DE DATOS",
        height=45,
        font=("Segoe UI", 14, "bold"),
        fg_color="#8B0000",
        hover_color="#FF0000",
        command=borrar_todo
    ).pack(padx=20, pady=(0, 20))

    # FIX FINAL: propagar scroll al canvas desde frames CTk no-Treeview
    def _propagar(widget):
        if isinstance(widget, ttk.Treeview):
            return
        try:
            widget.bind("<MouseWheel>", _scroll_principal)
        except Exception:
            pass
        for hijo in widget.winfo_children():
            _propagar(hijo)

    ventana.after(150, lambda: _propagar(scroll))