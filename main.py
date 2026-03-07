from modulos.membresias import crear_membresia, ver_membresias

crear_membresia("Mensual", 30, 30)

planes = ver_membresias()

for plan in planes:
    print(plan)
    