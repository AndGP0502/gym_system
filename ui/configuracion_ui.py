import os
import sys
import json
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

# ── Rutas ────────────────────────────────────────────────────────────────────

if getattr(sys, 'frozen', False):
    _RAIZ = os.path.dirname(sys.executable)
else:
    _RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.path.join(_RAIZ, "Config.JSON")


from modulos.rutas import get_config_path, get_assets_dir
import os, sys, json
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

CONFIG_PATH = get_config_path()

def ruta_assets(nombre_archivo):
    base = get_assets_dir()
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, nombre_archivo)

def ruta_assets_lectura(nombre_archivo):
    return os.path.join(get_assets_dir(), nombre_archivo)



# ── Leer / guardar Config.JSON ────────────────────────────────────────────────

def leer_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_config(datos: dict):
    config = leer_config()
    config.update(datos)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


# ── Ventana principal ─────────────────────────────────────────────────────────

def abrir_ventana_configuracion(parent):
    popup = ttk.Toplevel(parent)
    popup.title("Configuración del Gimnasio")
    popup.geometry("520x800")
    popup.resizable(False, False)

    # Centrar
    parent.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width()  // 2) - 260
    y = parent.winfo_y() + (parent.winfo_height() // 2) - 310
    popup.geometry(f"+{x}+{y}")
    popup.lift()
    popup.focus_force()

    config_actual = leer_config()

    # ── Frame principal ───────────────────────────────────────────────────────
    frame = ttk.Frame(popup, padding=30)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="⚙ Configuración del Gimnasio",
              font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 4))
    ttk.Label(frame, text="Esta información aparecerá en todos los PDFs generados.",
              font=("Segoe UI", 10), foreground="gray").pack(anchor="w", pady=(0, 20))

    ttk.Separator(frame).pack(fill="x", pady=(0, 20))

    # ── Campos de texto ───────────────────────────────────────────────────────
    campos = [
        ("🏋️  Nombre del gimnasio", "nombre_gimnasio"),
        ("📞  Teléfono",             "telefono"),
        ("📍  Dirección",            "direccion"),
        ("✉️   Correo",              "correo"),
    ]

    entradas = {}

    for label_text, clave in campos:
        ttk.Label(frame, text=label_text,
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 4))
        entrada = ttk.Entry(frame, font=("Segoe UI", 11), width=48)
        entrada.insert(0, config_actual.get(clave, ""))
        entrada.pack(anchor="w", pady=(0, 14))
        entradas[clave] = entrada

    ttk.Separator(frame).pack(fill="x", pady=(0, 20))

    # ── Sección logo ──────────────────────────────────────────────────────────
    ttk.Label(frame, text="🖼️  Logo del gimnasio",
              font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

    frame_logo = ttk.Frame(frame)
    frame_logo.pack(anchor="w", pady=(0, 20))

    label_preview = ttk.Label(frame_logo, text="Sin logo", width=12,
                               font=("Segoe UI", 9), foreground="gray",
                               cursor="hand2")
    label_preview.grid(row=0, column=0, rowspan=2, padx=(0, 20))

    def cargar_preview():
        ruta = ruta_assets_lectura("logo_gym.jpg")
        if os.path.exists(ruta):
            img = Image.open(ruta).resize((80, 80))
            foto = ImageTk.PhotoImage(img)
            label_preview.configure(image=foto, text="")
            label_preview.image = foto
        else:
            label_preview.configure(image="", text="Sin logo")

    def cambiar_logo(event=None):
        ruta_nueva = filedialog.askopenfilename(
            parent=popup,
            title="Selecciona el logo del gimnasio",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp"),
                       ("Todos los archivos", "*.*")]
        )
        if not ruta_nueva:
            return
        try:
            destino = ruta_assets("logo_gym.jpg")
            Image.open(ruta_nueva).convert("RGB").save(destino, "JPEG", quality=95)
            cargar_preview()
            messagebox.showinfo("Logo actualizado", "Logo actualizado correctamente.", parent=popup)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}", parent=popup)

    label_preview.bind("<Button-1>", cambiar_logo)
    cargar_preview()

    ttk.Button(frame_logo, text="📂 Cambiar logo", bootstyle="info-outline",
               command=cambiar_logo).grid(row=0, column=1, sticky="w")
    ttk.Label(frame_logo, text="Click en la imagen o en el botón para cambiar",
              font=("Segoe UI", 9), foreground="gray").grid(row=1, column=1, sticky="w")

    # ── Botones ───────────────────────────────────────────────────────────────
    ttk.Separator(frame).pack(fill="x", pady=(0, 20))

    frame_botones = ttk.Frame(frame)
    frame_botones.pack(fill="x")

    def guardar():
        datos = {clave: entradas[clave].get().strip() for _, clave in campos}
        guardar_config(datos)
        messagebox.showinfo("Guardado", "Configuración guardada correctamente.", parent=popup)
        popup.destroy()

    ttk.Button(frame_botones, text="💾 Guardar", bootstyle="success",
               width=16, command=guardar).pack(side="left")
    ttk.Button(frame_botones, text="Cancelar", bootstyle="secondary-outline",
               width=14, command=popup.destroy).pack(side="right")