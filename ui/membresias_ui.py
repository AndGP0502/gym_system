import customtkinter as ctk
from tkinter import ttk

from modulos.membresias import crear_membresia, ver_membresias


def abrir_ventana_membresias(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Membresías")
    ventana.geometry("600x400")

    frame = ctk.CTkFrame(ventana)
    frame.pack(pady=20)

    ctk.CTkLabel(frame, text="Nombre Plan").grid(row=0, column=0)
    entry_nombre = ctk.CTkEntry(frame)
    entry_nombre.grid(row=0, column=1)

    ctk.CTkLabel(frame, text="Precio").grid(row=1, column=0)
    entry_precio = ctk.CTkEntry(frame)
    entry_precio.grid(row=1, column=1)

    ctk.CTkLabel(frame, text="Duración (días)").grid(row=2, column=0)
    entry_dias = ctk.CTkEntry(frame)
    entry_dias.grid(row=2, column=1)

    def guardar():

        nombre = entry_nombre.get()
        precio = float(entry_precio.get())
        dias = int(entry_dias.get())

        crear_membresia(nombre, precio, dias)

    boton = ctk.CTkButton(
        ventana,
        text="Crear Membresía",
        command=guardar
    )

    boton.pack(pady=10)