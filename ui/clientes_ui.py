import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox

from modulos.clientes import agregar_cliente, ver_clientes, eliminar_cliente, editar_cliente


def abrir_ventana_clientes(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Gestión de Clientes")
    ventana.geometry("700x500")
    ventana.resizable(True, True)

    ventana.lift()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))
    ventana.focus_force()

    # -------- TITULO --------

    titulo = ctk.CTkLabel(
        ventana,
        text="Clientes del Gimnasio",
        font=("Arial", 20)
    )
    titulo.pack(pady=10)

    # -------- FORMULARIO --------

    frame_form = ctk.CTkFrame(ventana)
    frame_form.pack(pady=10, padx=20, fill="x")

    ctk.CTkLabel(frame_form, text="Nombre").grid(row=0, column=0, padx=10, pady=5)
    entry_nombre = ctk.CTkEntry(frame_form, width=200)
    entry_nombre.grid(row=0, column=1, padx=10)

    ctk.CTkLabel(frame_form, text="Teléfono").grid(row=1, column=0, padx=10, pady=5)
    entry_telefono = ctk.CTkEntry(frame_form, width=200)
    entry_telefono.grid(row=1, column=1, padx=10)

    ctk.CTkLabel(frame_form, text="Fecha Registro").grid(row=2, column=0, padx=10, pady=5)
    entry_fecha = ctk.CTkEntry(frame_form, width=200)
    entry_fecha.grid(row=2, column=1, padx=10)

    # -------- TABLA --------

    columnas = ("ID", "Nombre", "Telefono", "Fecha")

    tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=10)

    tabla.heading("ID", text="ID")
    tabla.heading("Nombre", text="Nombre")
    tabla.heading("Telefono", text="Teléfono")
    tabla.heading("Fecha", text="Fecha Registro")

    tabla.column("ID", width=50, anchor="center")
    tabla.column("Nombre", width=200)
    tabla.column("Telefono", width=150)
    tabla.column("Fecha", width=150)

    tabla.pack(pady=11, fill="both", expand=True)

    # -------- VARIABLE CLIENTE SELECCIONADO --------

    cliente_seleccionado = None

    # -------- FUNCION CARGAR CLIENTES --------

    def cargar_clientes():

        for fila in tabla.get_children():
            tabla.delete(fila)

        clientes = ver_clientes()

        for cliente in clientes:
            tabla.insert("", "end", values=cliente)

    # -------- FUNCION LIMPIAR CAMPOS --------

    def limpiar_campos():

        entry_nombre.delete(0, ctk.END)
        entry_telefono.delete(0, ctk.END)
        entry_fecha.delete(0, ctk.END)

    # -------- FUNCION AGREGAR CLIENTE --------

    def agregar():

        nombre = entry_nombre.get()
        telefono = entry_telefono.get()
        fecha = entry_fecha.get()

        if nombre == "" or telefono == "" or fecha == "":
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        agregar_cliente(nombre, telefono, fecha)

        messagebox.showinfo("Éxito", "Cliente agregado correctamente")

        limpiar_campos()
        cargar_clientes()

    # -------- SELECCIONAR CLIENTE --------

    def seleccionar_cliente(event):

        nonlocal cliente_seleccionado

        seleccion = tabla.selection()

        if not seleccion:
            return

        item = seleccion[0]
        valores = tabla.item(item, "values")

        cliente_seleccionado = int(valores[0])

        limpiar_campos()

        entry_nombre.insert(0, valores[1])
        entry_telefono.insert(0, valores[2])
        entry_fecha.insert(0, valores[3])

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

        nombre = entry_nombre.get()
        telefono = entry_telefono.get()
        fecha = entry_fecha.get()

        editar_cliente(cliente_seleccionado, nombre, telefono, fecha)

        messagebox.showinfo("Éxito", "Cliente actualizado")

        limpiar_campos()
        cargar_clientes()

        cliente_seleccionado = None

    # -------- FRAME BOTONES --------

    frame_botones = ctk.CTkFrame(ventana)
    frame_botones.pack(pady=10)

    boton_agregar = ctk.CTkButton(frame_botones, text="Agregar Cliente", width=150, command=agregar)
    boton_agregar.grid(row=0, column=0, padx=10)

    boton_limpiar = ctk.CTkButton(frame_botones, text="Limpiar", width=120, command=limpiar_campos)
    boton_limpiar.grid(row=0, column=1, padx=10)

    boton_actualizar = ctk.CTkButton(frame_botones, text="Actualizar Lista", width=150, command=cargar_clientes)
    boton_actualizar.grid(row=0, column=2, padx=10)

    boton_eliminar = ctk.CTkButton(frame_botones, text="Eliminar Cliente", width=150, fg_color="red", hover_color="#8B0000", command=eliminar)
    boton_eliminar.grid(row=0, column=3, padx=10)

    boton_editar = ctk.CTkButton(frame_botones, text="Editar Cliente", width=150, command=editar)
    boton_editar.grid(row=0, column=4, padx=10)

    # -------- CARGAR DATOS --------

    cargar_clientes()

    