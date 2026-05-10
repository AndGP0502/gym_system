from sri.sri_client import enviar_comprobante, consultar_autorizacion

# Leer XML firmado
with open("factura_firmada.xml", "r", encoding="utf-8") as f:
    xml_firmado = f.read()

# Clave de acceso
clave_acceso = "0905202601171451896400110010010000000011657851311"

# Ambiente pruebas
ambiente = 1

print("===================================")
print("ENVIANDO COMPROBANTE AL SRI")
print("===================================")

respuesta = enviar_comprobante(xml_firmado, ambiente)

print("\nRESPUESTA RECEPCIÓN:")
print(respuesta)

if respuesta["ok"]:
    print("\nComprobante recibido por el SRI.")
    print("Consultando autorización...")

    autorizacion = consultar_autorizacion(
        clave_acceso,
        ambiente
    )

    print("\nRESPUESTA AUTORIZACIÓN:")
    print(autorizacion)

else:
    print("\nEl SRI devolvió el comprobante.")