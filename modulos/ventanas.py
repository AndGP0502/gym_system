"""
Utilidades de ventanas multiplataforma.

El sistema se desarrollo originalmente en Windows, donde
ventana.state("zoomed") maximiza la ventana. En macOS y Linux ese
comando puede lanzar TclError ("bad argument zoomed") y la ventana
nunca llega a abrirse. Este helper intenta cada metodo en orden y
siempre deja la ventana maximizada sin romper la app.
"""


def maximizar(ventana):
    """Maximiza una ventana de tkinter/ttkbootstrap/customtkinter
    funcionando en Windows, macOS y Linux."""
    # 1) Windows (y algunas builds de Tk en macOS)
    try:
        ventana.state("zoomed")
        return
    except Exception:
        pass
    # 2) Linux / X11
    try:
        ventana.attributes("-zoomed", True)
        return
    except Exception:
        pass
    # 3) Fallback universal: ocupar toda la pantalla
    try:
        ancho = ventana.winfo_screenwidth()
        alto = ventana.winfo_screenheight()
        ventana.geometry(f"{ancho}x{alto}+0+0")
    except Exception:
        pass