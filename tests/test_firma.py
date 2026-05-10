from sri.xml_generator import generar_xml_factura
from sri.signer import firmar_xml

config = {
    "ruc": "tu_ruc",
    "razon_social": "tu_razonsocial",
    "nombre_comercial": "GYMSYSTEM",
    "codigo_establecimiento": "001",
    "punto_emision": "001",
    "direccion_matriz": "QUITO",
    "direccion_sucursal": "QUITO",
    "ambiente": 1,  # 1 = pruebas | 2 = producción
    "tipo_emision": 1
}

factura = {
    "fecha_emision": "2026-05-09",
    "secuencial": 1,
    "razon_social": "CONSUMIDOR FINAL",
    "identificacion": "9999999999999",
    "tipo_identificacion": "07",
    "direccion": "N/A",
    "telefono": "",
    "correo": ""
}

detalles = [
    {
        "descripcion": "Membresia mensual gimnasio",
        "cantidad": 1,
        "precio_unitario": 25.00,
        "descuento": 0.00,
        "subtotal": 25.00,
        "porcentaje_iva": 15,
        "iva": 3.75
    }
]

# Generar XML
xml, clave, secuencial = generar_xml_factura(
    config,
    factura,
    detalles
)

# Firmar XML
xml_firmado = firmar_xml(
    xml,
    r"C:\RUTA\TU_FIRMA.p12",
    "CLAVE_FIRMA"
)

# Guardar XML firmado
with open("factura_firmada.xml", "w", encoding="utf-8") as f:
    f.write(xml_firmado)

print("===================================")
print("FACTURA FIRMADA GENERADA")
print("===================================")
print("Clave de acceso:", clave)
print("Secuencial:", secuencial)
print("Archivo: factura_firmada.xml")