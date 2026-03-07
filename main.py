from modulos.clientes import agregar_cliente, ver_clientes
from modulos.membresias import crear_membresia, ver_membresias
from modulos.suscripciones import asignar_membresia, ver_suscripciones


# --------- AGREGAR CLIENTE ---------

print(agregar_cliente("Juan Perez", "0999999999", "2026-03-07"))


# --------- CREAR MEMBRESIA ---------

crear_membresia("Mensual", 30, 30)


# --------- VER CLIENTES ---------

print("\nCLIENTES:")
clientes = ver_clientes()

for cliente in clientes:
    print(cliente)


# --------- VER MEMBRESIAS ---------

print("\nMEMBRESIAS:")
membresias = ver_membresias()

for m in membresias:
    print(m)


# --------- ASIGNAR MEMBRESIA A CLIENTE ---------

# cliente_id = 1
# membresia_id = 1
# precio_total = 30
# pagado = 25

asignar_membresia(1, 1, 30, 25)


# --------- VER SUSCRIPCIONES ---------

print("\nSUSCRIPCIONES:")

suscripciones = ver_suscripciones()

for s in suscripciones:
    print(s)