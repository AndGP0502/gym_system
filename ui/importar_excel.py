import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import openpyxl
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "gym.db")


def _con():
    return sqlite3.connect(DB_PATH)


def importar_clientes_excel(ruta: str) -> dict:
    wb = openpyxl.load_workbook(ruta, data_only=True)

    if "Clientes" not in wb.sheetnames:
        return {"insertados": 0, "omitidos": 0, "errores": ["No se encontró la hoja 'Clientes'."]}

    ws  = wb["Clientes"]
    con = _con()
    cur = con.cursor()

    insertados = 0
    omitidos   = 0
    errores    = []

    for row in ws.iter_rows(min_row=3, values_only=True):
        if not any(row):
            continue
        try:
            nombre   = str(row[0]).strip() if row[0] else ""
            cedula   = str(row[1]).strip() if row[1] else ""
            telefono = str(row[2]).strip() if row[2] else ""
            fecha    = str(row[3]).strip() if row[3] else ""

            if hasattr(row[3], "strftime"):
                fecha = row[3].strftime("%d/%m/%Y")

            if not nombre or not cedula or not telefono or not fecha:
                omitidos += 1
                errores.append(f"Fila incompleta omitida: {row}")
                continue

            cur.execute("SELECT id FROM clientes WHERE cedula = ?", (cedula,))
            if cur.fetchone():
                omitidos += 1
                errores.append(f"Cédula duplicada omitida: {cedula} ({nombre})")
                continue

            cur.execute(
                "INSERT INTO clientes(nombre, cedula, telefono, fecha_registro) VALUES (?,?,?,?)",
                (nombre, cedula, telefono, fecha)
            )
            insertados += 1

        except Exception as e:
            errores.append(f"Error en fila: {e}")
            omitidos += 1

    con.commit()
    con.close()
    return {"insertados": insertados, "omitidos": omitidos, "errores": errores}


def importar_membresias_excel(ruta: str) -> dict:
    wb = openpyxl.load_workbook(ruta, data_only=True)

    if "Membresias" not in wb.sheetnames:
        return {"insertados": 0, "omitidos": 0, "errores": ["No se encontró la hoja 'Membresias'."]}

    ws  = wb["Membresias"]
    con = _con()
    cur = con.cursor()

    insertados = 0
    omitidos   = 0
    errores    = []

    for row in ws.iter_rows(min_row=3, values_only=True):
        if not any(row):
            continue
        try:
            nombre_plan   = str(row[0]).strip() if row[0] else ""
            precio        = float(row[1]) if row[1] is not None else None
            duracion_dias = int(row[2])   if row[2] is not None else None

            if not nombre_plan or precio is None or duracion_dias is None:
                omitidos += 1
                errores.append(f"Fila incompleta omitida: {row}")
                continue

            # Verificar duplicado por nombre_plan
            cur.execute("SELECT id FROM membresias WHERE nombre_plan = ?", (nombre_plan,))
            if cur.fetchone():
                omitidos += 1
                errores.append(f"Membresía duplicada omitida: {nombre_plan}")
                continue

            cur.execute(
                "INSERT INTO membresias(nombre_plan, precio, duracion_dias) VALUES (?,?,?)",
                (nombre_plan, precio, duracion_dias)
            )
            insertados += 1

        except Exception as e:
            errores.append(f"Error en fila: {e}")
            omitidos += 1

    con.commit()
    con.close()
    return {"insertados": insertados, "omitidos": omitidos, "errores": errores}


def abrir_ventana_importar(parent):

    ventana = ctk.CTkToplevel(parent)
    ventana.title("Importar desde Excel")
    ventana.geometry("700x500")
    ventana.resizable(False, False)
    ventana.attributes("-topmost", True)
    ventana.after(300, lambda: ventana.attributes("-topmost", False))
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    def traer_al_frente():
        ventana.attributes("-topmost", True)
        ventana.lift()
        ventana.focus_force()
        ventana.after(200, lambda: ventana.attributes("-topmost", False))

    # Layout: sidebar izquierdo fijo + área derecha con log
    frame_principal = ctk.CTkFrame(ventana, fg_color="transparent")
    frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
    frame_principal.columnconfigure(0, weight=0)
    frame_principal.columnconfigure(1, weight=1)
    frame_principal.rowconfigure(0, weight=1)

    # ── Panel izquierdo (controles) ──────────────────────────────────────────
    panel_izq = ctk.CTkFrame(frame_principal, corner_radius=18, width=380)
    panel_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
    panel_izq.pack_propagate(False)
    panel_izq.grid_propagate(False)

    ctk.CTkLabel(
        panel_izq,
        text="Importar desde Excel",
        font=("Segoe UI", 22, "bold")
    ).pack(anchor="w", padx=20, pady=(20, 5))

    ctk.CTkLabel(
        panel_izq,
        text="Selecciona el archivo y las hojas a importar",
        font=("Segoe UI", 12),
        text_color="gray60"
    ).pack(anchor="w", padx=20, pady=(0, 20))

    # Selector de archivo
    ctk.CTkLabel(panel_izq, text="Archivo Excel (.xlsx)", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=20)

    frame_ruta = ctk.CTkFrame(panel_izq, fg_color="transparent")
    frame_ruta.pack(fill="x", padx=20, pady=(5, 20))

    entry_ruta = ctk.CTkEntry(frame_ruta, height=38, state="readonly")
    entry_ruta.pack(side="left", fill="x", expand=True, padx=(0, 8))

    ruta_seleccionada = {"valor": ""}

    def seleccionar_archivo():
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")],
            parent=ventana
        )
        if ruta:
            ruta_seleccionada["valor"] = ruta
            entry_ruta.configure(state="normal")
            entry_ruta.delete(0, "end")
            entry_ruta.insert(0, ruta)
            entry_ruta.configure(state="readonly")
            lbl_estado.configure(text="")
        traer_al_frente()

    ctk.CTkButton(
        frame_ruta,
        text="Buscar",
        width=90, height=38,
        command=seleccionar_archivo
    ).pack(side="right")

    # Checkboxes
    ctk.CTkLabel(panel_izq, text="¿Qué deseas importar?", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=20)

    var_clientes   = ctk.BooleanVar(value=True)
    var_membresias = ctk.BooleanVar(value=True)

    ctk.CTkCheckBox(
        panel_izq,
        text="Clientes  (hoja 'Clientes')",
        variable=var_clientes,
        font=("Segoe UI", 13)
    ).pack(anchor="w", padx=20, pady=(10, 5))

    ctk.CTkCheckBox(
        panel_izq,
        text="Membresías  (hoja 'Membresias')",
        variable=var_membresias,
        font=("Segoe UI", 13)
    ).pack(anchor="w", padx=20, pady=(0, 25))

    # Estado
    lbl_estado = ctk.CTkLabel(panel_izq, text="", font=("Segoe UI", 12), text_color="#00D1FF")
    lbl_estado.pack(anchor="w", padx=20, pady=(0, 15))

    # Botón importar — siempre visible en el panel izquierdo
    def importar():
        ruta = ruta_seleccionada["valor"]

        if not ruta:
            messagebox.showwarning("Sin archivo", "Selecciona un archivo Excel primero.", parent=ventana)
            traer_al_frente()
            return

        if not var_clientes.get() and not var_membresias.get():
            messagebox.showwarning("Sin selección", "Selecciona al menos una opción.", parent=ventana)
            traer_al_frente()
            return

        limpiar_log()
        total_insertados = 0
        total_omitidos   = 0

        if var_clientes.get():
            escribir_log("── Importando Clientes ──────────────────")
            try:
                res = importar_clientes_excel(ruta)
                escribir_log(f"✅ Insertados: {res['insertados']}")
                escribir_log(f"⚠️  Omitidos:   {res['omitidos']}")
                for err in res["errores"]:
                    escribir_log(f"   → {err}")
                total_insertados += res["insertados"]
                total_omitidos   += res["omitidos"]
            except Exception as e:
                escribir_log(f"❌ Error: {e}")

        if var_membresias.get():
            escribir_log("── Importando Membresías ────────────────")
            try:
                res = importar_membresias_excel(ruta)
                escribir_log(f"✅ Insertados: {res['insertados']}")
                escribir_log(f"⚠️  Omitidos:   {res['omitidos']}")
                for err in res["errores"]:
                    escribir_log(f"   → {err}")
                total_insertados += res["insertados"]
                total_omitidos   += res["omitidos"]
            except Exception as e:
                escribir_log(f"❌ Error: {e}")

        escribir_log("─────────────────────────────────────────")
        escribir_log(f"TOTAL insertados: {total_insertados}  |  omitidos: {total_omitidos}")
        lbl_estado.configure(text=f"✅ Completado: {total_insertados} registros nuevos.")
        traer_al_frente()

    ctk.CTkButton(
        panel_izq,
        text="⬆ Importar datos",
        height=48,
        font=("Segoe UI", 15, "bold"),
        fg_color="#1a7a1a",
        hover_color="#145214",
        command=importar
    ).pack(fill="x", padx=20, pady=(0, 15))

    ctk.CTkButton(
        panel_izq,
        text="✕ Cerrar",
        height=40,
        fg_color="#2A2A2A",
        hover_color="#3A3A3A",
        command=ventana.destroy
    ).pack(fill="x", padx=20, pady=(0, 20))

    # ── Panel derecho (log de resultados) ────────────────────────────────────
    panel_der = ctk.CTkFrame(frame_principal, corner_radius=18)
    panel_der.grid(row=0, column=1, sticky="nsew")

    ctk.CTkLabel(
        panel_der,
        text="Resultado de la importación",
        font=("Segoe UI", 16, "bold")
    ).pack(anchor="w", padx=20, pady=(20, 10))

    log_box = ctk.CTkTextbox(panel_der, font=("Consolas", 12))
    log_box.pack(fill="both", expand=True, padx=15, pady=(0, 20))
    log_box.configure(state="disabled")

    def escribir_log(texto: str):
        log_box.configure(state="normal")
        log_box.insert("end", texto + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    def limpiar_log():
        log_box.configure(state="normal")
        log_box.delete("1.0", "end")
        log_box.configure(state="disabled")