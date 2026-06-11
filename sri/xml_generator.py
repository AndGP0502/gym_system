import uuid
from datetime import datetime
from xml.sax.saxutils import escape


def _clave_acceso(fecha, tipo_comprobante, ruc, ambiente, serie, secuencial, codigo_numerico, tipo_emision):
    fecha_fmt = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d%m%Y")
    clave = f"{fecha_fmt}{tipo_comprobante}{ruc}{ambiente}{serie}{secuencial}{codigo_numerico}{tipo_emision}"
    digito = _modulo11(clave)
    return clave + str(digito)


def _modulo11(clave):
    factores = [2, 3, 4, 5, 6, 7]
    suma = 0
    factor_idx = 0
    for digito in reversed(clave):
        suma += int(digito) * factores[factor_idx % 6]
        factor_idx += 1
    residuo = suma % 11
    if residuo == 0: return 0
    if residuo == 1: return 1
    return 11 - residuo


def _txt(valor):
    if valor is None:
        return ""
    return escape(str(valor).strip())


def generar_xml_factura(config, factura, detalles):
    fecha = factura.get("fecha_emision", datetime.now().strftime("%Y-%m-%d"))
    secuencial = str(factura["secuencial"]).zfill(9)
    serie = config["codigo_establecimiento"] + config["punto_emision"]
    codigo_numerico = str(uuid.uuid4().int)[:8]
    ambiente = config.get("ambiente", 2)
    tipo_emision = config.get("tipo_emision", 1)

    clave_acceso = _clave_acceso(fecha, "01", config["ruc"], ambiente, serie, secuencial, codigo_numerico, tipo_emision)
    fecha_fmt = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")

    subtotal_0  = sum(d["subtotal"] for d in detalles if d["porcentaje_iva"] == 0)
    subtotal_15 = sum(d["subtotal"] for d in detalles if d["porcentaje_iva"] == 15)
    iva_15      = sum(d["iva"]      for d in detalles if d["porcentaje_iva"] == 15)
    descuento   = sum(d["descuento"] * d["cantidad"] for d in detalles)
    total       = subtotal_0 + subtotal_15 + iva_15

    total_impuestos_xml = ""
    if subtotal_0 > 0:
        total_impuestos_xml += f"<totalImpuesto><codigo>2</codigo><codigoPorcentaje>0</codigoPorcentaje><baseImponible>{subtotal_0:.2f}</baseImponible><valor>0.00</valor></totalImpuesto>"
    if subtotal_15 > 0:
        total_impuestos_xml += f"<totalImpuesto><codigo>2</codigo><codigoPorcentaje>5</codigoPorcentaje><baseImponible>{subtotal_15:.2f}</baseImponible><tarifa>15.00</tarifa><valor>{iva_15:.2f}</valor></totalImpuesto>"

    detalles_xml = ""
    for d in detalles:
        cod_iva = "5" if d["porcentaje_iva"] == 15 else "0"
        detalles_xml += (
            f"<detalle>"
            f"<codigoPrincipal>SRV</codigoPrincipal>"
            f"<descripcion>{_txt(d['descripcion'])}</descripcion>"
            f"<cantidad>{d['cantidad']:.2f}</cantidad>"
            f"<precioUnitario>{d['precio_unitario']:.2f}</precioUnitario>"
            f"<descuento>{d['descuento'] * d['cantidad']:.2f}</descuento>"
            f"<precioTotalSinImpuesto>{d['subtotal']:.2f}</precioTotalSinImpuesto>"
            f"<impuestos>"
            f"<impuesto>"
            f"<codigo>2</codigo>"
            f"<codigoPorcentaje>{cod_iva}</codigoPorcentaje>"
            f"<tarifa>{d['porcentaje_iva']:.2f}</tarifa>"
            f"<baseImponible>{d['subtotal']:.2f}</baseImponible>"
            f"<valor>{d['iva']:.2f}</valor>"
            f"</impuesto>"
            f"</impuestos>"
            f"</detalle>"
        )

    xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<factura id="comprobante" version="2.1.0">'
        f'<infoTributaria>'
        f'<ambiente>{ambiente}</ambiente>'
        f'<tipoEmision>{tipo_emision}</tipoEmision>'
        f'<razonSocial>{_txt(config["razon_social"])}</razonSocial>'
        f'<nombreComercial>{_txt(config.get("nombre_comercial") or config["razon_social"])}</nombreComercial>'
        f'<ruc>{config["ruc"]}</ruc>'
        f'<claveAcceso>{clave_acceso}</claveAcceso>'
        f'<codDoc>01</codDoc>'
        f'<estab>{config["codigo_establecimiento"]}</estab>'
        f'<ptoEmi>{config["punto_emision"]}</ptoEmi>'
        f'<secuencial>{secuencial}</secuencial>'
        f'<dirMatriz>{_txt(config.get("direccion_matriz",""))}</dirMatriz>'
        f'</infoTributaria>'
        f'<infoFactura>'
        f'<fechaEmision>{fecha_fmt}</fechaEmision>'
        f'<dirEstablecimiento>{_txt(config.get("direccion_sucursal") or config.get("direccion_matriz","N/A"))}</dirEstablecimiento>'
        f'<obligadoContabilidad>NO</obligadoContabilidad>'
        f'<tipoIdentificacionComprador>{factura.get("tipo_identificacion","05")}</tipoIdentificacionComprador>'
        f'<razonSocialComprador>{_txt(factura["razon_social"])}</razonSocialComprador>'
        f'<identificacionComprador>{factura["identificacion"]}</identificacionComprador>'
        f'<direccionComprador>{_txt(factura.get("direccion","N/A"))}</direccionComprador>'
        f'<totalSinImpuestos>{subtotal_0 + subtotal_15:.2f}</totalSinImpuestos>'
        f'<totalDescuento>{descuento:.2f}</totalDescuento>'
        f'<totalConImpuestos>{total_impuestos_xml}</totalConImpuestos>'
        f'<propina>0.00</propina>'
        f'<importeTotal>{total:.2f}</importeTotal>'
        f'<moneda>DOLAR</moneda>'
        f'<pagos><pago><formaPago>01</formaPago><total>{total:.2f}</total><plazo>0</plazo><unidadTiempo>dias</unidadTiempo></pago></pagos>'
        f'</infoFactura>'
        f'<detalles>{detalles_xml}</detalles>'
        f'<infoAdicional>'
        f'<campoAdicional nombre="Telefono">{_txt(factura.get("telefono","N/A"))}</campoAdicional>'
        f'<campoAdicional nombre="Email">{_txt(factura.get("correo","N/A"))}</campoAdicional>'
        f'</infoAdicional>'
        f'</factura>'
    )

    return xml, clave_acceso, secuencial