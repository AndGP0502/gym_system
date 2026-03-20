import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime, timedelta
from collections import Counter

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from modulos.clientes import agregar_cliente, ver_clientes, eliminar_cliente, editar_cliente
from modulos.alertas import enviar_recordatorio_manual
from modulos.suscripciones import renovar_suscripcion_cliente
from ui.ficha_ui import abrir_ficha_cliente
from modulos.pdf_generador import generar_pdf_ficha_cliente

def abrir_ventana_clientes(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Gestión de Clientes")
    ventana.state("zoomed")
    ventana.resizable(True, True)
    ventana.configure(fg_color="#2b2b2b")

    ventana.update_idletasks()
    ventana.lift()
    ventana.focus_force()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))
    ventana.grab_set()

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

    def _scroll_principal(event):
        if canvas_principal.winfo_exists():
            canvas_principal.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas_principal.bind("<MouseWheel>", _scroll_principal)
    scroll.bind("<MouseWheel>", _scroll_principal)

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

    # HEADER
    frame_header = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_header.pack(fill="x", padx=10, pady=(5, 15))
    ctk.CTkLabel(frame_header, text="Clientes del Gimnasio",
                 font=("Segoe UI", 28, "bold"), text_color="white").pack(side="left", padx=20, pady=20)
    ctk.CTkLabel(frame_header, text="Administra, busca, edita y elimina clientes registrados",
                 font=("Segoe UI", 14), text_color="#d6d6d6").pack(side="left", padx=(0, 10), pady=20)
    ctk.CTkButton(frame_header, text="← Volver al menú", width=170, height=40,
                  font=("Segoe UI", 14, "bold"), corner_radius=12,
                  fg_color="#2A2A2A", hover_color="#3A3A3A",
                  command=ventana.destroy).pack(side="right", padx=20, pady=20)

    # TARJETAS
    frame_stats = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_stats.pack(fill="x", padx=10, pady=10)
    card_total = ctk.CTkFrame(frame_stats, corner_radius=15, fg_color="#1f6aa5")
    card_total.pack(side="left", padx=10, pady=10, expand=True, fill="both")
    ctk.CTkLabel(card_total, text="Total Clientes", font=("Segoe UI", 16, "bold"), text_color="white").pack(pady=(15, 5))
    numero_total = ctk.CTkLabel(card_total, text="0", font=("Segoe UI", 32, "bold"), text_color="white")
    numero_total.pack(pady=(0, 15))
    card_activos = ctk.CTkFrame(frame_stats, corner_radius=15, fg_color="#198754")
    card_activos.pack(side="left", padx=10, pady=10, expand=True, fill="both")
    ctk.CTkLabel(card_activos, text="Clientes Activos", font=("Segoe UI", 16, "bold"), text_color="white").pack(pady=(15, 5))
    numero_activos = ctk.CTkLabel(card_activos, text="0", font=("Segoe UI", 32, "bold"), text_color="white")
    numero_activos.pack(pady=(0, 15))
    card_hoy = ctk.CTkFrame(frame_stats, corner_radius=15, fg_color="#0d6efd")
    card_hoy.pack(side="left", padx=10, pady=10, expand=True, fill="both")
    ctk.CTkLabel(card_hoy, text="Nuevos Hoy", font=("Segoe UI", 16, "bold"), text_color="white").pack(pady=(15, 5))
    numero_hoy = ctk.CTkLabel(card_hoy, text="0", font=("Segoe UI", 32, "bold"), text_color="white")
    numero_hoy.pack(pady=(0, 15))

    # GRÁFICO
    frame_grafico = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_grafico.pack(fill="x", padx=10, pady=10)
    ctk.CTkLabel(frame_grafico, text="Clientes registrados por mes",
                 font=("Segoe UI", 20, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(15, 5))
    grafico_container = ctk.CTkFrame(frame_grafico, fg_color="#3f3f3f", corner_radius=15)
    grafico_container.pack(fill="x", padx=15, pady=(0, 15))
    fig = Figure(figsize=(10, 3.5), dpi=100)
    ax  = fig.add_subplot(111)
    fig.patch.set_facecolor("#3f3f3f")
    ax.set_facecolor("#3f3f3f")
    canvas_fig = FigureCanvasTkAgg(fig, master=grafico_container)
    canvas_fig.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # FORMULARIO
    frame_top  = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_top.pack(fill="x", padx=10, pady=10)
    frame_form = ctk.CTkFrame(frame_top, corner_radius=15, fg_color="#3f3f3f")
    frame_form.pack(fill="x", padx=15, pady=15)
    ctk.CTkLabel(frame_form, text="Formulario de Cliente",
                 font=("Segoe UI", 20, "bold"), text_color="white").grid(
        row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 20))
    ctk.CTkLabel(frame_form, text="Nombre", font=("Segoe UI", 15, "bold"), text_color="white").grid(row=1, column=0, padx=20, pady=10, sticky="w")
    entry_nombre = ctk.CTkEntry(frame_form, width=320, height=40, placeholder_text="Nombre completo")
    entry_nombre.grid(row=1, column=1, padx=15, pady=10, sticky="w")
    ctk.CTkLabel(frame_form, text="Cédula", font=("Segoe UI", 15, "bold"), text_color="white").grid(row=1, column=2, padx=20, pady=10, sticky="w")
    entry_cedula = ctk.CTkEntry(frame_form, width=320, height=40, placeholder_text="Cédula")
    entry_cedula.grid(row=1, column=3, padx=15, pady=10, sticky="w")
    ctk.CTkLabel(frame_form, text="Teléfono", font=("Segoe UI", 15, "bold"), text_color="white").grid(row=2, column=0, padx=20, pady=10, sticky="w")
    entry_telefono = ctk.CTkEntry(frame_form, width=320, height=40, placeholder_text="Teléfono")
    entry_telefono.grid(row=2, column=1, padx=15, pady=10, sticky="w")
    ctk.CTkLabel(frame_form, text="Fecha Registro", font=("Segoe UI", 15, "bold"), text_color="white").grid(row=2, column=2, padx=20, pady=10, sticky="w")
    entry_fecha = ctk.CTkEntry(frame_form, width=320, height=40)
    entry_fecha.grid(row=2, column=3, padx=15, pady=10, sticky="w")
    entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))

    # BÚSQUEDA
    frame_info = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_info.pack(fill="x", padx=10, pady=10)
    label_total = ctk.CTkLabel(frame_info, text="Total de clientes: 0",
                               font=("Segoe UI", 17, "bold"), text_color="white")
    label_total.pack(side="left", padx=20, pady=18)
    entry_buscar = ctk.CTkEntry(frame_info, width=340, height=40, font=("Segoe UI", 14),
                                placeholder_text="Buscar por nombre, cédula o teléfono")
    entry_buscar.pack(side="right", padx=20, pady=15)
    ctk.CTkLabel(frame_info, text="Buscar cliente:", font=("Segoe UI", 15, "bold"),
                 text_color="white").pack(side="right", padx=(10, 5), pady=15)

    # TABLA
    style = ttk.Style()
    style.configure("Clientes.Treeview",
                    background="#3a3a3a", foreground="white",
                    fieldbackground="#3a3a3a", rowheight=34,
                    font=("Segoe UI", 12))
    style.configure("Clientes.Treeview.Heading",
                    background="#2f2f2f", foreground="white",
                    font=("Segoe UI", 13, "bold"))
    style.map("Clientes.Treeview",
              background=[("selected", "#1f6aa5")],
              foreground=[("selected", "white")])

    frame_tabla = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)
    ctk.CTkLabel(frame_tabla, text="Lista de Clientes",
                 font=("Segoe UI", 20, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(15, 5))
    tabla_container = ctk.CTkFrame(frame_tabla, fg_color="transparent")
    tabla_container.pack(fill="both", expand=True, padx=15, pady=10)

    columnas = ("ID", "Nombre", "Cedula", "Telefono", "Fecha")
    tabla = ttk.Treeview(tabla_container, style="Clientes.Treeview",
                         columns=columnas, show="headings", height=14, selectmode="browse")
    tabla.heading("ID",       text="ID")
    tabla.heading("Nombre",   text="Nombre")
    tabla.heading("Cedula",   text="Cédula")
    tabla.heading("Telefono", text="Teléfono")
    tabla.heading("Fecha",    text="Fecha Registro")
    tabla.column("ID",       width=70,  anchor="center", minwidth=50)
    tabla.column("Nombre",   width=320, anchor="w",      minwidth=120)
    tabla.column("Cedula",   width=180, anchor="center", minwidth=80)
    tabla.column("Telefono", width=180, anchor="center", minwidth=80)
    tabla.column("Fecha",    width=180, anchor="center", minwidth=80)
    scrollbar_y = ttk.Scrollbar(tabla_container, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar_y.set)
    tabla.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")
    _scroll_local_treeview(tabla)

    cliente_seleccionado = None

    # FUNCIONES
    def actualizar_grafico(clientes):
        ax.clear()
        ax.set_facecolor("#3f3f3f")
        fig.patch.set_facecolor("#3f3f3f")
        meses_orden = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        contador = Counter()
        for c in clientes:
            try:
                fecha_obj = datetime.strptime(str(c[4]).strip(), "%d/%m/%Y")
                contador[meses_orden[fecha_obj.month - 1]] += 1
            except Exception:
                continue
        ax.bar(meses_orden, [contador.get(m, 0) for m in meses_orden], color="#1f6aa5")
        ax.set_title("Clientes registrados por mes", color="white", fontsize=14)
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_color("#3f3f3f")
        ax.spines["right"].set_color("#3f3f3f")
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        canvas_fig.draw()

    def actualizar_tarjetas(clientes):
        total   = len(clientes)
        hoy_str = datetime.now().strftime("%d/%m/%Y")
        nuevos  = sum(1 for c in clientes if str(c[4]).strip() == hoy_str)
        numero_total.configure(text=str(total))
        numero_activos.configure(text=str(total))
        numero_hoy.configure(text=str(nuevos))
        label_total.configure(text=f"Total de clientes: {total}")

    def mostrar_en_tabla(clientes):
        for fila in tabla.get_children():
            tabla.delete(fila)
        for i, c in enumerate(clientes):
            tag = "par" if i % 2 == 0 else "impar"
            tabla.insert("", "end", values=c, tags=(tag,))
        tabla.tag_configure("par",   background="#3a3a3a")
        tabla.tag_configure("impar", background="#444444")
        actualizar_tarjetas(clientes)
        actualizar_grafico(clientes)

    def cargar_clientes():
        mostrar_en_tabla(ver_clientes())

    def limpiar_campos():
        nonlocal cliente_seleccionado
        entry_nombre.delete(0, ctk.END)
        entry_cedula.delete(0, ctk.END)
        entry_telefono.delete(0, ctk.END)
        entry_fecha.delete(0, ctk.END)
        entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        sel = tabla.selection()
        if sel:
            tabla.selection_remove(sel)
        cliente_seleccionado = None

    def buscar_clientes(event=None):
        texto    = entry_buscar.get().strip().lower()
        clientes = ver_clientes()
        if texto == "":
            mostrar_en_tabla(clientes)
            return
        filtrados = [c for c in clientes if
                     texto in str(c[1]).lower() or
                     texto in str(c[2]).lower() or
                     texto in str(c[3]).lower()]
        mostrar_en_tabla(filtrados)

    entry_buscar.bind("<KeyRelease>", buscar_clientes)

    def agregar():
        nombre   = entry_nombre.get().strip()
        cedula   = entry_cedula.get().strip()
        telefono = entry_telefono.get().strip()
        fecha    = entry_fecha.get().strip()
        if not all([nombre, cedula, telefono, fecha]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        aceptar_datos = messagebox.askyesno(
            "Consentimiento de uso de datos",
            "Al continuar con el registro, el cliente autoriza el uso de sus datos personales "
            "únicamente para fines administrativos, de contacto, gestión de membresías, pagos, "
            "control interno y servicios relacionados con el gimnasio.\n\n"
            "La información será tratada de manera confidencial y no será compartida con terceros "
            "ajenos a la gestión del servicio.\n\n"
            "¿Desea aceptar y continuar con el registro?"
        )
        if not aceptar_datos:
            messagebox.showinfo("Registro cancelado", "No se realizó el registro del cliente.")
            return
        mensaje = agregar_cliente(nombre, cedula, telefono, fecha)
        if "correctamente" in mensaje:
            messagebox.showinfo("Éxito", mensaje)
            limpiar_campos()
            cargar_clientes()
        else:
            messagebox.showerror("Error", mensaje)

    def seleccionar_cliente(event):
        nonlocal cliente_seleccionado
        sel = tabla.selection()
        if not sel:
            return
        valores = tabla.item(sel[0], "values")
        cliente_seleccionado = int(valores[0])
        entry_nombre.delete(0, ctk.END);   entry_nombre.insert(0, valores[1])
        entry_cedula.delete(0, ctk.END);   entry_cedula.insert(0, valores[2])
        entry_telefono.delete(0, ctk.END); entry_telefono.insert(0, valores[3])
        entry_fecha.delete(0, ctk.END);    entry_fecha.insert(0, valores[4])

    tabla.bind("<<TreeviewSelect>>", seleccionar_cliente)

    def eliminar():
        item = tabla.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        valores    = tabla.item(item[0], "values")
        cliente_id = int(valores[0])
        if messagebox.askyesno("Confirmar", f"¿Eliminar al cliente '{valores[1]}'?"):
            eliminar_cliente(cliente_id)
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
            limpiar_campos()
            cargar_clientes()

    def editar():
        nonlocal cliente_seleccionado
        if cliente_seleccionado is None:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        nombre   = entry_nombre.get().strip()
        cedula   = entry_cedula.get().strip()
        telefono = entry_telefono.get().strip()
        fecha    = entry_fecha.get().strip()
        if not all([nombre, cedula, telefono, fecha]):
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return
        if not messagebox.askyesno("Confirmar", "¿Actualizar este cliente?"):
            return
        mensaje = editar_cliente(cliente_seleccionado, nombre, cedula, telefono, fecha)
        if mensaje and "correctamente" not in mensaje:
            messagebox.showerror("Error", mensaje)
            return
        messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
        limpiar_campos()
        cargar_clientes()

    def renovar_suscripcion():
        import sqlite3 as _sq
        from database.db_path import DB_PATH as _DB

        item = tabla.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return

        valores    = tabla.item(item[0], "values")
        cliente_id = int(valores[0])
        fecha_str  = valores[4]

        # Pedir monto
        monto_str = ctk.CTkInputDialog(
            text=f"Monto pagado por {valores[1]} en la renovacion:\n(escribe 0 si aun no paga)",
            title="Monto de renovacion"
        ).get_input()

        if monto_str is None:
            return  # Canceló el diálogo

        try:
            monto = float(monto_str)
        except ValueError:
            messagebox.showerror("Error", "Monto invalido")
            return

        # Actualizar fecha de registro del cliente +30 días
        try:
            fecha_obj   = datetime.strptime(fecha_str, "%d/%m/%Y")
            nueva_fecha = (fecha_obj + timedelta(days=30)).strftime("%d/%m/%Y")
        except Exception:
            nueva_fecha = fecha_str  # Si falla el parse, mantener fecha actual

        editar_cliente(cliente_id, valores[1], valores[2], valores[3], nueva_fecha)

        # Renovar suscripción: extiende fecha_vencimiento y registra pago
        resultado = renovar_suscripcion_cliente(cliente_id, dias=30, monto=monto)

        if resultado == "sin_suscripcion":
            messagebox.showinfo("Aviso",
                "No se encontro suscripcion activa.\nSolo se actualizo la fecha de registro.")
            cargar_clientes()
            return
        elif resultado == "fecha_invalida":
            messagebox.showwarning("Advertencia",
                "La fecha de vencimiento en la BD tiene un formato invalido.")
            cargar_clientes()
            return
        elif resultado != "ok":
            messagebox.showwarning("Advertencia",
                "No se pudo actualizar la suscripcion correctamente.")
            cargar_clientes()
            return

        msg_pago = f"Pago de ${monto:.2f} registrado." if monto > 0 else "Sin pago registrado ($0)."
        messagebox.showinfo("Renovado",
            f"Suscripcion de '{valores[1]}' renovada +30 dias.\n{msg_pago}")
        cargar_clientes()

    def enviar_whatsapp_manual():
        item = tabla.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        valores    = tabla.item(item[0], "values")
        id_cliente = int(valores[0])
        enviar_recordatorio_manual(valores[1], valores[3], id_cliente)
        messagebox.showinfo("WhatsApp", f"Abriendo WhatsApp para {valores[1]}...")

    def ver_ficha():
        nonlocal cliente_seleccionado
        if cliente_seleccionado is None:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la tabla primero.")
            return
        sel    = tabla.selection()
        nombre = tabla.item(sel[0], "values")[1]
        abrir_ficha_cliente(ventana, cliente_seleccionado, nombre)

    # BOTONES
    contenedor_botones = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    contenedor_botones.pack(fill="x", padx=10, pady=(10, 20))
    frame_botones = ctk.CTkFrame(contenedor_botones, fg_color="transparent")
    frame_botones.pack(fill="x", padx=20, pady=20)
    frame_botones.grid_columnconfigure(0, weight=1)
    frame_botones.grid_columnconfigure(1, weight=1)
    frame_botones.grid_columnconfigure(2, weight=1)

    # GESTIÓN
    ctk.CTkLabel(frame_botones, text="Gestión",
                 font=("Segoe UI", 18, "bold"), text_color="white").grid(row=0, column=0, pady=(0, 12))
    ctk.CTkButton(frame_botones, text="Agregar Cliente", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="#198754", hover_color="#157347",
                  text_color="white", command=agregar).grid(row=1, column=0, padx=12, pady=6, sticky="ew")
    ctk.CTkButton(frame_botones, text="Editar Cliente", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="#f0ad4e", hover_color="#d9962f",
                  text_color="black", command=editar).grid(row=2, column=0, padx=12, pady=6, sticky="ew")
    ctk.CTkButton(frame_botones, text="📄 Ver ficha", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="#1f6aa5", hover_color="#174f7a",
                  text_color="white", command=ver_ficha).grid(row=3, column=0, padx=12, pady=6, sticky="ew")
    ctk.CTkButton(frame_botones, text="📥 Descargar PDF", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="#6c757d", hover_color="#5a6268",
                  text_color="white",
                  command=lambda: generar_pdf_ficha_cliente(
                      ventana, cliente_seleccionado,
                      tabla.item(tabla.selection()[0], "values")[1] if tabla.selection() else ""
                  )).grid(row=4, column=0, padx=12, pady=6, sticky="ew")

    # UTILIDADES
    ctk.CTkLabel(frame_botones, text="Utilidades",
                 font=("Segoe UI", 18, "bold"), text_color="white").grid(row=0, column=1, pady=(0, 12))
    ctk.CTkButton(frame_botones, text="Limpiar", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="gray35", hover_color="gray25",
                  text_color="white", command=limpiar_campos).grid(row=1, column=1, padx=12, pady=6, sticky="ew")
    ctk.CTkButton(frame_botones, text="Actualizar Lista", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="#0d6efd", hover_color="#0b5ed7",
                  text_color="white", command=cargar_clientes).grid(row=2, column=1, padx=12, pady=6, sticky="ew")
    ctk.CTkLabel(frame_botones, text="", fg_color="transparent").grid(row=3, column=1, padx=12, pady=6, sticky="ew")

    # ACCIONES ESPECIALES
    ctk.CTkLabel(frame_botones, text="Acciones especiales",
                 font=("Segoe UI", 18, "bold"), text_color="white").grid(row=0, column=2, pady=(0, 12))
    ctk.CTkButton(frame_botones, text="Renovar +30 días", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="#20c997", hover_color="#17a589",
                  text_color="white", command=renovar_suscripcion).grid(row=1, column=2, padx=12, pady=6, sticky="ew")
    ctk.CTkButton(frame_botones, text="Enviar alerta WPP", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="#6f42c1", hover_color="#5a32a3",
                  text_color="white", command=enviar_whatsapp_manual).grid(row=2, column=2, padx=12, pady=6, sticky="ew")
    ctk.CTkButton(frame_botones, text="Eliminar Cliente", height=45, corner_radius=12,
                  font=("Segoe UI", 14, "bold"), fg_color="#dc3545", hover_color="#bb2d3b",
                  text_color="white", command=eliminar).grid(row=3, column=2, padx=12, pady=6, sticky="ew")

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
    cargar_clientes()