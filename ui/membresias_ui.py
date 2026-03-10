import customtkinter as ctk
from tkinter import ttk, messagebox

from modulos.membresias import (
    crear_membresia,
    ver_membresias,
    eliminar_membresia,
    editar_membresia
)


def abrir_ventana_membresias(parent):

    # ---------- CONFIGURACION DE VENTANA ----------
    ventana = ctk.CTkToplevel(parent)
    ventana.title("Membresías")
    ventana.geometry("1000x700")
    ventana.resizable(True, True)

    ventana.lift()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))
    ventana.focus_force()

    # ---------- CONTENEDOR FORMULARIO ----------
    frame_contenedor = ctk.CTkFrame(ventana, fg_color="transparent")
    frame_contenedor.pack(pady=20)

    # ---------- FORMULARIO ----------
    frame_form = ctk.CTkFrame(frame_contenedor)
    frame_form.pack(side="left", padx=50)

    ctk.CTkLabel(
        frame_form,
        text="Nombre Plan",
        font=("Segoe UI", 16)
    ).grid(row=0, column=0, padx=10, pady=10)

    entry_nombre = ctk.CTkEntry(
        frame_form,
        font=("Segoe UI", 16),
        height=35,
        width=220
    )
    entry_nombre.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(
        frame_form,
        text="Precio",
        font=("Segoe UI", 16)
    ).grid(row=1, column=0, padx=10, pady=10)

    entry_precio = ctk.CTkEntry(
        frame_form,
        font=("Segoe UI", 16),
        height=35,
        width=220
    )
    entry_precio.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(
        frame_form,
        text="Duración (días)",
        font=("Segoe UI", 16)
    ).grid(row=2, column=0, padx=10, pady=10)

    entry_dias = ctk.CTkEntry(
        frame_form,
        font=("Segoe UI", 16),
        height=35,
        width=220
    )
    entry_dias.grid(row=2, column=1, padx=10, pady=10)

    # ---------- BOTON REGRESAR INDEPENDIENTE ----------
    boton_regresar = ctk.CTkButton(
    ventana,
    text="← Volver al menú",
    width=170,
    height=35,
    font=("Segoe UI", 14),
    command=ventana.destroy
)

    # mover solo el botón, sin afectar el formulario
    boton_regresar.place(relx=0.97, y=30, anchor="ne")
    
    # ---------- ESTILO DE TABLA ----------
    style = ttk.Style()

    style.configure(
        "Treeview",
        font=("Segoe UI", 15),
        rowheight=32
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 16, "bold")
    )

    # ---------- TABLA ----------
    frame_tabla = ctk.CTkFrame(ventana)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)

    tabla = ttk.Treeview(
        frame_tabla,
        columns=("ID", "PLAN", "PRECIO", "DIAS"),
        show="headings",
        height=15
    )

    tabla.heading("ID", text="ID")
    tabla.heading("PLAN", text="Nombre Plan")
    tabla.heading("PRECIO", text="Precio")
    tabla.heading("DIAS", text="Duración (días)")

    tabla.column("ID", width=80, anchor="center")
    tabla.column("PLAN", width=350, anchor="center")
    tabla.column("PRECIO", width=150, anchor="center")
    tabla.column("DIAS", width=200, anchor="center")

    tabla.pack(fill="both", expand=True)

    # ---------- CARGAR TABLA ----------
    def cargar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)

        membresias = ver_membresias()

        for m in membresias:
            tabla.insert("", "end", values=m)

    # ---------- SELECCIONAR FILA ----------
    def seleccionar(event):
        seleccion = tabla.selection()

        if not seleccion:
            return

        item = tabla.item(seleccion[0])
        datos = item["values"]

        entry_nombre.delete(0, "end")
        entry_precio.delete(0, "end")
        entry_dias.delete(0, "end")

        entry_nombre.insert(0, datos[1])
        entry_precio.insert(0, datos[2])
        entry_dias.insert(0, datos[3])

    tabla.bind("<<TreeviewSelect>>", seleccionar)

    # ---------- LIMPIAR CAMPOS ----------
    def limpiar_campos():
        entry_nombre.delete(0, "end")
        entry_precio.delete(0, "end")
        entry_dias.delete(0, "end")

    # ---------- CREAR MEMBRESIA ----------
    def guardar():
        try:
            nombre = entry_nombre.get().strip()
            precio = float(entry_precio.get())
            dias = int(entry_dias.get())

            crear_membresia(nombre, precio, dias)

            cargar_tabla()
            limpiar_campos()

            messagebox.showinfo("Éxito", "Membresía creada correctamente")

        except:
            messagebox.showerror("Error", "Datos inválidos")

    # ---------- EDITAR MEMBRESIA ----------
    def editar():
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una membresía")
            return

        try:
            item = tabla.item(seleccion[0])
            id_membresia = item["values"][0]

            nombre = entry_nombre.get().strip()
            precio = float(entry_precio.get())
            dias = int(entry_dias.get())

            editar_membresia(id_membresia, nombre, precio, dias)

            cargar_tabla()
            limpiar_campos()

            messagebox.showinfo("Éxito", "Membresía actualizada correctamente")

        except:
            messagebox.showerror("Error", "Datos inválidos")

    # ---------- ELIMINAR MEMBRESIA ----------
    def eliminar():
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una membresía")
            return

        item = tabla.item(seleccion[0])
        id_membresia = item["values"][0]

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Deseas eliminar esta membresía?"
        )

        if confirmar:
            eliminar_membresia(id_membresia)
            cargar_tabla()
            limpiar_campos()
            messagebox.showinfo("Éxito", "Membresía eliminada correctamente")

    # ---------- BOTONES ----------
    frame_botones = ctk.CTkFrame(ventana)
    frame_botones.pack(pady=10)

    boton_crear = ctk.CTkButton(
        frame_botones,
        text="Crear Membresía",
        width=200,
        height=40,
        font=("Segoe UI", 16),
        command=guardar
    )
    boton_crear.grid(row=0, column=0, padx=10)

    boton_editar = ctk.CTkButton(
        frame_botones,
        text="Editar",
        width=200,
        height=40,
        font=("Segoe UI", 16),
        fg_color="#f0ad4e",
        hover_color="#d9962f",
        command=editar
    )
    boton_editar.grid(row=0, column=1, padx=10)

    boton_eliminar = ctk.CTkButton(
        frame_botones,
        text="Eliminar",
        width=200,
        height=40,
        font=("Segoe UI", 16),
        fg_color="red",
        hover_color="#b30000",
        command=eliminar
    )
    boton_eliminar.grid(row=0, column=2, padx=10)

    # ---------- CARGAR DATOS ----------
    cargar_tabla()