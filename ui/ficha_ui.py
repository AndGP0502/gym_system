import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
import os

from modulos.ficha_cliente import (
    obtener_ficha, guardar_ficha, guardar_foto, obtener_foto,
    agregar_medida, obtener_historial, eliminar_medida
)
from modulos.rutas import get_assets_dir

FOTO_DEFAULT = os.path.join(get_assets_dir(), "default_avatar.png")


def _crear_avatar_default():
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(ruta, exist_ok=True)
    ruta_img = os.path.join(ruta, "default_avatar.png")
    if not os.path.exists(ruta_img):
        img = Image.new("RGB", (200, 200), color="#3f3f3f")
        draw = ImageDraw.Draw(img)
        draw.ellipse([50, 30, 150, 130], fill="#666666")
        draw.ellipse([30, 120, 170, 230], fill="#666666")
        img.save(ruta_img)
    return ruta_img


def _fmt(val):
    """Formatea un número con 2 decimales y coma."""
    try:
        return f"{float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(val) if val else "—"


def abrir_ficha_cliente(parent, cliente_id: int, nombre_cliente: str):

    popup = ctk.CTkToplevel(parent)
    popup.title(f"Ficha — {nombre_cliente}")
    popup.state("zoomed")
    popup.resizable(True, True)
    popup.attributes("-topmost", True)
    popup.after(300, lambda: popup.attributes("-topmost", False))
    popup.lift()
    popup.focus_force()
    popup.grab_set()

    def traer_al_frente():
        popup.attributes("-topmost", True)
        popup.lift()
        popup.focus_force()
        popup.after(200, lambda: popup.attributes("-topmost", False))

    scroll = ctk.CTkScrollableFrame(popup)
    scroll.pack(fill="both", expand=True)

    # ── HEADER ───────────────────────────────────────────────────────────────
    frame_header = ctk.CTkFrame(scroll, corner_radius=18)
    frame_header.pack(fill="x", padx=20, pady=(20, 10))

    ctk.CTkLabel(frame_header, text=f"Ficha de {nombre_cliente}",
                 font=("Segoe UI", 26, "bold")).pack(side="left", padx=20, pady=18)

    ctk.CTkButton(frame_header, text="✕ Cerrar", width=120, height=38,
                  fg_color="#2A2A2A", hover_color="#3A3A3A",
                  command=popup.destroy).pack(side="right", padx=(20, 0), pady=18)

    # ── PANEL SUPERIOR: foto + datos generales ────────────────────────────────
    frame_superior = ctk.CTkFrame(scroll, corner_radius=18)
    frame_superior.pack(fill="x", padx=20, pady=10)
    frame_superior.columnconfigure(1, weight=1)

    # ── Foto ─────────────────────────────────────────────────────────────────
    frame_foto = ctk.CTkFrame(frame_superior, corner_radius=15, width=220, fg_color="#2b2b2b")
    frame_foto.grid(row=0, column=0, padx=20, pady=20, sticky="n")
    frame_foto.pack_propagate(False)

    foto_ruta   = {"valor": obtener_foto(cliente_id)}
    foto_imagen = {"ref": None}

    def cargar_imagen_foto(ruta):
        try:
            img = Image.open(ruta).resize((180, 180))
        except Exception:
            ruta = _crear_avatar_default()
            img  = Image.open(ruta).resize((180, 180))
        mask = Image.new("L", (180, 180), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, 180, 180], fill=255)
        img_circular = Image.new("RGBA", (180, 180))
        img_circular.paste(img.convert("RGBA"), mask=mask)
        foto_tk = ctk.CTkImage(light_image=img_circular, size=(180, 180))
        foto_imagen["ref"] = foto_tk
        lbl_foto.configure(image=foto_tk, text="")

    lbl_foto = ctk.CTkLabel(frame_foto, text="📷\nToca para\nagregar foto",
                            width=180, height=180, cursor="hand2")
    lbl_foto.pack(pady=(15, 8))
    lbl_foto.bind("<Button-1>", lambda e: seleccionar_foto())
    cargar_imagen_foto(foto_ruta["valor"] or _crear_avatar_default())

    def seleccionar_foto():
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto del cliente",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp")],
            parent=popup
        )
        if ruta:
            ruta_guardada = guardar_foto(cliente_id, ruta)
            foto_ruta["valor"] = ruta_guardada
            cargar_imagen_foto(ruta_guardada)
        traer_al_frente()

    ctk.CTkButton(frame_foto, text="📷 Cambiar foto", height=36, width=160,
                  fg_color="#1f6aa5", hover_color="#174f7a",
                  command=seleccionar_foto).pack(pady=(0, 15))

    # ── Datos generales ───────────────────────────────────────────────────────
    frame_datos = ctk.CTkFrame(frame_superior, corner_radius=15, fg_color="#2b2b2b")
    frame_datos.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")

    ctk.CTkLabel(frame_datos, text="Información General",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(18, 10))

    frame_campos = ctk.CTkFrame(frame_datos, fg_color="transparent")
    frame_campos.pack(fill="x", padx=20)
    frame_campos.columnconfigure(1, weight=1)
    frame_campos.columnconfigure(3, weight=1)

    ctk.CTkLabel(frame_campos, text="Objetivo:", font=("Segoe UI", 13, "bold")).grid(
        row=0, column=0, padx=(0, 10), pady=8, sticky="w")
    objetivos = ["Perdida de grasa", "Aumento de masa muscular", "Entrenamiento funcional",
                 "Atletas", "Mantenimiento", "Rehabilitación", "Otro"]
    combo_objetivo = ctk.CTkComboBox(frame_campos, values=objetivos, width=240, height=36)
    combo_objetivo.grid(row=0, column=1, padx=(0, 25), pady=8, sticky="w")

    ctk.CTkLabel(frame_campos, text="Estado físico:", font=("Segoe UI", 13, "bold")).grid(
        row=0, column=2, padx=(0, 10), pady=8, sticky="w")
    estados = ["Principiante", "Intermedio", "Avanzado", "Atleta"]
    combo_estado = ctk.CTkComboBox(frame_campos, values=estados, width=180, height=36)
    combo_estado.grid(row=0, column=3, pady=8, sticky="w")

    ctk.CTkLabel(frame_campos, text="Notas adicionales:", font=("Segoe UI", 13, "bold")).grid(
        row=1, column=0, padx=(0, 10), pady=(10, 0), sticky="nw")
    txt_notas = ctk.CTkTextbox(frame_campos, height=60)
    txt_notas.grid(row=1, column=1, columnspan=3, pady=(10, 0), sticky="ew")

    # ── DATOS FÍSICOS ─────────────────────────────────────────────────────────
    frame_fisicos = ctk.CTkFrame(scroll, corner_radius=18)
    frame_fisicos.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_fisicos, text="Datos Físicos",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 10))

    frame_fis_inner = ctk.CTkFrame(frame_fisicos, fg_color="transparent")
    frame_fis_inner.pack(fill="x", padx=20, pady=(0, 10))

    campos_fis = [
        ("Peso (kg):",           "entry_peso_fis"),
        ("Altura (m):",          "entry_altura_fis"),
        ("Cir. Abdominal (cm):", "entry_cir"),
        ("Peso ideal (kg):",     "entry_peso_ideal"),
    ]
    entries_fis = {}
    for col_idx, (label, key) in enumerate(campos_fis):
        ctk.CTkLabel(frame_fis_inner, text=label, font=("Segoe UI", 12, "bold")).grid(
            row=0, column=col_idx * 2, padx=(0, 6), pady=6, sticky="w")
        e = ctk.CTkEntry(frame_fis_inner, width=120, height=34)
        e.grid(row=0, column=col_idx * 2 + 1, padx=(0, 20), pady=6)
        entries_fis[key] = e

    ctk.CTkLabel(frame_fis_inner, text="Status:", font=("Segoe UI", 12, "bold")).grid(
        row=1, column=0, padx=(0, 6), pady=6, sticky="w")
    status_vals = ["Principiante", "Intermedio", "Avanzado", "Atleta"]
    combo_status = ctk.CTkComboBox(frame_fis_inner, values=status_vals, width=160, height=34)
    combo_status.grid(row=1, column=1, padx=(0, 20), pady=6, sticky="w")

    ctk.CTkLabel(frame_fis_inner, text="Objetivo secundario:", font=("Segoe UI", 12, "bold")).grid(
        row=1, column=2, padx=(0, 6), pady=6, sticky="w")
    combo_obj2 = ctk.CTkComboBox(frame_fis_inner, values=objetivos, width=220, height=34)
    combo_obj2.grid(row=1, column=3, padx=(0, 20), pady=6, sticky="w")

    # ── CONDICIONES MÉDICAS ───────────────────────────────────────────────────
    frame_medicas = ctk.CTkFrame(scroll, corner_radius=18)
    frame_medicas.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_medicas, text="Condiciones Médicas",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 6))
    ctk.CTkLabel(frame_medicas, text="Marca las condiciones que aplican al cliente:",
                 font=("Segoe UI", 11), text_color="gray70").pack(anchor="w", padx=20, pady=(0, 10))

    frame_checks = ctk.CTkFrame(frame_medicas, fg_color="transparent")
    frame_checks.pack(fill="x", padx=20, pady=(0, 18))

    condiciones_config = [
        ("lesion",         "Lesión muscular o articular"),
        ("cardiovascular", "Enfermedad cardiovascular"),
        ("asfixia",        "Se asfixia con facilidad"),
        ("asmatico",       "Asmático / Epiléptico / Diabético"),
        ("medicacion",     "Toma medicación actualmente"),
        ("mareos",         "Mareos o desmayos al ejercitar"),
    ]

    checks_vars = {}
    for i, (key, label) in enumerate(condiciones_config):
        var = ctk.StringVar(value="NO")
        checks_vars[key] = var
        ctk.CTkCheckBox(
            frame_checks, text=label, variable=var,
            onvalue="SI", offvalue="NO", font=("Segoe UI", 12)
        ).grid(row=i // 3, column=i % 3, padx=15, pady=6, sticky="w")

    # ── Cargar ficha existente ────────────────────────────────────────────────
    ficha = obtener_ficha(cliente_id)
    if ficha:
        if ficha.get("objetivo"):      combo_objetivo.set(ficha["objetivo"])
        if ficha.get("estado_fisico"): combo_estado.set(ficha["estado_fisico"])
        if ficha.get("notas"):         txt_notas.insert("1.0", ficha["notas"])

        def _set_entry(entry, val):
            if val is not None:
                entry.delete(0, "end")
                entry.insert(0, str(val))

        _set_entry(entries_fis["entry_peso_fis"],   ficha.get("peso_kg"))
        _set_entry(entries_fis["entry_altura_fis"], ficha.get("altura_m"))
        _set_entry(entries_fis["entry_cir"],        ficha.get("cir_abdominal"))
        _set_entry(entries_fis["entry_peso_ideal"], ficha.get("peso_ideal"))

        if ficha.get("status_fisico"): combo_status.set(ficha["status_fisico"])
        if ficha.get("objetivo_2"):    combo_obj2.set(ficha["objetivo_2"])

        for key, var in checks_vars.items():
            valor = ficha.get(key, "NO")
            var.set("SI" if str(valor).upper() == "SI" else "NO")

    def guardar_ficha_click():
        guardar_ficha(
            cliente_id,
            objetivo       = combo_objetivo.get().strip(),
            estado_fisico  = combo_estado.get().strip(),
            condiciones    = ", ".join(
                label for key, label in condiciones_config
                if checks_vars[key].get() == "SI"
            ) or "Ninguna",
            notas          = txt_notas.get("1.0", "end").strip(),
            foto_ruta      = foto_ruta["valor"],
            peso_kg        = _safe_float(entries_fis["entry_peso_fis"].get()),
            altura_m       = _safe_float(entries_fis["entry_altura_fis"].get()),
            cir_abdominal  = _safe_float(entries_fis["entry_cir"].get()),
            status_fisico  = combo_status.get().strip(),
            objetivo_2     = combo_obj2.get().strip(),
            peso_ideal     = _safe_float(entries_fis["entry_peso_ideal"].get()),
            lesion         = checks_vars["lesion"].get(),
            cardiovascular = checks_vars["cardiovascular"].get(),
            asfixia        = checks_vars["asfixia"].get(),
            asmatico       = checks_vars["asmatico"].get(),
            medicacion     = checks_vars["medicacion"].get(),
            mareos         = checks_vars["mareos"].get(),
        )
        messagebox.showinfo("Guardado", "Ficha guardada correctamente.", parent=popup)
        traer_al_frente()

    ctk.CTkButton(
        frame_datos, text="💾 Guardar ficha",
        height=40, font=("Segoe UI", 13, "bold"),
        fg_color="#1a7a1a", hover_color="#145214",
        command=guardar_ficha_click
    ).pack(anchor="e", padx=20, pady=(12, 18))

    # ── REGISTRAR NUEVA MEDIDA ────────────────────────────────────────────────
    frame_medida = ctk.CTkFrame(scroll, corner_radius=18)
    frame_medida.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(frame_medida, text="Registrar nueva medida",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 10))

    frame_inputs = ctk.CTkFrame(frame_medida, fg_color="transparent")
    frame_inputs.pack(fill="x", padx=20, pady=(0, 5))

    # Peso
    ctk.CTkLabel(frame_inputs, text="Peso (kg):", font=("Segoe UI", 13)).grid(
        row=0, column=0, padx=(0, 8), pady=8, sticky="w")
    entry_peso = ctk.CTkEntry(frame_inputs, width=110, height=36, placeholder_text="ej: 75.5")
    entry_peso.grid(row=0, column=1, padx=(0, 20), pady=8)

    # Altura en cm
    ctk.CTkLabel(frame_inputs, text="Altura (cm):", font=("Segoe UI", 13)).grid(
        row=0, column=2, padx=(0, 8), pady=8, sticky="w")
    entry_altura = ctk.CTkEntry(frame_inputs, width=110, height=36, placeholder_text="ej: 175")
    entry_altura.grid(row=0, column=3, padx=(0, 20), pady=8)

    # IMC calculado
    ctk.CTkLabel(frame_inputs, text="IMC:", font=("Segoe UI", 13)).grid(
        row=0, column=4, padx=(0, 8), pady=8, sticky="w")
    lbl_imc = ctk.CTkLabel(frame_inputs, text="—", font=("Segoe UI", 15, "bold"),
                            text_color="#00D1FF", width=180)
    lbl_imc.grid(row=0, column=5, padx=(0, 20), pady=8)

    # Notas
    ctk.CTkLabel(frame_inputs, text="Notas:", font=("Segoe UI", 13)).grid(
        row=0, column=6, padx=(0, 8), pady=8, sticky="w")
    entry_notas_m = ctk.CTkEntry(frame_inputs, width=200, height=36)
    entry_notas_m.grid(row=0, column=7, pady=8)

    def calcular_imc_preview(event=None):
        try:
            peso   = float(entry_peso.get().replace(",", "."))
            altura = float(entry_altura.get().replace(",", "."))
            if altura > 0:
                # altura en cm → convertir a metros
                imc = round(peso / ((altura / 100) ** 2), 2)
                imc_fmt = _fmt(imc)
                if   imc < 18.5: cat, color = f"{imc_fmt} — Bajo peso",  "#FFA500"
                elif imc < 25:   cat, color = f"{imc_fmt} — Normal",     "#00D1FF"
                elif imc < 30:   cat, color = f"{imc_fmt} — Sobrepeso",  "#FFA500"
                else:            cat, color = f"{imc_fmt} — Obesidad",   "#FF4444"
                lbl_imc.configure(text=cat, text_color=color)
        except ValueError:
            lbl_imc.configure(text="—", text_color="#00D1FF")

    entry_peso.bind("<KeyRelease>", calcular_imc_preview)
    entry_altura.bind("<KeyRelease>", calcular_imc_preview)

    def agregar_medida_click():
        try:
            peso   = float(entry_peso.get().replace(",", ".").strip())
            altura = float(entry_altura.get().replace(",", ".").strip())
        except ValueError:
            messagebox.showerror("Error", "Peso y altura deben ser números.", parent=popup)
            traer_al_frente()
            return
        notas = entry_notas_m.get().strip()
        # altura en cm → se pasa directamente, agregar_medida lo convierte internamente
        imc = agregar_medida(cliente_id, peso, altura, notas)
        entry_peso.delete(0, "end")
        entry_altura.delete(0, "end")
        entry_notas_m.delete(0, "end")
        lbl_imc.configure(text="—", text_color="#00D1FF")
        cargar_historial()
        messagebox.showinfo("Medida registrada", f"Medida guardada. IMC: {_fmt(imc)}", parent=popup)
        traer_al_frente()

    ctk.CTkButton(
        frame_medida, text="➕ Agregar medida",
        height=40, font=("Segoe UI", 13, "bold"),
        fg_color="#0d6efd", hover_color="#0b5ed7",
        command=agregar_medida_click
    ).pack(anchor="e", padx=20, pady=(5, 18))

    # ── HISTORIAL DE MEDIDAS ──────────────────────────────────────────────────
    frame_historial = ctk.CTkFrame(scroll, corner_radius=18)
    frame_historial.pack(fill="x", padx=20, pady=(10, 30))

    ctk.CTkLabel(frame_historial, text="Historial de medidas",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 10))

    tabla_container = ctk.CTkFrame(frame_historial, fg_color="transparent")
    tabla_container.pack(fill="x", padx=15, pady=(0, 10))

    style = ttk.Style()
    style.configure("Ficha.Treeview", background="#3a3a3a", foreground="white",
                    fieldbackground="#3a3a3a", rowheight=32, font=("Segoe UI", 11))
    style.configure("Ficha.Treeview.Heading", background="#2f2f2f", foreground="white",
                    font=("Segoe UI", 12, "bold"))
    style.map("Ficha.Treeview", background=[("selected", "#1f6aa5")],
              foreground=[("selected", "white")])

    columnas_hist = ("ID", "Fecha", "Peso (kg)", "Altura (cm)", "IMC", "Notas")
    tabla_hist = ttk.Treeview(tabla_container, style="Ficha.Treeview",
                               columns=columnas_hist, show="headings", height=8)
    for col in columnas_hist:
        tabla_hist.heading(col, text=col)
    tabla_hist.column("ID",          anchor="center", width=50)
    tabla_hist.column("Fecha",       anchor="center", width=110)
    tabla_hist.column("Peso (kg)",   anchor="center", width=100)
    tabla_hist.column("Altura (cm)", anchor="center", width=110)
    tabla_hist.column("IMC",         anchor="center", width=200)
    tabla_hist.column("Notas",       anchor="w",      width=280)
    tabla_hist.pack(fill="x", expand=True)

    def cargar_historial():
        for fila in tabla_hist.get_children():
            tabla_hist.delete(fila)
        for id_m, fecha, peso, altura, imc, notas in obtener_historial(cliente_id):
            imc_fmt = _fmt(imc)
            if   imc < 18.5: cat = f"{imc_fmt} (Bajo peso)"
            elif imc < 25:   cat = f"{imc_fmt} (Normal)"
            elif imc < 30:   cat = f"{imc_fmt} (Sobrepeso)"
            else:            cat = f"{imc_fmt} (Obesidad)"
            tabla_hist.insert("", "end", values=(
                id_m, fecha,
                _fmt(peso),
                _fmt(altura),
                cat,
                notas or ""
            ))

    cargar_historial()

    def eliminar_medida_click():
        seleccion = tabla_hist.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona una medida para eliminar.", parent=popup)
            traer_al_frente()
            return
        fila   = tabla_hist.item(seleccion[0])["values"]
        id_med = fila[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la medida del {fila[1]}?", parent=popup):
            eliminar_medida(int(id_med))
            cargar_historial()
        traer_al_frente()

    ctk.CTkButton(
        frame_historial, text="🗑 Eliminar medida seleccionada",
        height=38, fg_color="#C0392B", hover_color="#922B21",
        command=eliminar_medida_click
    ).pack(anchor="e", padx=20, pady=(5, 18))

# ── Helper ────────────────────────────────────────────────────────────────────
def _safe_float(val: str):
    try:
        return float(str(val).replace(",", ".").strip())
    except Exception:
        return None