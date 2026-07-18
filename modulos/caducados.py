"""
Modulo de Clientes Caducados
----------------------------
Ventana dedicada para ver todos los clientes cuya membresia ya vencio.
- Busqueda en vivo por cedula o nombre (sin IDs visibles)
- Filtro por mes/año de vencimiento
- Dias transcurridos desde el vencimiento
- Colores segun antiguedad del vencimiento
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from datetime import datetime

from modulos.suscripciones import ver_clientes_caducados_detalle


def abrir_ventana_caducados(parent):

    ventana = tb.Toplevel(parent)
    ventana.title("Clientes Caducados")
    ventana.geometry("1100x600")
    ventana.resizable(True, True)

    parent.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width()  // 2) - 550
    y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
    ventana.geometry(f"+{x}+{y}")

    ventana.lift()
    ventana.focus_force()
    ventana.attributes("-topmost", True)
    ventana.after(200, lambda: ventana.attributes("-topmost", False))

    frame = tb.Frame(ventana, padding=20)
    frame.pack(fill="both", expand=True)

    # ---------- HEADER ----------
    tb.Label(frame, text="Clientes con Membresia Caducada",
             font=("Segoe UI", 18, "bold"), bootstyle="danger").pack(anchor="w", pady=(0, 4))
    tb.Label(frame,
             text="Clientes cuya suscripcion ya vencio a la fecha de hoy. "
                  "Utiles para contactar y ofrecer renovacion.",
             font=("Segoe UI", 10), foreground="gray").pack(anchor="w", pady=(0, 14))

    # ---------- BUSCADOR Y FILTROS ----------
    frame_filtros = tb.Frame(frame)
    frame_filtros.pack(fill="x", pady=(0, 10))

    tb.Label(frame_filtros, text="Buscar (cedula o nombre):",
             font=("Segoe UI", 11)).pack(side="left", padx=(0, 8))
    entry_buscar = tb.Entry(frame_filtros, width=26)
    entry_buscar.pack(side="left", padx=(0, 14))

    tb.Label(frame_filtros, text="Mes venc.:",
             font=("Segoe UI", 11)).pack(side="left", padx=(0, 6))
    meses = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    combo_mes = ttk.Combobox(frame_filtros, values=meses, width=12, state="readonly")
    combo_mes.set("Todos")
    combo_mes.pack(side="left", padx=(0, 10))

    tb.Label(frame_filtros, text="Año:",
             font=("Segoe UI", 11)).pack(side="left", padx=(0, 6))
    anios = ["Todos"] + [str(a) for a in range(2020, 2101)]
    combo_anio = ttk.Combobox(frame_filtros, values=anios, width=8, state="readonly")
    combo_anio.set("Todos")
    combo_anio.pack(side="left", padx=(0, 10))

    # ---------- TABLA ----------
    tabla_container = tb.Frame(frame)
    tabla_container.pack(fill="both", expand=True)

    style = ttk.Style()
    style.configure("Cad.Treeview",         font=("Segoe UI", 10), rowheight=32)
    style.configure("Cad.Treeview.Heading", font=("Segoe UI", 11, "bold"))

    columnas = ("Cedula", "Cliente", "Telefono", "Plan",
                "Inicio", "Vencio", "Dias vencido", "Pagado", "Pendiente")
    tabla = ttk.Treeview(tabla_container, columns=columnas, show="headings",
                         height=16, style="Cad.Treeview")
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=100, anchor="center", minwidth=70)
    tabla.column("Cliente",  width=210, anchor="w", minwidth=120)
    tabla.column("Telefono", width=110, anchor="center", minwidth=80)
    tabla.column("Plan",     width=170, anchor="w", minwidth=100)

    # Colores segun cuanto tiempo lleva vencida la membresia
    tabla.tag_configure("reciente", background="#fff3cd", foreground="#664d03")  # <= 7 dias
    tabla.tag_configure("vencido",  background="#f8d7da", foreground="#842029")  # 8 - 30 dias
    tabla.tag_configure("antiguo",  background="#f5b7b1", foreground="#641e16")  # > 30 dias

    sb_y = ttk.Scrollbar(tabla_container, orient="vertical",   command=tabla.yview)
    sb_x = ttk.Scrollbar(tabla_container, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
    tabla.grid(row=0, column=0, sticky="nsew")
    sb_y.grid(row=0, column=1, sticky="ns")
    sb_x.grid(row=1, column=0, sticky="ew")
    tabla_container.grid_rowconfigure(0, weight=1)
    tabla_container.grid_columnconfigure(0, weight=1)

    # ---------- FOOTER ----------
    frame_footer = tb.Frame(frame, padding=(0, 10, 0, 0))
    frame_footer.pack(fill="x")
    lbl_count = tb.Label(frame_footer, text="", font=("Segoe UI", 11, "bold"),
                         bootstyle="danger")
    lbl_count.pack(side="left")

    lbl_leyenda = tb.Label(
        frame_footer,
        text="Amarillo: vencio hace 7 dias o menos   |   Rojo: 8-30 dias   |   Rojo oscuro: mas de 30 dias",
        font=("Segoe UI", 9), foreground="gray")
    lbl_leyenda.pack(side="left", padx=20)

    tb.Button(frame_footer, text="Cerrar", bootstyle="secondary-outline",
              width=12, command=ventana.destroy).pack(side="right")

    # ---------- LOGICA ----------
    datos_caducados = []

    def cargar_datos():
        nonlocal datos_caducados
        try:
            datos_caducados = ver_clientes_caducados_detalle()
        except Exception as e:
            datos_caducados = []
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{e}",
                                 parent=ventana)

    def poblar(event=None):
        for fila in tabla.get_children():
            tabla.delete(fila)

        filtro    = entry_buscar.get().strip().lower()
        sel_mes   = combo_mes.get()
        sel_anio  = combo_anio.get()
        mes_num   = meses.index(sel_mes) if sel_mes != "Todos" else None
        anio      = sel_anio if sel_anio != "Todos" else None

        hoy = datetime.now()
        visibles = 0

        for d in datos_caducados:
            cedula, nombre, telefono, plan, inicio, vence, pagado, pendiente, sus_id = d

            # Filtro de texto: cedula o nombre (parcial, sin distinguir mayusculas)
            if filtro and filtro not in (nombre or "").lower() \
                      and filtro not in (cedula or "").lower():
                continue

            # Filtro por mes/año de vencimiento (formato YYYY-MM-DD)
            v = str(vence or "")
            if anio and not v.startswith(anio):
                continue
            if mes_num and v[5:7] != f"{mes_num:02d}":
                continue

            # Dias transcurridos desde el vencimiento
            try:
                dias = (hoy - datetime.strptime(v, "%Y-%m-%d")).days
            except Exception:
                dias = None

            if dias is None:
                tag = "vencido"; dias_txt = "?"
            elif dias <= 7:
                tag = "reciente"; dias_txt = f"{dias} dias"
            elif dias <= 30:
                tag = "vencido";  dias_txt = f"{dias} dias"
            else:
                tag = "antiguo";  dias_txt = f"{dias} dias"

            # El ID de suscripcion no se muestra: se guarda como iid oculto
            tabla.insert("", "end", iid=f"{sus_id}", values=(
                cedula or "—", nombre, telefono or "—", plan,
                inicio, vence, dias_txt,
                f"${float(pagado):.2f}", f"${max(0.0, float(pendiente)):.2f}"
            ), tags=(tag,))
            visibles += 1

        lbl_count.configure(
            text=f"Mostrando {visibles} de {len(datos_caducados)} clientes caducados")

    def actualizar():
        cargar_datos()
        poblar()

    def limpiar_filtros():
        entry_buscar.delete(0, "end")
        combo_mes.set("Todos")
        combo_anio.set("Todos")
        poblar()

    # Busqueda en vivo y filtros
    entry_buscar.bind("<KeyRelease>", poblar)
    entry_buscar.bind("<Return>", poblar)
    combo_mes.bind("<<ComboboxSelected>>",  poblar)
    combo_anio.bind("<<ComboboxSelected>>", poblar)

    tb.Button(frame_filtros, text="Limpiar", bootstyle="secondary", width=10,
              command=limpiar_filtros).pack(side="left", padx=(0, 6))
    tb.Button(frame_filtros, text="🔄 Actualizar", bootstyle="info", width=13,
              command=actualizar).pack(side="left")

    # Carga inicial
    actualizar()