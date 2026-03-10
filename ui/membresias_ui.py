import customtkinter as ctk
from tkinter import ttk, messagebox

from modulos.membresias import crear_membresia, ver_membresias, eliminar_membresia


def abrir_ventana_membresias(parent):

    # ---------- CONFIGURACION DE VENTANA ----------
    ventana = ctk.CTkToplevel(parent)
    ventana.title("Membresías")
    ventana.geometry("1000x700")

    ventana.transient(parent)
    ventana.grab_set()
    ventana.lift()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))
    ventana.focus_force()

    # ---------- FORMULARIO ----------
    frame_form = ctk.CTkFrame(ventana)
    frame_form.pack(pady=20)

    ctk.CTkLabel(frame_form, text="Nombre Plan", font=("Segoe UI",16)).grid(row=0, column=0, padx=10, pady=10)

    entry_nombre = ctk.CTkEntry(frame_form, font=("Segoe UI",16), height=35, width=200)
    entry_nombre.grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(frame_form, text="Precio", font=("Segoe UI",16)).grid(row=1, column=0, padx=10, pady=10)

    entry_precio = ctk.CTkEntry(frame_form, font=("Segoe UI",16), height=35, width=200)
    entry_precio.grid(row=1, column=1, padx=10, pady=10)

    ctk.CTkLabel(frame_form, text="Duración (días)", font=("Segoe UI",16)).grid(row=2, column=0, padx=10, pady=10)

    entry_dias = ctk.CTkEntry(frame_form, font=("Segoe UI",16), height=35, width=200)
    entry_dias.grid(row=2, column=1, padx=10, pady=10)

    # ---------- ESTILO DE TABLA ----------
    style = ttk.Style()

    style.configure(
        "Treeview",
        font=("Segoe UI",15),
        rowheight=30
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI",16,"bold")
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

    # ---------- FUNCIONES ----------
    def cargar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)

        membresias = ver_membresias()

        for m in membresias:
            tabla.insert("", "end", values=m)

    def guardar():
        try:
            nombre = entry_nombre.get()
            precio = float(entry_precio.get())
            dias = int(entry_dias.get())

            crear_membresia(nombre, precio, dias)

            entry_nombre.delete(0, "end")
            entry_precio.delete(0, "end")
            entry_dias.delete(0, "end")

            cargar_tabla()

        except:
            messagebox.showerror("Error", "Datos inválidos")

    def eliminar():
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una membresía")
            return

        item = tabla.item(seleccion)
        id_membresia = item["values"][0]

        eliminar_membresia(id_membresia)

        cargar_tabla()

    # ---------- BOTONES ----------
    frame_botones = ctk.CTkFrame(ventana)
    frame_botones.pack(pady=10)

    boton_crear = ctk.CTkButton(
        frame_botones,
        text="Crear Membresía",
        width=200,
        height=40,
        font=("Segoe UI",16),
        command=guardar
    )
    boton_crear.grid(row=0, column=0, padx=10)

    boton_eliminar = ctk.CTkButton(
        frame_botones,
        text="Eliminar",
        width=200,
        height=40,
        font=("Segoe UI",16),
        fg_color="red",
        command=eliminar
    )
    boton_eliminar.grid(row=0, column=1, padx=10)

    boton_regresar = ctk.CTkButton(
        ventana,
        text="← Regresar",
        width=180,
        height=40,
        font=("Segoe UI",15),
        command=ventana.destroy
    )

    boton_regresar.pack(side="bottom", anchor="e", padx=20, pady=20)

    # ---------- BOTON REGRESAR ----------
    boton_regresar = ctk.CTkButton(
    ventana,
    text="← Regresar al menú",
    width=200,
    height=40,
    font=("Segoe UI",16),
    command=ventana.destroy
)

    boton_regresar.pack(side="bottom", anchor="e", padx=20, pady=20)

    # ---------- CARGAR DATOS ----------
    cargar_tabla()