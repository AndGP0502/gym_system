from modulos.ventanas import maximizar
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys
from datetime import datetime

from modulos.rutas import get_db_path

DB_PATH = get_db_path()


def _con():
    return sqlite3.connect(DB_PATH)


def init_tabla_asistencia():
    """Crea la tabla de asistencia si no existe."""
    con = _con()
    con.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id  INTEGER,
            cedula      TEXT,
            nombre      TEXT,
            fecha       TEXT,
            hora        TEXT,
            estado      TEXT,
            vencimiento TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)
    con.commit()
    con.close()


init_tabla_asistencia()


def registrar_asistencia(cedula: str) -> dict:
    """
    Busca al cliente por cédula, verifica su membresía y registra asistencia.
    Devuelve info del cliente y estado.
    """
    con = _con()
    cur = con.cursor()

    # Buscar cliente
    cur.execute("""
        SELECT id, nombre, cedula FROM clientes WHERE cedula = ?
    """, (cedula,))
    cliente = cur.fetchone()

    if not cliente:
        con.close()
        return {"ok": False, "error": "Cliente no encontrado con esa cédula."}

    cliente_id, nombre, ced = cliente

    # Buscar suscripción activa
    cur.execute("""
        SELECT s.fecha_vencimiento, m.nombre_plan, s.pagado, s.pendiente
        FROM suscripciones s
        JOIN membresias m ON s.membresia_id = m.id
        WHERE s.cliente_id = ?
        ORDER BY s.fecha_vencimiento DESC
        LIMIT 1
    """, (cliente_id,))
    sus = cur.fetchone()

    hoy        = datetime.now().strftime("%Y-%m-%d")
    hora       = datetime.now().strftime("%H:%M:%S")
    fecha_disp = datetime.now().strftime("%d/%m/%Y")

    if not sus:
        estado      = "SIN MEMBRESÍA"
        vencimiento = "—"
        plan        = "—"
        alerta      = "⚠️ No tiene membresía registrada."
    else:
        vencimiento = sus[0]
        plan        = sus[1]
        pagado      = float(sus[2])
        pendiente   = float(sus[3])

        try:
            fecha_venc = datetime.strptime(vencimiento, "%Y-%m-%d")
            dias_rest  = (fecha_venc - datetime.now()).days
        except Exception:
            dias_rest = -1

        if dias_rest < 0:
            estado = "VENCIDO"
            alerta = f"❌ Membresía VENCIDA hace {abs(dias_rest)} días."
        elif dias_rest <= 5:
            estado = "POR VENCER"
            alerta = f"⚠️ Membresía vence en {dias_rest} días."
        else:
            estado = "ACTIVO"
            alerta = f"✅ Activo — {dias_rest} días restantes."

        if pendiente > 0:
            alerta += f"\n💳 Tiene un pago pendiente de ${pendiente:.2f}"

    # Registrar asistencia
    con.execute("""
        INSERT INTO asistencia (cliente_id, cedula, nombre, fecha, hora, estado, vencimiento)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cliente_id, ced, nombre, hoy, hora, estado, vencimiento))
    con.commit()
    con.close()

    return {
        "ok":         True,
        "nombre":     nombre,
        "cedula":     ced,
        "plan":       plan,
        "estado":     estado,
        "vencimiento": vencimiento,
        "hora":       hora,
        "fecha":      fecha_disp,
        "alerta":     alerta,
    }


def abrir_ventana_asistencia(parent):
    ventana = ctk.CTkToplevel(parent)
    ventana.title("Registro de Asistencia")
    maximizar(ventana)
    ventana.resizable(True, True)
    ventana.attributes("-topmost", True)
    ventana.after(300, lambda: ventana.attributes("-topmost", False))
    ventana.lift()
    ventana.focus_force()

    def traer_al_frente():
        ventana.attributes("-topmost", True)
        ventana.lift()
        ventana.focus_force()
        ventana.after(200, lambda: ventana.attributes("-topmost", False))

    scroll = ctk.CTkScrollableFrame(ventana, fg_color="#1e1e1e")
    scroll.pack(fill="both", expand=True)

    # ── HEADER ────────────────────────────────────────────────────────────────
    frame_header = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#2b2b2b")
    frame_header.pack(fill="x", padx=20, pady=(20, 10))

    ctk.CTkLabel(frame_header, text="📋 Registro de Asistencia",
                 font=("Segoe UI", 26, "bold")).pack(side="left", padx=20, pady=18)
    ctk.CTkButton(frame_header, text="← Volver", width=120, height=38,
                  fg_color="#2A2A2A", hover_color="#3A3A3A",
                  command=ventana.destroy).pack(side="right", padx=20, pady=18)

    # ── RELOJ EN TIEMPO REAL ──────────────────────────────────────────────────
    frame_reloj = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#2b2b2b")
    frame_reloj.pack(fill="x", padx=20, pady=10)

    lbl_fecha_hora = ctk.CTkLabel(frame_reloj, text="",
                                   font=("Segoe UI", 18, "bold"),
                                   text_color="#00D1FF")
    lbl_fecha_hora.pack(pady=14)

    def actualizar_reloj():
        ahora = datetime.now().strftime("%A %d/%m/%Y  —  %H:%M:%S")
        lbl_fecha_hora.configure(text=ahora.capitalize())
        ventana.after(1000, actualizar_reloj)

    actualizar_reloj()

    # ── REGISTRO ──────────────────────────────────────────────────────────────
    frame_registro = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#2b2b2b")
    frame_registro.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_registro, text="Registrar Asistencia",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 10))

    frame_input = ctk.CTkFrame(frame_registro, fg_color="transparent")
    frame_input.pack(fill="x", padx=20, pady=(0, 10))

    ctk.CTkLabel(frame_input, text="Cédula del cliente:",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=(0, 10))

    entry_cedula = ctk.CTkEntry(frame_input, width=220, height=42,
                                font=("Segoe UI", 14),
                                placeholder_text="Ingresa la cédula")
    entry_cedula.pack(side="left", padx=(0, 10))
    entry_cedula.focus_set()

    btn_registrar = ctk.CTkButton(frame_input, text="✅ Registrar",
                                   width=140, height=42,
                                   font=("Segoe UI", 13, "bold"),
                                   fg_color="#1a7a1a", hover_color="#145214")
    btn_registrar.pack(side="left")

    # ── RESULTADO ─────────────────────────────────────────────────────────────
    frame_resultado = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#2b2b2b")
    frame_resultado.pack(fill="x", padx=20, pady=10)

    lbl_nombre    = ctk.CTkLabel(frame_resultado, text="",
                                  font=("Segoe UI", 22, "bold"))
    lbl_nombre.pack(pady=(16, 4))

    lbl_alerta    = ctk.CTkLabel(frame_resultado, text="",
                                  font=("Segoe UI", 14), wraplength=600)
    lbl_alerta.pack(pady=(0, 16))

    # ── HISTORIAL DEL DÍA ─────────────────────────────────────────────────────
    frame_historial = ctk.CTkFrame(scroll, corner_radius=18, fg_color="#2b2b2b")
    frame_historial.pack(fill="x", padx=20, pady=(10, 30))

    ctk.CTkLabel(frame_historial, text="Asistencia de Hoy",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 8))

    style = ttk.Style()
    style.configure("Asist.Treeview", background="#3a3a3a", foreground="white",
                    fieldbackground="#3a3a3a", rowheight=34, font=("Segoe UI", 11))
    style.configure("Asist.Treeview.Heading", background="#2f2f2f", foreground="white",
                    font=("Segoe UI", 12, "bold"))
    style.map("Asist.Treeview", background=[("selected", "#1f6aa5")],
              foreground=[("selected", "white")])

    columnas = ("Cédula", "Nombre", "Estado", "Vencimiento", "Hora")
    tabla = ttk.Treeview(frame_historial, style="Asist.Treeview",
                          columns=columnas, show="headings", height=12)
    for col in columnas:
        tabla.heading(col, text=col)
    tabla.column("Cédula",      anchor="center", width=130)
    tabla.column("Nombre",      anchor="w",      width=250)
    tabla.column("Estado",      anchor="center", width=130)
    tabla.column("Vencimiento", anchor="center", width=130)
    tabla.column("Hora",        anchor="center", width=100)

    tabla.tag_configure("ACTIVO",       background="#1a3d1a", foreground="#90ee90")
    tabla.tag_configure("VENCIDO",      background="#3d1a1a", foreground="#ff6b6b")
    tabla.tag_configure("POR VENCER",   background="#3d3d1a", foreground="#ffd700")
    tabla.tag_configure("SIN MEMBRESÍA",background="#2a2a2a", foreground="#aaaaaa")

    sb = ttk.Scrollbar(frame_historial, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=sb.set)
    tabla.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 16))
    sb.pack(side="right", fill="y", pady=(0, 16), padx=(0, 10))

    def cargar_historial():
        for fila in tabla.get_children():
            tabla.delete(fila)
        hoy = datetime.now().strftime("%Y-%m-%d")
        con = _con()
        filas = con.execute("""
            SELECT cedula, nombre, estado, vencimiento, hora
            FROM asistencia WHERE fecha = ?
            ORDER BY id DESC
        """, (hoy,)).fetchall()
        con.close()
        for f in filas:
            tabla.insert("", "end", values=f, tags=(f[2],))

    def registrar():
        cedula = entry_cedula.get().strip()
        if not cedula:
            messagebox.showwarning("Advertencia", "Ingresa una cédula.", parent=ventana)
            traer_al_frente()
            return

        resultado = registrar_asistencia(cedula)

        if not resultado["ok"]:
            lbl_nombre.configure(text="❌ No encontrado", text_color="#ff6b6b")
            lbl_alerta.configure(text=resultado["error"], text_color="#ff6b6b")
            traer_al_frente()
            return

        # Mostrar resultado
        lbl_nombre.configure(text=f"{resultado['nombre']}  —  {resultado['hora']}",
                              text_color="white")

        estado = resultado["estado"]
        if estado == "ACTIVO":
            color = "#90ee90"
        elif estado == "VENCIDO":
            color = "#ff6b6b"
        elif estado == "POR VENCER":
            color = "#ffd700"
        else:
            color = "#aaaaaa"

        lbl_alerta.configure(text=resultado["alerta"], text_color=color)

        entry_cedula.delete(0, "end")
        entry_cedula.focus_set()
        cargar_historial()
        traer_al_frente()

    btn_registrar.configure(command=registrar)
    entry_cedula.bind("<Return>", lambda e: registrar())

    cargar_historial()