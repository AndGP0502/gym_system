import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from modulos.clientes import agregar_cliente, ver_clientes, eliminar_cliente, editar_cliente


def abrir_ventana_clientes(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Gestión de Clientes")

    ventana.geometry("950x650")
    ventana.resizable(True, True)

    # asegurar que la ventana esté creada
    ventana.update_idletasks()

    # traer al frente
    ventana.lift()
    ventana.focus_force()
    ventana.attributes("-topmost", True)

    # quitar topmost después para comportamiento normal
    ventana.after(200, lambda: ventana.attributes("-topmost", False))

    ventana.grab_set()

    # -------- SCROLL PRINCIPAL --------
    scroll = ctk.CTkScrollableFrame(ventana)
    scroll.pack(fill="both", expand=True)

    # -------- BOTON VOLVER --------
    boton_regresar = ctk.CTkButton(
        ventana,
        text="← Volver al menú",
        width=170,
        height=35,
        font=("Segoe UI", 14),
        command=ventana.destroy
    )
    boton_regresar.place(relx=0.97, y=30, anchor="ne")

    # -------- TITULO --------
    titulo = ctk.CTkLabel(
        scroll,
        text="Clientes del Gimnasio",
        font=("Arial", 24, "bold")
    )
    titulo.pack(pady=15)

    # -------- FORMULARIO --------
    frame_form = ctk.CTkFrame(scroll)
    frame_form.pack(pady=10, padx=20, fill="x")

    ctk.CTkLabel(frame_form, text="Nombre", font=("Segoe UI", 15)).grid(row=0, column=0, padx=10, pady=8)
    entry_nombre = ctk.CTkEntry(frame_form, width=250, height=35)
    entry_nombre.grid(row=0, column=1, padx=10, pady=8)

    ctk.CTkLabel(frame_form, text="Cédula", font=("Segoe UI", 15)).grid(row=1, column=0, padx=10, pady=8)
    entry_cedula = ctk.CTkEntry(frame_form, width=250, height=35)
    entry_cedula.grid(row=1, column=1, padx=10, pady=8)

    ctk.CTkLabel(frame_form, text="Teléfono", font=("Segoe UI", 15)).grid(row=2, column=0, padx=10, pady=8)
    entry_telefono = ctk.CTkEntry(frame_form, width=250, height=35)
    entry_telefono.grid(row=2, column=1, padx=10, pady=8)

    ctk.CTkLabel(frame_form, text="Fecha Registro", font=("Segoe UI", 15)).grid(row=3, column=0, padx=10, pady=8)
    entry_fecha = ctk.CTkEntry(frame_form, width=250, height=35)
    entry_fecha.grid(row=3, column=1, padx=10, pady=8)

    # colocar fecha actual automática
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    entry_fecha.insert(0, fecha_actual)

    # -------- CONTADOR --------
    label_total = ctk.CTkLabel(
        scroll,
        text="Total de clientes: 0",
        font=("Segoe UI", 15, "bold")
    )
    label_total.pack(pady=(10, 5))

    # -------- BUSCADOR --------
    frame_busqueda = ctk.CTkFrame(scroll)
    frame_busqueda.pack(pady=10)

    ctk.CTkLabel(
        frame_busqueda,
        text="Buscar cliente:",
        font=("Segoe UI", 15)
    ).grid(row=0, column=0, padx=10, pady=10)

    entry_buscar = ctk.CTkEntry(
        frame_busqueda,
        width=280,
        height=35,
        font=("Segoe UI", 15),
        placeholder_text="Buscar por nombre, cédula o teléfono"
    )
    entry_buscar.grid(row=0, column=1, padx=10, pady=10)

    # -------- ESTILO TABLA --------
    style = ttk.Style()
    style.configure("Treeview", font=("Segoe UI", 13), rowheight=30)
    style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"))

    # -------- TABLA --------
    frame_tabla = ctk.CTkFrame(scroll)
    frame_tabla.pack(pady=10, padx=20, fill="both", expand=True)

    columnas = ("ID", "Nombre", "Cedula", "Telefono", "Fecha")

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)

    tabla.heading("ID", text="ID")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Cedula", text="Cédula")
    tabla.heading("Telefono", text="Teléfono")
    tabla.heading("Fecha", text="Fecha Registro")

    tabla.column("ID", width=70, anchor="center")
    tabla.column("Nombre", width=220, anchor="center")
    tabla.column("Cedula", width=160, anchor="center")
    tabla.column("Telefono", width=160, anchor="center")
    tabla.column("Fecha", width=160, anchor="center")

    tabla.pack(pady=10, fill="both", expand=True)

    # -------- VARIABLE CLIENTE SELECCIONADO --------
    cliente_seleccionado = None

    # -------- MOSTRAR EN TABLA --------
    def mostrar_en_tabla(clientes):
        for fila in tabla.get_children():
            tabla.delete(fila)

        for cliente in clientes:
            tabla.insert("", "end", values=cliente)

        label_total.configure(text=f"Total de clientes: {len(clientes)}")

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
            "¿Seguro que desea eliminar este cliente?"
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
    frame_botones = ctk.CTkFrame(scroll)
    frame_botones.pack(pady=15)

    boton_agregar = ctk.CTkButton(
        frame_botones,
        text="Agregar Cliente",
        width=150,
        height=40,
        command=agregar
    )
    boton_agregar.grid(row=0, column=0, padx=10, pady=10)

    boton_limpiar = ctk.CTkButton(
        frame_botones,
        text="Limpiar",
        width=120,
        height=40,
        fg_color="gray40",
        hover_color="gray30",
        command=limpiar_campos
    )
    boton_limpiar.grid(row=0, column=1, padx=10, pady=10)

    boton_actualizar = ctk.CTkButton(
        frame_botones,
        text="Actualizar Lista",
        width=150,
        height=40,
        command=cargar_clientes
    )
    boton_actualizar.grid(row=0, column=2, padx=10, pady=10)

    boton_eliminar = ctk.CTkButton(
        frame_botones,
        text="Eliminar Cliente",
        width=150,
        height=40,
        fg_color="red",
        hover_color="#8B0000",
        command=eliminar
    )
    boton_eliminar.grid(row=0, column=3, padx=10, pady=10)

    boton_editar = ctk.CTkButton(
        frame_botones,
        text="Editar Cliente",
        width=150,
        height=40,
        fg_color="#f0ad4e",
        hover_color="#d9962f",
        command=editar
    )
    boton_editar.grid(row=0, column=4, padx=10, pady=10)

    # -------- CARGAR DATOS --------
    cargar_clientes()
    