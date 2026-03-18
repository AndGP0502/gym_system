import ttkbootstrap as ttk
import webbrowser
from ttkbootstrap.constants import *

from ui.clientes_ui import abrir_ventana_clientes
from ui.configuracion_ui import abrir_ventana_configuracion
from ui.pagos_ui import abrir_ventana_pagos
from ui.suscripciones_ui import abrir_ventana_suscripciones
from ui.membresias_ui import abrir_ventana_membresias

from modulos.clientes import contar_clientes, contar_clientes_filtro
from modulos.membresias import contar_membresias
from modulos.suscripciones import contar_suscripciones_vencidas, contar_clientes_activos, ver_clientes_activos_detalle, contar_suscripciones_vencidas_filtro, contar_clientes_activos_filtro
from modulos.backup_db import crear_backup, exportar_backup_excel, importar_desde_excel
from modulos.graficas import grafica_clientes
from ui.importar_excel import abrir_ventana_importar
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

# Raíz del proyecto: funciona tanto corriendo main.py como como .exe
if getattr(sys, 'frozen', False):
    _RAIZ = os.path.dirname(sys.executable)
else:
    _RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ruta_assets(nombre_archivo):
    """Ruta ESCRIBIBLE — AppData cuando es .exe, assets/ local en desarrollo."""
    if getattr(sys, 'frozen', False):
        base = os.path.join(os.environ.get("APPDATA", ""), "GymSystem", "assets")
    else:
        base = os.path.join(_RAIZ, "assets")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, nombre_archivo)

def ruta_assets_lectura(nombre_archivo):
    """Ruta de LECTURA — busca primero en AppData, luego en assets/ empaquetado."""
    personalizada = ruta_assets(nombre_archivo)
    if os.path.exists(personalizada):
        return personalizada
    if getattr(sys, 'frozen', False):
        base = os.path.join(sys._MEIPASS, "assets")
    else:
        base = os.path.join(_RAIZ, "assets")
    return os.path.join(base, nombre_archivo)


def iniciar_ventana():

    ventana = ttk.Window(themename="darkly")
    ventana.title("Sistema de Gestión de Gimnasio")
    ventana.state("zoomed")

    # ---------------- POPUP DE CONTACTO ----------------

    def mostrar_contacto(event=None):
        popup = ttk.Toplevel(ventana)
        popup.title("Acerca de")
        popup.geometry("340x280")
        popup.resizable(False, False)

        ventana.update_idletasks()
        x = ventana.winfo_x() + (ventana.winfo_width()  // 2) - 170
        y = ventana.winfo_y() + (ventana.winfo_height() // 2) - 140
        popup.geometry(f"+{x}+{y}")

        popup.attributes("-topmost", True)
        popup.after(200, lambda: popup.attributes("-topmost", False))
        popup.lift()
        popup.focus_force()

        frame_header = ttk.Frame(popup, padding=(20, 16, 20, 0))
        frame_header.pack(fill="x")

        ttk.Label(
            frame_header,
            text="Software de Control A&D",
            font=("Segoe UI", 14, "bold"),
            bootstyle="info"
        ).pack()

        ttk.Label(
            frame_header,
            text="Desarrollado por:",
            font=("Segoe UI", 10),
            foreground="gray"
        ).pack(pady=(2, 8))

        ttk.Separator(frame_header).pack(fill="x")

        scroll_frame = ttk.Frame(popup)
        scroll_frame.pack(fill="both", expand=True)

        sb = ttk.Scrollbar(scroll_frame, orient="vertical")
        sb.pack(side="right", fill="y")

        canvas_popup = ttk.Canvas(scroll_frame, highlightthickness=0, height=150,
                                  yscrollcommand=sb.set)
        canvas_popup.pack(side="left", fill="both", expand=True)
        sb.configure(command=canvas_popup.yview)

        inner = ttk.Frame(canvas_popup, padding=(20, 10, 20, 10))
        win_id = canvas_popup.create_window((0, 0), window=inner, anchor="nw")

        def _ajustar(event):
            canvas_popup.configure(scrollregion=canvas_popup.bbox("all"))
            canvas_popup.itemconfig(win_id, width=canvas_popup.winfo_width())

        inner.bind("<Configure>", _ajustar)

        contactos = [
            (
                "👤 André Garzón",
                "",
                "+593 983760090",
                "Facebook",
                "https://www.facebook.com/",
            ),
            (
                "👤 Dennys Chanchicocha",
                "",
                "+593 980844726",
                "Facebook",
                "https://www.facebook.com/share/186cb5uQdG/",
            ),
        ]

        def _abrir_link(url):
            rutas_chrome = [
                "C:/Program Files/Google/Chrome/Application/chrome.exe %s",
                "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s",
            ]
            abierto = False
            for ruta in rutas_chrome:
                try:
                    webbrowser.get(ruta).open_new_tab(url)
                    abierto = True
                    break
                except webbrowser.Error:
                    continue
            if not abierto:
                webbrowser.open_new_tab(url)

        for nombre, correo, telefono, red_label, red_url in contactos:
            ttk.Label(inner, text=nombre,
                      font=("Segoe UI", 11, "bold")).pack(anchor="w")
            ttk.Label(inner, text=f"  ✉  {correo}",
                      font=("Segoe UI", 10), foreground="gray").pack(anchor="w")
            ttk.Label(inner, text=f"  📞 {telefono}",
                      font=("Segoe UI", 10), foreground="gray").pack(anchor="w")

            if red_label and red_url:
                lbl_link = ttk.Label(
                    inner,
                    text=f"  🔗 {red_label}",
                    font=("Segoe UI", 10, "underline"),
                    foreground="#4DA6FF",
                    cursor="hand2"
                )
                lbl_link.pack(anchor="w", pady=(0, 10))
                lbl_link.bind("<Button-1>", lambda e, u=red_url: _abrir_link(u))
            else:
                ttk.Label(inner, text="").pack(pady=(0, 4))

        frame_footer = ttk.Frame(popup, padding=(20, 8, 20, 14))
        frame_footer.pack(fill="x")

        ttk.Separator(frame_footer).pack(fill="x", pady=(0, 10))

        ttk.Button(
            frame_footer,
            text="Cerrar",
            bootstyle="secondary-outline",
            width=12,
            command=popup.destroy
        ).pack()

    # ---------------- FUNCIONES ----------------

    def actualizar_dashboard(event=None):
        try:
            sel_mes  = combo_mes_dash.get()
            sel_anio = combo_anio_dash.get()
            mes_num  = meses_dash.index(sel_mes)  if sel_mes  != "Todos" else None
            anio     = int(sel_anio)              if sel_anio != "Todos" else None
        except Exception:
            mes_num = None
            anio    = None
            sel_mes = sel_anio = "Todos"

        numero_clientes.config(text=str(
            contar_clientes_filtro(mes_num, anio) if (mes_num or anio) else contar_clientes()
        ))
        numero_membresias.config(text=str(contar_membresias()))
        numero_vencidas.config(text=str(
            contar_suscripciones_vencidas_filtro(mes_num, anio) if (mes_num or anio) else contar_suscripciones_vencidas()
        ))
        numero_activos.config(text=str(
            contar_clientes_activos_filtro(mes_num, anio) if (mes_num or anio) else contar_clientes_activos()
        ))

        try:
            filtro = []
            if mes_num: filtro.append(meses_dash[mes_num])
            if anio:    filtro.append(str(anio))
            lbl_filtro_info.configure(
                text=f"Filtrando: {' / '.join(filtro)}" if filtro else "Mostrando todos los periodos"
            )
        except Exception:
            pass

        for widget in frame_grafica.winfo_children():
            widget.destroy()

        grafica_clientes(frame_grafica)

    def hacer_backup():
        """Crea backup binario .db clásico."""
        try:
            ruta = crear_backup()
            messagebox.showinfo("Backup creado", f"Backup guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el backup:\n{e}")

    def hacer_backup_excel():
        """Exporta todos los datos a un archivo Excel organizado por hojas."""
        try:
            ruta = exportar_backup_excel()
            if not ruta:
                return  # El usuario canceló el diálogo
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el backup Excel:\n{e}")

    def hacer_restauracion_excel():
        """Restaura la BD desde un archivo Excel generado previamente."""
        try:
            ok = importar_desde_excel()
            if ok:
                ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo restaurar desde Excel:\n{e}")

    # ---------------- LAYOUT PRINCIPAL ----------------

    import tkinter as tk_raw

    root_frame = ttk.Frame(ventana)
    root_frame.pack(fill="both", expand=True)
    root_frame.columnconfigure(0, weight=1)
    root_frame.rowconfigure(0, weight=1)

    main_canvas = tk_raw.Canvas(root_frame, highlightthickness=0)
    main_canvas.grid(row=0, column=0, sticky="nsew")

    global_sb = ttk.Scrollbar(root_frame, orient="vertical", command=main_canvas.yview)
    global_sb.grid(row=0, column=1, sticky="ns")
    main_canvas.configure(yscrollcommand=global_sb.set)

    contenedor = ttk.Frame(main_canvas)
    main_canvas.create_window((0, 0), window=contenedor, anchor="nw", tags="contenedor")

    def _ajustar_main(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    def _ajustar_ancho_main(event):
        main_canvas.itemconfig("contenedor", width=event.width)

    contenedor.bind("<Configure>", _ajustar_main)
    main_canvas.bind("<Configure>", _ajustar_ancho_main)

    def _on_mousewheel(event):
        main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    contenedor.columnconfigure(1, weight=1)
    contenedor.rowconfigure(0, weight=1)

    # ---------------- SIDEBAR ----------------

    sidebar = ttk.Frame(contenedor, padding=30)
    sidebar.grid(row=0, column=0, sticky="ns")

    lbl_titulo = ttk.Label(
        sidebar,
        text="Software de Control A&D",
        font=("Segoe UI", 16, "bold"),
        cursor="hand2"
    )
    lbl_titulo.pack(pady=(0, 25))
    lbl_titulo.bind("<Button-1>", mostrar_contacto)

    boton_style = {"width": 22, "padding": 10}

    ttk.Button(
        sidebar, text="👥 Clientes", bootstyle="primary-outline",
        command=lambda: abrir_ventana_clientes(ventana), **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="🏷 Membresías", bootstyle="primary-outline",
        command=lambda: abrir_ventana_membresias(ventana), **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="📋 Suscripciones", bootstyle="primary-outline",
        command=lambda: abrir_ventana_suscripciones(ventana), **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="💳 Pagos", bootstyle="primary-outline",
        command=lambda: abrir_ventana_pagos(ventana), **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="🟢 Clientes Activos", bootstyle="success-outline",
        command=lambda: abrir_ventana_activos(ventana), **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar, text="💾 Crear Backup (.db)", bootstyle="success",
        command=hacer_backup, **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="📊 Exportar Backup Excel", bootstyle="success-outline",
        command=hacer_backup_excel, **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="♻ Restaurar desde Excel", bootstyle="warning",
        command=hacer_restauracion_excel, **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar, text="📥 Importar Excel", bootstyle="info",
        command=lambda: abrir_ventana_importar(ventana), **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar, text="⚙ Configuración", bootstyle="secondary-outline",
        command=lambda: abrir_ventana_configuracion(ventana), **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="❌ Salir",
        command=ventana.destroy, **boton_style
    ).pack(pady=6)

    # Logo del gym (clickeable para cambiar)
    label_logo = ttk.Label(sidebar, cursor="hand2")
    label_logo.pack(pady=(30, 4))

    lbl_ayuda_logo = ttk.Label(
        sidebar,
        text="Click para cambiar el logo",
        font=("Segoe UI", 8),
        foreground="gray",
        cursor="hand2"
    )
    lbl_ayuda_logo.pack(pady=(0, 10))

    def cargar_logo():
        ruta = ruta_assets_lectura("logo_gym.jpg")

        if not os.path.exists(ruta):
            ruta_ico = ruta_assets_lectura("logo_gym.ico")
            if os.path.exists(ruta_ico):
                try:
                    destino = ruta_assets("logo_gym.jpg")
                    Image.open(ruta_ico).convert("RGB").save(destino, "JPEG", quality=95)
                    ruta = destino
                except Exception:
                    pass

        if os.path.exists(ruta):
            img = ImageTk.PhotoImage(Image.open(ruta).resize((200, 200)))
            label_logo.configure(image=img, text="")
            label_logo.image = img
        else:
            label_logo.configure(text="Sin logo - click para agregar",
                                 font=("Segoe UI", 10), foreground="gray")

    def cambiar_logo(event=None):
        from tkinter import filedialog
        ventana.focus_force()
        ruta_nueva = filedialog.askopenfilename(
            parent=ventana,
            title="Selecciona el logo del gimnasio",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.bmp *.webp"),
                       ("Todos los archivos", "*.*")]
        )
        if not ruta_nueva:
            return
        try:
            destino = ruta_assets("logo_gym.jpg")
            Image.open(ruta_nueva).convert("RGB").save(destino, "JPEG", quality=95)
            cargar_logo()
            messagebox.showinfo("Logo actualizado", "El logo se actualizo correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")

    label_logo.bind("<Button-1>", cambiar_logo)
    lbl_ayuda_logo.bind("<Button-1>", cambiar_logo)

    cargar_logo()

    # ---------------- ÁREA PRINCIPAL ----------------

    area = ttk.Frame(contenedor, padding=(40, 30))
    area.grid(row=0, column=1, sticky="nsew")

    # ---------------- HEADER ----------------

    header = ttk.Frame(area)
    header.pack(fill="x", pady=(0, 20))

    ttk.Label(
        header,
        text="Dashboard del Gimnasio",
        font=("Segoe UI", 28, "bold"),
    ).pack(side="left")

    ttk.Button(
        header, text="🔄 Actualizar",
        bootstyle="info", command=actualizar_dashboard
    ).pack(side="right", padx=5)

    # ---------------- SELECTOR MES/AÑO ----------------

    frame_filtro = ttk.Frame(area)
    frame_filtro.pack(fill="x", pady=(0, 10))

    ttk.Label(frame_filtro, text="Filtrar cards por:",
              font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 10))

    meses_dash = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    combo_mes_dash = ttk.Combobox(frame_filtro, values=meses_dash, width=14, state="readonly")
    combo_mes_dash.set("Todos")
    combo_mes_dash.pack(side="left", padx=(0, 8))

    ttk.Label(frame_filtro, text="Año:",
              font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 6))

    anios_dash = ["Todos"] + [str(a) for a in range(2020, 2101)]
    combo_anio_dash = ttk.Combobox(frame_filtro, values=anios_dash, width=10, state="readonly")
    combo_anio_dash.set("Todos")
    combo_anio_dash.pack(side="left", padx=(0, 8))

    lbl_filtro_info = ttk.Label(frame_filtro, text="Mostrando todos los periodos",
                                font=("Segoe UI", 10), bootstyle="info")
    lbl_filtro_info.pack(side="left", padx=15)

    combo_mes_dash.bind("<<ComboboxSelected>>",  actualizar_dashboard)
    combo_anio_dash.bind("<<ComboboxSelected>>", actualizar_dashboard)

    # ---------------- CARDS ----------------

    fila_cards = ttk.Frame(area)
    fila_cards.pack(fill="x", pady=(0, 30))

    for i in range(4):
        fila_cards.columnconfigure(i, weight=1, uniform="card")

    def crear_card(parent, icono, titulo, valor, col):
        frame = ttk.Frame(parent, padding=25)
        frame.grid(row=0, column=col, padx=12, pady=10, sticky="nsew")

        ttk.Label(frame, text=icono, font=("Segoe UI", 28)).pack(pady=(0, 6))
        ttk.Label(frame, text=titulo, font=("Segoe UI", 11)).pack()
        numero = ttk.Label(
            frame, text=valor,
            font=("Segoe UI", 36, "bold"),
            bootstyle="info"
        )
        numero.pack(pady=(8, 0))
        return frame, numero

    _, numero_clientes   = crear_card(fila_cards, "👥", "Clientes Registrados",   str(contar_clientes()),               0)
    _, numero_membresias = crear_card(fila_cards, "🏷", "Membresías Activas",     str(contar_membresias()),             1)
    _, numero_vencidas   = crear_card(fila_cards, "⚠️",  "Suscripciones Vencidas", str(contar_suscripciones_vencidas()), 2)
    _, numero_activos    = crear_card(fila_cards, "🔥", "Clientes Activos",        str(contar_clientes_activos()),       3)

    # ---------------- CONTENIDO INFERIOR ----------------

    contenido_inferior = ttk.Frame(area)
    contenido_inferior.pack(fill="both", expand=True, pady=10)
    contenido_inferior.columnconfigure(0, weight=1)
    contenido_inferior.columnconfigure(1, weight=1)

    # ---- Actividad reciente ----
    actividad = ttk.Frame(contenido_inferior, padding=30)
    actividad.grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=10)

    ttk.Label(actividad, text="Actividad reciente",
              font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 16))

    for item in [
        "✅ Sistema iniciado",
        "✅ Clientes registrados",
        "✅ Membresías cargadas",
        "✅ Base de datos conectada",
    ]:
        ttk.Label(actividad, text=item, font=("Segoe UI", 11)).pack(anchor="w", pady=5)

    # ---- Gráfica PIE ----
    frame_grafica = ttk.Frame(contenido_inferior, padding=20, bootstyle="secondary")
    frame_grafica.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10, 0), pady=10)

    grafica_clientes(frame_grafica)

    # ---------------- CLIENTES ACTIVOS ----------------

    def abrir_ventana_activos(parent):
        from tkinter import ttk as ttkb
        import ttkbootstrap as ttk2
        from datetime import datetime

        popup = ttk2.Toplevel(parent)
        popup.title("Clientes Activos")
        popup.geometry("900x550")
        popup.resizable(True, True)
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  // 2) - 450
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 275
        popup.geometry(f"+{x}+{y}")
        popup.lift()

        frame = ttk2.Frame(popup, padding=20)
        frame.pack(fill="both", expand=True)

        ttk2.Label(frame, text="Clientes con Suscripción Activa",
                   font=("Segoe UI", 18, "bold"), bootstyle="success").pack(anchor="w", pady=(0, 4))
        ttk2.Label(frame, text="Clientes cuya suscripcion no ha vencido a la fecha de hoy.",
                   font=("Segoe UI", 10), foreground="gray").pack(anchor="w", pady=(0, 14))

        tabla_container = ttk2.Frame(frame)
        tabla_container.pack(fill="both", expand=True)

        columnas = ("ID", "Cliente", "Plan", "Fecha Inicio", "Vence", "Dias Restantes", "Pagado", "Pendiente")
        tabla_act = ttkb.Treeview(tabla_container, columns=columnas, show="headings", height=18)
        for col in columnas:
            tabla_act.heading(col, text=col)
        tabla_act.column("ID",            width=50,  anchor="center")
        tabla_act.column("Cliente",       width=200, anchor="w")
        tabla_act.column("Plan",          width=170, anchor="w")
        tabla_act.column("Fecha Inicio",  width=110, anchor="center")
        tabla_act.column("Vence",         width=110, anchor="center")
        tabla_act.column("Dias Restantes",width=110, anchor="center")
        tabla_act.column("Pagado",        width=90,  anchor="center")
        tabla_act.column("Pendiente",     width=90,  anchor="center")

        tabla_act.tag_configure("ok",      background="#b6f2c6", foreground="#0f5132")
        tabla_act.tag_configure("pronto",  background="#fff3cd", foreground="#664d03")

        sb = ttkb.Scrollbar(tabla_container, orient="vertical", command=tabla_act.yview)
        tabla_act.configure(yscrollcommand=sb.set)
        tabla_act.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        frame_footer = ttk2.Frame(frame, padding=(0, 10, 0, 0))
        frame_footer.pack(fill="x")
        lbl_count = ttk2.Label(frame_footer, text="", font=("Segoe UI", 11, "bold"), bootstyle="success")
        lbl_count.pack(side="left")
        ttk2.Button(frame_footer, text="Cerrar", bootstyle="secondary-outline",
                    width=12, command=popup.destroy).pack(side="right")

        def cargar():
            for fila in tabla_act.get_children():
                tabla_act.delete(fila)
            try:
                datos = ver_clientes_activos_detalle()
            except Exception:
                datos = []
            hoy = datetime.now()
            count = 0
            for row in datos:
                id_s, cliente, plan, inicio, vence, pagado, pendiente = row
                try:
                    dias = (datetime.strptime(vence, "%Y-%m-%d") - hoy).days
                except Exception:
                    dias = "?"
                tag = "pronto" if isinstance(dias, int) and dias <= 7 else "ok"
                tabla_act.insert("", "end", values=(
                    id_s, cliente, plan, inicio, vence,
                    f"{dias} dias" if isinstance(dias, int) else dias,
                    f"${float(pagado):.2f}", f"${float(pendiente):.2f}"
                ), tags=(tag,))
                count += 1
            lbl_count.configure(text=f"Total clientes activos: {count}")

        cargar()

    # ---------------- LOOP ----------------
    ventana.mainloop()