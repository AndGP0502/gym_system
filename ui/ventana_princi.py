import ttkbootstrap as ttk
import webbrowser
from ttkbootstrap.constants import *

from ui.clientes_ui import abrir_ventana_clientes
from ui.pagos_ui import abrir_ventana_pagos
from ui.suscripciones_ui import abrir_ventana_suscripciones
from ui.membresias_ui import abrir_ventana_membresias

from modulos.clientes import contar_clientes
from modulos.membresias import contar_membresias
from modulos.suscripciones import contar_suscripciones_vencidas, contar_clientes_activos
from modulos.backup_db import crear_backup, restaurar_backup
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
    # main_ui.py está en gym_system/ui/, assets/ está en gym_system/
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
        """Popup pequeño no invasivo con datos de los creadores."""
        popup = ttk.Toplevel(ventana)
        popup.title("Acerca de")
        popup.geometry("340x280")
        popup.resizable(False, False)

        # Centrar el popup relativo a la ventana principal
        ventana.update_idletasks()
        x = ventana.winfo_x() + (ventana.winfo_width()  // 2) - 170
        y = ventana.winfo_y() + (ventana.winfo_height() // 2) - 140
        popup.geometry(f"+{x}+{y}")

        popup.attributes("-topmost", True)
        popup.after(200, lambda: popup.attributes("-topmost", False))
        popup.lift()
        popup.focus_force()

        # --- Cabecera fija (título + separador, fuera del scroll) ---
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

        # --- Zona con barra de scroll (solo arrastre, sin rueda del mouse) ---
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

        # ── Aquí van tus datos ────────────────────────────────────────────
        # Cada entrada: (nombre, correo, teléfono, red_social, url)
        # Si no tienes red social en alguno, pon ("", "")
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
        # ─────────────────────────────────────────────────────────────────

        def _abrir_link(url):
            # Intenta abrir con Chrome; si no está instalado usa el navegador predeterminado
            rutas_chrome = [
                "C:/Program Files/Google/Chrome/Application/chrome.exe %s",          # Windows 64-bit
                "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s",    # Windows 32-bit
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
                webbrowser.open_new_tab(url)  # Fallback al navegador predeterminado

        for nombre, correo, telefono, red_label, red_url in contactos:
            ttk.Label(inner, text=nombre,
                      font=("Segoe UI", 11, "bold")).pack(anchor="w")
            ttk.Label(inner, text=f"  ✉  {correo}",
                      font=("Segoe UI", 10), foreground="gray").pack(anchor="w")
            ttk.Label(inner, text=f"  📞 {telefono}",
                      font=("Segoe UI", 10), foreground="gray").pack(anchor="w")

            if red_label and red_url:
                # Label que actúa como hipervínculo
                lbl_link = ttk.Label(
                    inner,
                    text=f"  🔗 {red_label}",
                    font=("Segoe UI", 10, "underline"),
                    foreground="#4DA6FF",   # azul clickeable
                    cursor="hand2"          # cursor de manito
                )
                lbl_link.pack(anchor="w", pady=(0, 10))
                # Captura url en el closure con argumento por defecto
                lbl_link.bind("<Button-1>", lambda e, u=red_url: _abrir_link(u))
            else:
                ttk.Label(inner, text="").pack(pady=(0, 4))

        # --- Botón cerrar fijo abajo ---
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

    def actualizar_dashboard():
        numero_clientes.config(text=str(contar_clientes()))
        numero_membresias.config(text=str(contar_membresias()))
        numero_vencidas.config(text=str(contar_suscripciones_vencidas()))
        numero_activos.config(text=str(contar_clientes_activos()))

        for widget in frame_grafica.winfo_children():
            widget.destroy()

        grafica_clientes(frame_grafica)

    def hacer_backup():
        try:
            ruta = crear_backup()
            messagebox.showinfo("Backup creado", f"Backup guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el backup:\n{e}")

    def hacer_restauracion():
        try:
            archivo = restaurar_backup()
            if archivo:
                messagebox.showinfo(
                    "Backup restaurado",
                    "Base restaurada correctamente.\nReinicia el sistema."
                )
                ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo restaurar:\n{e}")

    # ---------------- LAYOUT PRINCIPAL ----------------

    contenedor = ttk.Frame(ventana)
    contenedor.pack(fill="both", expand=True)
    contenedor.columnconfigure(1, weight=1)
    contenedor.rowconfigure(0, weight=1)

    # ---------------- SIDEBAR ----------------

    sidebar = ttk.Frame(contenedor, padding=30)
    sidebar.grid(row=0, column=0, sticky="ns")

    # FIX: se agrega cursor="hand2" y bind a mostrar_contacto
    lbl_titulo = ttk.Label(
        sidebar,
        text="Software de Control A&D",
        font=("Segoe UI", 16, "bold"),
        cursor="hand2"          # ← el cursor cambia a manito al pasar encima
    )
    lbl_titulo.pack(pady=(0, 25))
    lbl_titulo.bind("<Button-1>", mostrar_contacto)   # ← abre el popup al hacer click

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

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar, text="💾 Crear Backup", bootstyle="success",
        command=hacer_backup, **boton_style
    ).pack(pady=6)

    ttk.Button(
        sidebar, text="♻ Restaurar Backup", bootstyle="warning",
        command=hacer_restauracion, **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar, text="📥 Importar Excel", bootstyle="info",
        command=lambda: abrir_ventana_importar(ventana), **boton_style
    ).pack(pady=6)

    ttk.Separator(sidebar).pack(fill="x", pady=20)

    ttk.Button(
        sidebar, text="❌ Salir",
        command=ventana.destroy, **boton_style
    ).pack(pady=6)

    # Logo del gym (clickeable para cambiar)
    label_logo = ttk.Label(sidebar, cursor="hand2")
    label_logo.pack(pady=(30, 4))

    lbl_ayuda_logo = ttk.Label(
        sidebar,
        text="Clic para cambiar el logo",
        font=("Segoe UI", 8),
        foreground="gray",
        cursor="hand2"
    )
    lbl_ayuda_logo.pack(pady=(0, 10))

    def cargar_logo():
        ruta = ruta_assets_lectura("logo_gym.jpg")

        # Si no existe el .jpg, intenta convertir el .ico automáticamente
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
            label_logo.configure(text="Sin logo - clic para agregar",
                                 font=("Segoe UI", 10), foreground="gray")

    def cambiar_logo(event=None):
        from tkinter import filedialog
        ruta_nueva = filedialog.askopenfilename(
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

    # ---------------- ÁREA PRINCIPAL CON SCROLL ----------------

    contenedor_scroll = ttk.Frame(contenedor)
    contenedor_scroll.grid(row=0, column=1, sticky="nsew")
    contenedor_scroll.rowconfigure(0, weight=1)
    contenedor_scroll.columnconfigure(0, weight=1)

    canvas = ttk.Canvas(contenedor_scroll)
    canvas.grid(row=0, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    area = ttk.Frame(canvas, padding=(40, 30))
    canvas_window = canvas.create_window((0, 0), window=area, anchor="nw")

    def actualizar_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def ajustar_ancho_area(event):
        canvas.itemconfig(canvas_window, width=event.width)

    area.bind("<Configure>", actualizar_scroll)
    canvas.bind("<Configure>", ajustar_ancho_area)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

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

    # ---- Logo del gimnasio (clickeable para cambiar foto) ----
    from tkinter import filedialog

    frame_gym = ttk.Frame(contenido_inferior, padding=20)
    frame_gym.grid(row=0, column=0, sticky="n", padx=(0, 10), pady=10)

    ttk.Label(frame_gym, text="Nuestro Gimnasio",
              font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

    label_gym = ttk.Label(frame_gym, cursor="hand2")
    label_gym.pack()

    lbl_ayuda = ttk.Label(
        frame_gym,
        text="📷 Clic para cambiar la foto",
        font=("Segoe UI", 9),
        foreground="gray",
        cursor="hand2"
    )
    lbl_ayuda.pack(pady=(6, 0))

    def cargar_imagen_gym():
        ruta = ruta_assets_lectura("gym.jpg")
        if os.path.exists(ruta):
            img = ImageTk.PhotoImage(Image.open(ruta).resize((450, 260), Image.LANCZOS))
            label_gym.configure(image=img, text="")
            label_gym.image = img
        else:
            label_gym.configure(text="Sin foto  —  clic para agregar",
                                font=("Segoe UI", 11), foreground="gray")

    def cambiar_foto_gimnasio(event=None):
        ruta_nueva = filedialog.askopenfilename(
            title="Selecciona la foto del gimnasio",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.bmp *.webp"),
                       ("Todos los archivos", "*.*")]
        )
        if not ruta_nueva:
            return
        try:
            destino = ruta_assets("gym.jpg")
            Image.open(ruta_nueva).convert("RGB").save(destino, "JPEG", quality=95)
            cargar_imagen_gym()
            messagebox.showinfo("Foto actualizada", "La foto del gimnasio se actualizo correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")

    label_gym.bind("<Button-1>", cambiar_foto_gimnasio)
    lbl_ayuda.bind("<Button-1>", cambiar_foto_gimnasio)

    cargar_imagen_gym()

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

    # ---------------- LOOP ----------------
    ventana.mainloop()