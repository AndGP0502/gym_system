import customtkinter as ctk
from tkinter import ttk, messagebox

from modulos.pagos import registrar_pago, ver_historial_pagos, listar_suscripciones_para_pago, buscar_cliente_pagos, eliminar_pago
from modulos.clientes import ver_clientes
from modulos.suscripciones import ver_suscripciones_completas, crear_suscripcion


def abrir_ventana_pagos(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Gestión de Pagos")
    ventana.state("zoomed")

    ventana.lift()
    ventana.after(10, lambda: ventana.focus())
    # -------- SCROLL PRINCIPAL --------

    scroll = ctk.CTkScrollableFrame(ventana)
    scroll.pack(fill="both", expand=True)

    # -------- TABLA CLIENTES --------

    frame_clientes = ctk.CTkFrame(scroll)
    frame_clientes.pack(pady=10, fill="x")

    ctk.CTkLabel(frame_clientes, text="Clientes registrados").pack(pady=5)

    tabla_clientes = ttk.Treeview(
        frame_clientes,
        columns=("ID", "Nombre"),
        show="headings",
        height=4
    )

    tabla_clientes.heading("ID", text="ID")
    tabla_clientes.heading("Nombre", text="Nombre")

    tabla_clientes.column("ID", width=80, anchor="center")
    tabla_clientes.column("Nombre", width=250, anchor="w")

    tabla_clientes.pack(fill="x", padx=10, pady=5)

    # -------- TABLA SUSCRIPCIONES --------

    frame_sus = ctk.CTkFrame(scroll)
    frame_sus.pack(pady=10, fill="x")

    ctk.CTkLabel(frame_sus, text="Suscripciones registradas").pack(pady=5)

    tabla_sus = ttk.Treeview(
        frame_sus,
        columns=("ID", "Cliente", "Plan"),
        show="headings",
        height=4
    )

    tabla_sus.heading("ID", text="ID Suscripción")
    tabla_sus.heading("Cliente", text="Cliente")
    tabla_sus.heading("Plan", text="Plan")

    tabla_sus.column("ID", width=100, anchor="center")
    tabla_sus.column("Cliente", width=200)
    tabla_sus.column("Plan", width=150)

    tabla_sus.pack(fill="x", padx=10)

    # -------- TABLA ESTADO PAGOS --------

    frame_tabla = ctk.CTkFrame(scroll)
    frame_tabla.pack(pady=10, fill="both", expand=True)

    columnas = (
        "ID",
        "Cliente",
        "Plan",
        "Total",
        "Pagado",
        "Pendiente",
        "Inicio",
        "Vence"
    )

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=6)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=110, anchor="center")

    tabla.pack(side="left", fill="both", expand=True)

    scroll_tabla = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    scroll_tabla.pack(side="right", fill="y")

    tabla.configure(yscrollcommand=scroll_tabla.set)

    # -------- COLORES --------

    tabla.tag_configure("pagado", background="#baf7b0")
    tabla.tag_configure("parcial", background="#fff3a6")
    tabla.tag_configure("deuda", background="#f5b7b1")

    # -------- BUSCAR / CREAR SUSCRIPCION --------

    frame_buscar = ctk.CTkFrame(scroll)
    frame_buscar.pack(pady=10)

    ctk.CTkLabel(frame_buscar, text="Buscar por ID Cliente").grid(row=0, column=0, padx=10)

    entry_cliente = ctk.CTkEntry(frame_buscar, width=120)
    entry_cliente.grid(row=0, column=1, padx=10)

    ctk.CTkLabel(frame_buscar, text="ID Cliente").grid(row=1, column=0, padx=10)

    entry_id_cliente = ctk.CTkEntry(frame_buscar, width=120)
    entry_id_cliente.grid(row=1, column=1)

    ctk.CTkLabel(frame_buscar, text="ID Membresía").grid(row=2, column=0, padx=10)

    entry_id_membresia = ctk.CTkEntry(frame_buscar, width=120)
    entry_id_membresia.grid(row=2, column=1)



    # -------- FORMULARIO PAGOS --------

    frame = ctk.CTkFrame(scroll)
    frame.pack(pady=10)

    ctk.CTkLabel(frame, text="ID Suscripción").grid(row=0, column=0, padx=10)

    entry_id = ctk.CTkEntry(frame, width=120)
    entry_id.grid(row=0, column=1, padx=10)

    ctk.CTkLabel(frame, text="Monto pagado").grid(row=1, column=0, padx=10)

    entry_monto = ctk.CTkEntry(frame, width=120)
    entry_monto.grid(row=1, column=1, padx=10)

    # -------- FUNCIONES --------

    def cargar_clientes():
        for fila in tabla_clientes.get_children():
            tabla_clientes.delete(fila)

        clientes = ver_clientes()

        for cliente in clientes:
            id_cliente, nombre, telefono, fecha = cliente
            tabla_clientes.insert("", "end", values=(id_cliente, nombre))

    def cargar_suscripciones():
        for fila in tabla.get_children():
            tabla.delete(fila)

        datos = listar_suscripciones_para_pago()

        for sus in datos:

            cliente = sus[1]
            id_suscripcion = sus[2]
            plan = sus[3]
            total = float(sus[4])
            pagado = float(sus[5])
            pendiente = float(sus[6])
            inicio = sus[7]
            vence = sus[8]

            fila = (
                id_suscripcion,
                cliente,
                plan,
                total,
                pagado,
                pendiente,
                inicio,
                vence
            )

            if pendiente == 0 or pagado >= total:
                tag = "pagado"
            elif pagado > 0:
                tag = "parcial"
            else:
                tag = "deuda"

            tabla.insert("", "end", values=fila, tags=(tag,))

    def buscar_cliente():

        cliente_id = entry_cliente.get()

        if cliente_id == "":
            messagebox.showerror("Error", "Ingrese un ID de cliente", parent=ventana)
            return

        try:
            cliente_id = int(cliente_id)
        except ValueError:
            messagebox.showerror("Error", "ID inválido", parent=ventana)
            return

        datos = buscar_cliente_pagos(cliente_id)

        for fila in tabla.get_children():
            tabla.delete(fila)

        for fila in datos:
            tabla.insert("", "end", values=fila)

    def seleccionar_fila(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        valores = tabla.item(seleccion[0], "values")

        entry_id.delete(0, ctk.END)
        entry_id.insert(0, valores[0])

    def seleccionar_cliente(event):

        item = tabla_clientes.selection()

        if not item:
            return

        valores = tabla_clientes.item(item[0], "values")

        entry_cliente.delete(0, ctk.END)
        entry_cliente.insert(0, valores[0])

    def seleccionar_suscripcion(event):

        item = tabla_sus.selection()

        if not item:
            return

        valores = tabla_sus.item(item[0], "values")

        entry_id.delete(0, ctk.END)
        entry_id.insert(0, valores[0])

    def pagar():

        suscripcion = entry_id.get()
        monto = entry_monto.get()

        if suscripcion == "" or monto == "":
            messagebox.showerror("Error", "Debes seleccionar una suscripción y escribir el monto", parent=ventana)
            return

        try:
            suscripcion = int(suscripcion)
            monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos", parent=ventana)
            return

        if monto <= 0:
            messagebox.showerror("Error", "El monto debe ser mayor a 0", parent=ventana)
            return

        registrar_pago(suscripcion, monto)

        messagebox.showinfo("Pago registrado", "El pago fue registrado correctamente", parent=ventana)

        entry_id.delete(0, ctk.END)
        entry_monto.delete(0, ctk.END)

        cargar_suscripciones()
        cargar_suscripciones_lista()

    def ver_historial():
        
        suscripcion = entry_id.get()

        if suscripcion == "":
            messagebox.showerror(
                "Error",
                "Seleccione una suscripción primero",
                parent=ventana
                
            )
            return

        try:
            suscripcion = int(suscripcion)
        except ValueError:
            messagebox.showerror(
                "Error",
                "ID de suscripción inválido",
                parent=ventana
            )
            return

        historial = ver_historial_pagos(suscripcion)
        
        if not historial:
            messagebox.showinfo(
                "Historial",
                "No hay pagos registrados",
                parent=ventana
            )
            return
        
        # -------- VENTANA HISTORIAL --------
         
        ventana_historial = ctk.CTkToplevel(ventana)
        ventana_historial.title("Historial de Pagos")
        ventana_historial.geometry("500x350")
        
        tabla_historial = ttk.Treeview(
            ventana_historial,
            columns=("ID", "Monto", "Fecha"),
            show="headings"
        )
        
        tabla_historial.heading("ID", text="ID")
        tabla_historial.heading("Monto", text="Monto")
        tabla_historial.heading("Fecha", text="Fecha")
        
        tabla_historial.column("Monto", width=120, anchor="center")
        tabla_historial.column("Fecha", width=200, anchor="center")
        
        tabla_historial.pack(fill="both", expand=True, padx=10, pady=10)
        
        for pago_id, monto, fecha in historial:
            tabla_historial.insert("", "end", values=(monto, fecha))

    def cargar_suscripciones_lista():

        for fila in tabla_sus.get_children():
            tabla_sus.delete(fila)

        datos = ver_suscripciones_completas()

        for sus in datos:
            id_s, cliente, plan, inicio, vence, pagado, deuda = sus
            tabla_sus.insert("", "end", values=(id_s, cliente, plan))

    def eliminar_pago_seleccionado():
        
        suscripcion = entry_id.get()
        
        if suscripcion == "":
            
            messagebox.showerror("Error", "Selecciona una suscripción", parent=ventana)
            return
        
        confirmar = messagebox.askyesno(
            
            "Confirmar",
            "¿Seguro que deseas eliminar un pago?", 
            parent=ventana
            
      )
        
        if not confirmar:
            return

        # obtener último pago
         
        historial = ver_historial_pagos(int(suscripcion))
        
        if not historial:
            messagebox.showinfo("Información", "No hay pagos para eliminar", parent=ventana)
            return
        
        pago_id = historial[-1][0]
        
        eliminar_pago(pago_id)
        
        messagebox.showinfo("Pago eliminado", "El pago fue eliminado", parent=ventana)
        
        cargar_suscripciones()


    def crear_suscripcion_rapida():

        cliente = entry_id_cliente.get()
        membresia = entry_id_membresia.get()

        if cliente == "" or membresia == "":
            messagebox.showerror("Error", "Debes ingresar cliente y membresía", parent=ventana)
            return

        try:
            cliente = int(cliente)
            membresia = int(membresia)
        except:
            messagebox.showerror("Error", "IDs inválidos", parent=ventana)
            return

        crear_suscripcion(cliente, membresia)

        messagebox.showinfo("Éxito", "Suscripción creada", parent=ventana)

        cargar_suscripciones()
        cargar_suscripciones_lista()

    # -------- EVENTOS --------

    tabla.bind("<<TreeviewSelect>>", seleccionar_fila)
    tabla_clientes.bind("<<TreeviewSelect>>", seleccionar_cliente)
    tabla_sus.bind("<<TreeviewSelect>>", seleccionar_suscripcion)

    # -------- BOTONES --------

    frame_botones = ctk.CTkFrame(scroll)
    frame_botones.pack(pady=5)

    ctk.CTkButton(frame_buscar, text="Buscar", command=buscar_cliente).grid(row=0, column=2, padx=10)

    ctk.CTkButton(frame_buscar, text="Crear Suscripción", command=crear_suscripcion_rapida).grid(row=3, column=0, columnspan=2, pady=5)

    ctk.CTkButton(frame_botones, text="Registrar Pago", width=130, height=32, command=pagar).grid(row=0, column=0, padx=10)
    ctk.CTkButton(frame_botones, text="Ver Historial", width=130, height=32, command=ver_historial).grid(row=0, column=1, padx=10)
    ctk.CTkButton(frame_botones, text="Actualizar", width=130, height=32, command=lambda: [cargar_suscripciones(), cargar_suscripciones_lista()]).grid(row=0, column=2, padx=10)
    ctk.CTkButton(frame_botones, text="← Volver", width=110, height=32, command=ventana.destroy).grid(row=0, column=3, padx=10)
    
    boton_eliminar = ctk.CTkButton(
        frame_botones,
        text="Eliminar Pago",
        fg_color="#d9534f",
        command=eliminar_pago_seleccionado
    )
    
    boton_eliminar.grid(row=0, column=4, padx=10)
    # -------- CARGA INICIAL --------

    cargar_clientes()
    cargar_suscripciones()
    cargar_suscripciones_lista()