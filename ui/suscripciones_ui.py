import customtkinter as ctk
from tkinter import ttk, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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


def abrir_ventana_suscripciones(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Suscripciones")
    ventana.state("zoomed")
    ventana.resizable(True, True)
    ventana.lift()
    ventana.focus_force()

    # ---------- SCROLL PRINCIPAL ----------
    scroll = ctk.CTkScrollableFrame(ventana)
    scroll.pack(fill="both", expand=True)

    # ---------- TITULO ----------
    titulo = ctk.CTkLabel(
        scroll,
        text="Ingresos mensuales",
        font=("Segoe UI", 26, "bold")
    )
    titulo.pack(pady=(20, 10))

    # ---------- GRAFICO ----------
    frame_grafico = ctk.CTkFrame(scroll, height=250)
    frame_grafico.pack(fill="x", padx=20, pady=(0, 20))
    frame_grafico.pack_propagate(False)

    grafico_container = ctk.CTkFrame(frame_grafico)
    grafico_container.pack(fill="both", expand=True, padx=10, pady=10)
    grafico_container.pack_propagate(False)

    def cargar_grafico_ingresos():

        if not ventana.winfo_exists():
            return

        try:
           for widget in grafico_container.winfo_children():
            widget.destroy()
        except:
            return

        datos = ingresos_por_mes()

        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

        ingresos = [0] * 12

        for mes, total in datos:
            if mes is not None and total is not None:
                ingresos[int(mes) - 1] = float(total)

        fig, ax = plt.subplots(figsize=(9, 2.4))
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

        # ---------- TOOLTIP ----------
        anotacion = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="#1f1f1f", ec="white"),
            color="white"
        )
        anotacion.set_visible(False)

        def mover_mouse(event):

            if event.inaxes == ax and event.xdata is not None:

               for i, valor in enumerate(ingresos):

                  if abs(event.xdata - i) < 0.3:

                    anotacion.xy = (i, valor)
                    anotacion.set_text(f"{meses[i]} : ${valor:.2f}")
                    anotacion.set_visible(True)

                    fig.canvas.draw_idle()
                    return

            anotacion.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", mover_mouse)

        plt.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=grafico_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------- TABLA ----------
    columnas = ("ID", "Cliente", "Plan", "Vence", "Pagado", "Estado")

    frame_tabla = ctk.CTkFrame(scroll)
    frame_tabla.pack(fill="x", padx=20, pady=10)

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
        show="headings",
        height=10
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

    # colores de estado
    tabla.tag_configure("activo", foreground="#2ecc71")
    tabla.tag_configure("vencido", foreground="#e74c3c")
    tabla.tag_configure("por_vencer", foreground="#f1c40f")

    # SCROLL VERTICAL
    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll_y.set)

    # SCROLL HORIZONTAL
    scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)
    tabla.configure(xscrollcommand=scroll_x.set)

    # POSICIONES
    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    # ---------- RUEDA DEL MOUSE ----------
    def _on_mousewheel_principal(event):
        scroll._parent_canvas.yview_scroll(int(-1 * (event.delta / 5)), "units")
        return "break"

    def _on_mousewheel_principal_linux_up(event):
        scroll._parent_canvas.yview_scroll(-1, "units")
        return "break"

    def _on_mousewheel_principal_linux_down(event):
        scroll._parent_canvas.yview_scroll(1, "units")
        return "break"

    def _on_mousewheel_tabla(event):
        tabla.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _on_mousewheel_tabla_linux_up(event):
        tabla.yview_scroll(-1, "units")
        return "break"

    def _on_mousewheel_tabla_linux_down(event):
        tabla.yview_scroll(1, "units")
        return "break"

    def activar_scroll_tabla(event):
        ventana.bind_all("<MouseWheel>", _on_mousewheel_tabla)
        ventana.bind_all("<Button-4>", _on_mousewheel_tabla_linux_up)
        ventana.bind_all("<Button-5>", _on_mousewheel_tabla_linux_down)

    def activar_scroll_principal(event=None):
       ventana.bind_all("<MouseWheel>", _on_mousewheel_principal)
       ventana.bind_all("<Button-4>", _on_mousewheel_principal_linux_up)
       ventana.bind_all("<Button-5>", _on_mousewheel_principal_linux_down)

    tabla.bind("<Enter>", activar_scroll_tabla)
    tabla.bind("<Leave>", activar_scroll_principal)

    # activar scroll principal al inicio
    activar_scroll_principal()

    # ---------- FRAME BOTONES ----------
    frame_botones = ctk.CTkFrame(scroll)
    frame_botones.pack(pady=10)

    # ---------- FUNCIONES ----------
    def limpiar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)

    def eliminar():
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una suscripción")
            return

        item = tabla.item(seleccion[0])
        datos = item["values"]

        if not datos or not datos[0]:
            messagebox.showwarning("Aviso", "Esta fila no tiene ID de suscripción")
            return

        suscripcion_id = datos[0]

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Eliminar esta suscripción?"
        )

        if confirmar:
            eliminar_suscripcion(suscripcion_id)
            tabla.delete(seleccion[0])
            messagebox.showinfo("Eliminado", "Suscripción eliminada correctamente")

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
            estado_texto = str(estado).upper()

            if "VENCIDO" in estado_texto:
                tag = "vencido"
            elif "VENCE EN" in estado_texto:
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

    ctk.CTkButton(
        frame_botones,
        text="Eliminar suscripción",
        fg_color="#e74c3c",
        hover_color="#c0392b",
        command=eliminar
    ).grid(row=1, column=2, padx=10)

    # ---------- FORMULARIO ----------
    frame_asignar = ctk.CTkFrame(scroll)
    frame_asignar.pack(pady=15)

    ctk.CTkLabel(frame_asignar, text="ID Cliente").grid(row=0, column=0, padx=10, pady=5)
    entry_cliente = ctk.CTkEntry(frame_asignar)
    entry_cliente.grid(row=0, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame_asignar, text="ID Membresía").grid(row=1, column=0, padx=10, pady=5)
    entry_membresia = ctk.CTkEntry(frame_asignar)
    entry_membresia.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame_asignar, text="Precio").grid(row=2, column=0, padx=10, pady=5)
    entry_precio = ctk.CTkEntry(frame_asignar)
    entry_precio.grid(row=2, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame_asignar, text="Pagado").grid(row=3, column=0, padx=10, pady=5)
    entry_pagado = ctk.CTkEntry(frame_asignar)
    entry_pagado.grid(row=3, column=1, padx=10, pady=5)

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

        cargar_grafico_ingresos()

    ctk.CTkButton(
        frame_asignar,
        text="Asignar membresía",
        command=asignar
    ).grid(row=4, column=0, columnspan=2, pady=10)

    # ---------- CARGAR GRAFICO ----------
    cargar_grafico_ingresos()