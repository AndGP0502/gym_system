import customtkinter as ctk
from tkinter import ttk, messagebox

from modulos.membresias import crear_membresia, ver_membresias, eliminar_membresia


def abrir_ventana_membresias(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Membresías")
    ventana.geometry("700x550")

    frame = ctk.CTkFrame(ventana)
    frame.pack(pady=20)

    ctk.CTkLabel(frame, text="Nombre Plan").grid(row=0, column=0, padx=10, pady=5)
    entry_nombre = ctk.CTkEntry(frame)
    entry_nombre.grid(row=0, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Precio").grid(row=1, column=0, padx=10, pady=5)
    entry_precio = ctk.CTkEntry(frame)
    entry_precio.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(frame, text="Duración (días)").grid(row=2, column=0, padx=10, pady=5)
    entry_dias = ctk.CTkEntry(frame)
    entry_dias.grid(row=2, column=1, padx=10, pady=5)

    # Tabla de Membresias
    tabla = ttk.Treeview(
        ventana,
        columns=("ID", "PLAN", "PRECIO", "DIAS"),
        show="headings",
        height=8
    )
    tabla.heading("ID", text="ID")
    tabla.heading("PLAN", text="Nombre Plan")
    tabla.heading("PRECIO", text="Precio")
    tabla.heading("DIAS", text="Duración (días)")

    tabla.column("ID", width=50, anchor="center")
    tabla.column("PLAN", width=200, anchor="center")
    tabla.column("PRECIO", width=100, anchor="center")
    tabla.column("DIAS", width=120, anchor="center")

    tabla.pack(pady=20)

    # Cargar Tabla
    def cargar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)

        membresias = ver_membresias()

        for membresia in membresias:
            tabla.insert("", "end", values=membresia)

    def guardar():
        try:
            nombre = entry_nombre.get().strip()
            precio = float(entry_precio.get())
            dias = int(entry_dias.get())

            crear_membresia(nombre, precio, dias)

            entry_nombre.delete(0, "end")
            entry_precio.delete(0, "end")
            entry_dias.delete(0, "end")

            cargar_tabla()
            messagebox.showinfo("Éxito", "Membresía creada correctamente")

        except ValueError:
            messagebox.showerror("Error", "Precio y duración deben ser numéricos")

    # Eliminar Membresia
    def eliminar():
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una membresía para eliminar")
            return

        item = tabla.item(seleccion[0])
        datos = item["values"]

        id_membresia = datos[0]
        nombre_plan = datos[1]

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar la membresía '{nombre_plan}'?"
        )

        if confirmar:
            eliminar_membresia(id_membresia)
            cargar_tabla()
            messagebox.showinfo("Éxito", "Membresía eliminada correctamente")

    # Boton Crear
    boton_crear = ctk.CTkButton(
        ventana,
        text="Crear Membresía",
        command=guardar
    )
    boton_crear.pack(pady=10)

    #Boton Eliminar
    boton_eliminar = ctk.CTkButton(
        ventana,
        text="Eliminar Membresía",
        command=eliminar,
        fg_color="red",
        hover_color="darkred"
    )
    boton_eliminar.pack(pady=10)

    #boton Regrear al menu
    boton_regresar = ctk.CTkButton(
        ventana,
        text="← Regresar al menú",
        command=ventana.destroy
    )

    boton_regresar.pack(
        side="bottom",
        anchor="e",
        padx=50,
        pady=50
    )
    
    #Cargar membresia al abrir
    cargar_tabla()