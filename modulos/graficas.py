import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from modulos.suscripciones import contar_clientes_activos, contar_suscripciones_vencidas


def grafica_clientes(frame):

    activos = contar_clientes_activos()
    vencidos = contar_suscripciones_vencidas()

    total = activos + vencidos

    # evitar error si no hay datos
    if total == 0:
        activos = 1
        vencidos = 1
        etiquetas = ["Sin datos", "Sin datos"]
    else:
        etiquetas = ["Activos", "Vencidos"]

    datos = [activos, vencidos]

    fig, ax = plt.subplots(figsize=(3,2))

    ax.pie(
        datos,
        labels=etiquetas,
        autopct="%1.0f%%",
        startangle=90
    )

    ax.set_title("Estado de Clientes")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()