import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import Counter

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from modulos.clientes import agregar_cliente, ver_clientes, eliminar_cliente, editar_cliente
from modulos.alertas import enviar_recordatorio_manual
from datetime import timedelta

def abrir_ventana_clientes(parent):

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
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

    # -------- SCROLL PRINCIPAL --------
    scroll = ctk.CTkScrollableFrame(ventana, fg_color="#2b2b2b")
    scroll.pack(fill="both", expand=True, padx=15, pady=15)

    # -------- HEADER SUPERIOR --------
    frame_header = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_header.pack(fill="x", padx=10, pady=(5, 15))

    titulo = ctk.CTkLabel(
        frame_header,
        text="Clientes del Gimnasio",
        font=("Segoe UI", 28, "bold"),
        text_color="white"
    )
    titulo.pack(side="left", padx=20, pady=20)

    subtitulo = ctk.CTkLabel(
        frame_header,
        text="Administra, busca, edita y elimina clientes registrados",
        font=("Segoe UI", 14),
        text_color="#d6d6d6"
    )
    subtitulo.pack(side="left", padx=(0, 10), pady=20)

    
    boton_regresar = ctk.CTkButton(
        frame_header,
        text="← Volver al menú",
        width=170,
        height=40,
        font=("Segoe UI", 14, "bold"),
        corner_radius=12,
        fg_color="#2A2A2A",
        hover_color="#3A3A3A",
        command=ventana.destroy
    )
    boton_regresar.pack(side="right", padx=20, pady=20)

    # -------- TARJETAS ESTADISTICAS --------
    frame_stats = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_stats.pack(fill="x", padx=10, pady=10)

    card_total = ctk.CTkFrame(frame_stats, corner_radius=15, fg_color="#1f6aa5")
    card_total.pack(side="left", padx=10, pady=10, expand=True, fill="both")

    ctk.CTkLabel(
        card_total,
        text="Total Clientes",
        font=("Segoe UI", 16, "bold"),
        text_color="white"
    ).pack(pady=(15, 5))

    numero_total = ctk.CTkLabel(
        card_total,
        text="0",
        font=("Segoe UI", 32, "bold"),
        text_color="white"
    )
    numero_total.pack(pady=(0, 15))

    card_activos = ctk.CTkFrame(frame_stats, corner_radius=15, fg_color="#198754")
    card_activos.pack(side="left", padx=10, pady=10, expand=True, fill="both")

    ctk.CTkLabel(
        card_activos,
        text="Clientes Activos",
        font=("Segoe UI", 16, "bold"),
        text_color="white"
    ).pack(pady=(15, 5))

    numero_activos = ctk.CTkLabel(
        card_activos,
        text="0",
        font=("Segoe UI", 32, "bold"),
        text_color="white"
    )
    numero_activos.pack(pady=(0, 15))

    card_hoy = ctk.CTkFrame(frame_stats, corner_radius=15, fg_color="#0d6efd")
    card_hoy.pack(side="left", padx=10, pady=10, expand=True, fill="both")

    ctk.CTkLabel(
        card_hoy,
        text="Nuevos Hoy",
        font=("Segoe UI", 16, "bold"),
        text_color="white"
    ).pack(pady=(15, 5))

    numero_hoy = ctk.CTkLabel(
        card_hoy,
        text="0",
        font=("Segoe UI", 32, "bold"),
        text_color="white"
    )
    numero_hoy.pack(pady=(0, 15))

    # -------- GRAFICO --------
    frame_grafico = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_grafico.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(
        frame_grafico,
        text="Clientes registrados por mes",
        font=("Segoe UI", 20, "bold"),
        text_color="white"
    ).pack(anchor="w", padx=20, pady=(15, 5))

    grafico_container = ctk.CTkFrame(frame_grafico, fg_color="#3f3f3f", corner_radius=15)
    grafico_container.pack(fill="x", padx=15, pady=(0, 15))

    fig = Figure(figsize=(10, 3.5), dpi=100)
    ax = fig.add_subplot(111)

    fig.patch.set_facecolor("#3f3f3f")
    ax.set_facecolor("#3f3f3f")

    canvas = FigureCanvasTkAgg(fig, master=grafico_container)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

    # -------- CONTENEDOR SUPERIOR --------
    frame_top = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_top.pack(fill="x", padx=10, pady=10)

    # -------- FORMULARIO --------
    frame_form = ctk.CTkFrame(frame_top, corner_radius=15, fg_color="#3f3f3f")
    frame_form.pack(fill="x", padx=15, pady=15)

    label_form = ctk.CTkLabel(
        frame_form,
        text="Formulario de Cliente",
        font=("Segoe UI", 20, "bold"),
        text_color="white"
    )
    label_form.grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 20))

    ctk.CTkLabel(frame_form, text="Nombre", font=("Segoe UI", 15, "bold"), text_color="white").grid(
        row=1, column=0, padx=20, pady=10, sticky="w"
    )
    entry_nombre = ctk.CTkEntry(
        frame_form, width=320, height=40, placeholder_text="Ingrese el nombre completo"
    )
    entry_nombre.grid(row=1, column=1, padx=15, pady=10, sticky="w")

    ctk.CTkLabel(frame_form, text="Cédula", font=("Segoe UI", 15, "bold"), text_color="white").grid(
        row=1, column=2, padx=20, pady=10, sticky="w"
    )
    entry_cedula = ctk.CTkEntry(
        frame_form, width=320, height=40, placeholder_text="Ingrese la cédula"
    )
    entry_cedula.grid(row=1, column=3, padx=15, pady=10, sticky="w")

    ctk.CTkLabel(frame_form, text="Teléfono", font=("Segoe UI", 15, "bold"), text_color="white").grid(
        row=2, column=0, padx=20, pady=10, sticky="w"
    )
    entry_telefono = ctk.CTkEntry(
        frame_form, width=320, height=40, placeholder_text="Ingrese el teléfono"
    )
    entry_telefono.grid(row=2, column=1, padx=15, pady=10, sticky="w")

    ctk.CTkLabel(frame_form, text="Fecha Registro", font=("Segoe UI", 15, "bold"), text_color="white").grid(
        row=2, column=2, padx=20, pady=10, sticky="w"
    )
    entry_fecha = ctk.CTkEntry(
        frame_form, width=320, height=40
    )
    entry_fecha.grid(row=2, column=3, padx=15, pady=10, sticky="w")

    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    entry_fecha.insert(0, fecha_actual)

    # -------- INFO Y BUSQUEDA --------
    frame_info = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_info.pack(fill="x", padx=10, pady=10)

    label_total = ctk.CTkLabel(
        frame_info,
        text="Total de clientes: 0",
        font=("Segoe UI", 17, "bold"),
        text_color="white"
    )
    label_total.pack(side="left", padx=20, pady=18)

    entry_buscar = ctk.CTkEntry(
        frame_info,
        width=340,
        height=40,
        font=("Segoe UI", 14),
        placeholder_text="Buscar por nombre, cédula o teléfono"
    )
    entry_buscar.pack(side="right", padx=20, pady=15)

    label_buscar = ctk.CTkLabel(
        frame_info,
        text="Buscar cliente:",
        font=("Segoe UI", 15, "bold"),
        text_color="white"
    )
    label_buscar.pack(side="right", padx=(10, 5), pady=15)

    # -------- ESTILO TABLA --------
    
    style = ttk.Style()

    style.configure(
        "Clientes.Treeview",
        background="#3a3a3a",
        foreground="white",
        fieldbackground="#3a3a3a",
        rowheight=34,
        font=("Segoe UI", 12)
    )

    style.configure(
        "Treeview.Heading",
        background="#2f2f2f",
        foreground="white",
        font=("Segoe UI", 13, "bold")
    )

    style.map(
        "Treeview",
        background=[("selected", "#1f6aa5")],
        foreground=[("selected", "white")]
    )

    # -------- TABLA --------
    frame_tabla = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

    label_tabla = ctk.CTkLabel(
        frame_tabla,
        text="Lista de Clientes",
        font=("Segoe UI", 20, "bold"),
        text_color="white"
    )
    label_tabla.pack(anchor="w", padx=20, pady=(15, 5))

    tabla_container = ctk.CTkFrame(frame_tabla, fg_color="transparent")
    tabla_container.pack(fill="both", expand=True, padx=15, pady=10)

    columnas = ("ID", "Nombre", "Cedula", "Telefono", "Fecha")

    tabla = ttk.Treeview(
        tabla_container,
        style="Clientes.Treeview",
        columns=columnas,
        show="headings",
        height=14,
        selectmode="browse"
    )

    tabla.heading("ID", text="ID")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Cedula", text="Cédula")
    tabla.heading("Telefono", text="Teléfono")
    tabla.heading("Fecha", text="Fecha Registro")

    tabla.column("ID", width=70, anchor="center")
    tabla.column("Nombre", width=320, anchor="center")
    tabla.column("Cedula", width=180, anchor="center")
    tabla.column("Telefono", width=180, anchor="center")
    tabla.column("Fecha", width=180, anchor="center")

    scrollbar_y = ttk.Scrollbar(tabla_container, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar_y.set)

    tabla.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    # -------- VARIABLE CLIENTE SELECCIONADO --------

    cliente_seleccionado = None

    # -------- FUNCIONES DE ESTADISTICAS Y GRAFICO --------
    def actualizar_grafico(clientes):
        ax.clear()
        ax.set_facecolor("#3f3f3f")
        fig.patch.set_facecolor("#3f3f3f")

        meses_orden = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                       "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

        contador = Counter()

        for cliente in clientes:
            try:
                fecha_txt = str(cliente[4]).strip()
                fecha_obj = datetime.strptime(fecha_txt, "%d/%m/%Y")
                mes = meses_orden[fecha_obj.month - 1]
                contador[mes] += 1
            except Exception:
                continue

        valores = [contador.get(mes, 0) for mes in meses_orden]

        ax.bar(meses_orden, valores, color="#1f6aa5")
        ax.set_title("Clientes registrados por mes", color="white", fontsize=14)
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_color("#3f3f3f")
        ax.spines["right"].set_color("#3f3f3f")
        ax.grid(axis="y", linestyle="--", alpha=0.3)

        canvas.draw()

    #------FUNCION ALERTA PARA CLIENTES-------
    def renovar_suscripcion():
        
        item = tabla.selection()

        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        
        valores = tabla.item(item[0], "values")
        
        cliente_id = int(valores[0])
        fecha = valores[4]
        
        try:
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")
        except:
            messagebox.showerror("Error", "Fecha inválida")
            return
        
        nueva_fecha = fecha_obj + timedelta(days=30)
        
        editar_cliente(
            cliente_id,
            valores[1],
            valores[2],
            valores[3],
            nueva_fecha.strftime("%d/%m/%Y")
        )

        messagebox.showinfo("Éxito", "Suscripción renovada +30 días")

        cargar_clientes()

    def actualizar_tarjetas(clientes):
        total = len(clientes)
        hoy = datetime.now().strftime("%d/%m/%Y")

        nuevos_hoy = 0
        for cliente in clientes:
            try:
                if str(cliente[4]).strip() == hoy:
                    nuevos_hoy += 1
            except Exception:
                pass

        numero_total.configure(text=str(total))
        numero_activos.configure(text=str(total))
        numero_hoy.configure(text=str(nuevos_hoy))
        label_total.configure(text=f"Total de clientes: {total}")

    #-------FUNCIÓN PARA ENVIAR MESJ DE WPP MANUAL-------
    def enviar_whatsapp_manual():
        
        item = tabla.selection()

        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        
        valores = tabla.item(item[0], "values")
        
        
        nombre = valores[1]
        telefono = valores[3]
        
        enviar_recordatorio_manual(nombre, telefono)

        messagebox.showinfo("WhatsApp", "Mensaje enviado")

    # -------- MOSTRAR EN TABLA --------
    def mostrar_en_tabla(clientes):
        for fila in tabla.get_children():
            tabla.delete(fila)

        for i, cliente in enumerate(clientes):
            tag = "par" if i % 2 == 0 else "impar"
            tabla.insert("", "end", values=cliente, tags=(tag,))

        tabla.tag_configure("par", background="#3a3a3a")
        tabla.tag_configure("impar", background="#444444")

        actualizar_tarjetas(clientes)
        actualizar_grafico(clientes)

    # -------- FUNCION CARGAR CLIENTES --------
    def cargar_clientes():
        clientes = ver_clientes()
        mostrar_en_tabla(clientes)

    # -------- FUNCION LIMPIAR CAMPOS --------
    def limpiar_campos():
        nonlocal cliente_seleccionado

        entry_nombre.delete(0, ctk.END)
        entry_cedula.delete(0, ctk.END)
        entry_telefono.delete(0, ctk.END)
        entry_fecha.delete(0, ctk.END)
        entry_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))

        seleccion = tabla.selection()
        if seleccion:
            tabla.selection_remove(seleccion)

        cliente_seleccionado = None

    # -------- FUNCION BUSCAR CLIENTES --------
    def buscar_clientes(event=None):
        texto = entry_buscar.get().strip().lower()
        clientes = ver_clientes()

        if texto == "":
            mostrar_en_tabla(clientes)
            return

        filtrados = []
        for cliente in clientes:
            nombre = str(cliente[1]).lower()
            cedula = str(cliente[2]).lower()
            telefono = str(cliente[3]).lower()

            if texto in nombre or texto in cedula or texto in telefono:
                filtrados.append(cliente)

        mostrar_en_tabla(filtrados)

    entry_buscar.bind("<KeyRelease>", buscar_clientes)

    # -------- FUNCION AGREGAR CLIENTE --------
    def agregar():
        nombre = entry_nombre.get().strip()
        cedula = entry_cedula.get().strip()
        telefono = entry_telefono.get().strip()
        fecha = entry_fecha.get().strip()

        if nombre == "" or cedula == "" or telefono == "" or fecha == "":
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        mensaje = agregar_cliente(nombre, cedula, telefono, fecha)

        if "correctamente" in mensaje:
            messagebox.showinfo("Éxito", mensaje)
            limpiar_campos()
            cargar_clientes()
        else:
            messagebox.showerror("Error", mensaje)

    # -------- SELECCIONAR CLIENTE --------
    def seleccionar_cliente(event):
        nonlocal cliente_seleccionado

        seleccion = tabla.selection()
        if not seleccion:
            return

        item = seleccion[0]
        valores = tabla.item(item, "values")

        cliente_seleccionado = int(valores[0])

        entry_nombre.delete(0, ctk.END)
        entry_cedula.delete(0, ctk.END)
        entry_telefono.delete(0, ctk.END)
        entry_fecha.delete(0, ctk.END)

        entry_nombre.insert(0, valores[1])
        entry_cedula.insert(0, valores[2])
        entry_telefono.insert(0, valores[3])
        entry_fecha.insert(0, valores[4])

    tabla.bind("<<TreeviewSelect>>", seleccionar_cliente)

    # -------- ELIMINAR CLIENTE --------
    def eliminar():
        item = tabla.selection()

        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return

        valores = tabla.item(item[0], "values")
        cliente_id = int(valores[0])

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que desea eliminar al cliente '{valores[1]}'?"
        )

        if not confirmar:
            return

        eliminar_cliente(cliente_id)

        messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
        limpiar_campos()
        cargar_clientes()

    # -------- EDITAR CLIENTE --------
    def editar():
        nonlocal cliente_seleccionado

        if cliente_seleccionado is None:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return

        nombre = entry_nombre.get().strip()
        cedula = entry_cedula.get().strip()
        telefono = entry_telefono.get().strip()
        fecha = entry_fecha.get().strip()

        if nombre == "" or cedula == "" or telefono == "" or fecha == "":
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Desea actualizar este cliente?"
        )

        if not confirmar:
            return

        mensaje = editar_cliente(cliente_seleccionado, nombre, cedula, telefono, fecha)

        if mensaje and "correctamente" not in mensaje:
            messagebox.showerror("Error", mensaje)
            return

        messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
        limpiar_campos()
        cargar_clientes()

    # -------- FRAME BOTONES --------
    frame_botones = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#343434")
    frame_botones.pack(fill="x", padx=10, pady=(10, 20))

     # -------- FRAME BOTONES CON SCROLL --------
    contenedor_botones = ctk.CTkFrame(scroll)
    contenedor_botones.pack(fill="x", padx=10, pady=(10, 20))
    
    canvas_botones = ctk.CTkCanvas(contenedor_botones, height=90, highlightthickness=0)
    canvas_botones.pack(side="top", fill="x", expand=True)

    scrollbar_botones = ctk.CTkScrollbar(
        contenedor_botones,
        orientation="horizontal",
        command=canvas_botones.xview
    )
    scrollbar_botones.pack(side="bottom", fill="x")

    canvas_botones.configure(xscrollcommand=scrollbar_botones.set)
    
    frame_botones = ctk.CTkFrame(canvas_botones, fg_color="#343434", corner_radius=18)
    
    canvas_botones.create_window((0, 0), window=frame_botones, anchor="nw")

    def ajustar_scroll(event):
        
        canvas_botones.configure(scrollregion=canvas_botones.bbox("all"))

    frame_botones.bind("<Configure>", ajustar_scroll)


    boton_agregar = ctk.CTkButton(
        frame_botones,
        text="Agregar Cliente",
        width=170,
        height=45,
        corner_radius=12,
        font=("Segoe UI", 14, "bold"),
        fg_color="#198754",
        hover_color="#157347",
        command=agregar
    )
    boton_agregar.grid(row=0, column=0, padx=15, pady=20)

    boton_limpiar = ctk.CTkButton(
        frame_botones,
        text="Limpiar",
        width=140,
        height=45,
        corner_radius=12,
        font=("Segoe UI", 14, "bold"),
        fg_color="gray35",
        hover_color="gray25",
        command=limpiar_campos
    )
    boton_limpiar.grid(row=0, column=1, padx=15, pady=20)

    boton_actualizar = ctk.CTkButton(
        frame_botones,
        text="Actualizar Lista",
        width=170,
        height=45,
        corner_radius=12,
        font=("Segoe UI", 14, "bold"),
        fg_color="#0d6efd",
        hover_color="#0b5ed7",
        command=cargar_clientes
    )
    boton_actualizar.grid(row=0, column=2, padx=15, pady=20)

    boton_editar = ctk.CTkButton(
        frame_botones,
        text="Editar Cliente",
        width=170,
        height=45,
        corner_radius=12,
        font=("Segoe UI", 14, "bold"),
        fg_color="#f0ad4e",
        hover_color="#d9962f",
        text_color="black",
        command=editar
    )
    boton_editar.grid(row=0, column=3, padx=15, pady=20)

    boton_eliminar = ctk.CTkButton(
        frame_botones,
        text="Eliminar Cliente",
        width=170,
        height=45,
        corner_radius=12,
        font=("Segoe UI", 14, "bold"),
        fg_color="#dc3545",
        hover_color="#bb2d3b",
        command=eliminar
    )
    boton_eliminar.grid(row=0, column=4, padx=15, pady=20)

    boton_renovar = ctk.CTkButton(
        frame_botones,
        text="Renovar +30 días",
        width=170,
        height=45,
        corner_radius=12,
        font=("Segoe UI", 14, "bold"),
        fg_color="#20c997",
        hover_color="#17a589",
        command=renovar_suscripcion
    )
    boton_renovar.grid(row=0, column=5, padx=15, pady=20)
    

    boton_enviar = ctk.CTkButton(
        frame_botones,
        text="Enviar alerta",
        width=170,
        height=45,
        corner_radius=12,
        font=("Segoe UI", 14, "bold"),
        fg_color="#20c997",
        hover_color="#17a589",
        command=enviar_whatsapp_manual
    )
    boton_enviar.grid(row=0, column=6, padx=15, pady=20)
  

    # -------- CARGAR DATOS --------
    cargar_clientes()