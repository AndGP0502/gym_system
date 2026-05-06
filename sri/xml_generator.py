import hashlib
import uuid
from datetime import datetime


def _clave_acceso(fecha: str, tipo_comprobante: str, ruc: str,
                  ambiente: int, serie: str, secuencial: str,
                  codigo_numerico: str, tipo_emision: int) -> str:
    """Genera la clave de acceso de 49 dígitos según el SRI."""
    fecha_fmt = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d%m%Y")
    clave = (
        f"{fecha_fmt}"
        f"{tipo_comprobante}"
        f"{ruc}"
        f"{ambiente}"
        f"{serie}"        # establecimiento + punto emision
        f"{secuencial}"
        f"{codigo_numerico}"
        f"{tipo_emision}"
    )
    # Módulo 11
    digito = _modulo11(clave)
    return clave + str(digito)


def _modulo11(clave: str) -> int:
    factores = [2, 3, 4, 5, 6, 7]
    suma = 0
    factor_idx = 0
    for digito in reversed(clave):
        suma += int(digito) * factores[factor_idx % 6]
        factor_idx += 1
    residuo = suma % 11
    if residuo == 0:
        return 0
    if residuo == 1:
        return 1
    return 11 - residuo


def generar_xml_factura(config: dict, factura: dict, detalles: list) -> str:
    """
    Genera el XML de factura según el esquema del SRI Ecuador versión 1.1.0.
    config: datos del emisor y configuración SRI
    factura: datos del receptor y totales
    detalles: lista de items de la factura
    """
    fecha = factura.get("fecha_emision", datetime.now().strftime("%Y-%m-%d"))
    secuencial = str(factura["secuencial"]).zfill(9)
    serie = config["codigo_establecimiento"] + config["punto_emision"]
    codigo_numerico = str(uuid.uuid4().int)[:8]
    ambiente = config.get("ambiente", 2)
    tipo_emision = config.get("tipo_emision", 1)

    clave_acceso = _clave_acceso(
        fecha, "01", config["ruc"], ambiente,
        serie, secuencial, codigo_numerico, tipo_emision
    )

    fecha_fmt = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")

    # Calcular totales
    subtotal_0   = sum(d["subtotal"] for d in detalles if d["porcentaje_iva"] == 0)
    subtotal_15  = sum(d["subtotal"] for d in detalles if d["porcentaje_iva"] == 15)
    iva_15       = sum(d["iva"]      for d in detalles if d["porcentaje_iva"] == 15)
    descuento    = sum(d["descuento"] * d["cantidad"] for d in detalles)
    total        = subtotal_0 + subtotal_15 + iva_15

    # Detalles XML
    detalles_xml = ""
    for d in detalles:
        detalles_xml += f"""
            <detalle>
                <codigoPrincipal>SRV</codigoPrincipal>
                <descripcion>{d['descripcion']}</descripcion>
                <cantidad>{d['cantidad']:.2f}</cantidad>
                <precioUnitario>{d['precio_unitario']:.2f}</precioUnitario>
                <descuento>{d['descuento'] * d['cantidad']:.2f}</descuento>
                <precioTotalSinImpuesto>{d['subtotal']:.2f}</precioTotalSinImpuesto>
                <impuestos>
                    <impuesto>
                        <codigo>2</codigo>
                        <codigoPorcentaje>{'4' if d['porcentaje_iva'] == 15 else '0'}</codigoPorcentaje>
                        <tarifa>{d['porcentaje_iva']:.2f}</tarifa>
                        <baseImponible>{d['subtotal']:.2f}</baseImponible>
                        <valor>{d['iva']:.2f}</valor>
                    </impuesto>
                </impuestos>
            </detalle>"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<factura id="comprobante" version="1.1.0">
    <infoTributaria>
        <ambiente>{ambiente}</ambiente>
        <tipoEmision>{tipo_emision}</tipoEmision>
        <razonSocial>{config['razon_social']}</razonSocial>
        <nombreComercial>{config.get('nombre_comercial', config['razon_social'])}</nombreComercial>
        <ruc>{config['ruc']}</ruc>
        <claveAcceso>{clave_acceso}</claveAcceso>
        <codDoc>01</codDoc>
        <estab>{config['codigo_establecimiento']}</estab>
        <ptoEmi>{config['punto_emision']}</ptoEmi>
        <secuencial>{secuencial}</secuencial>
        <dirMatriz>{config.get('direccion_matriz', '')}</dirMatriz>
    </infoTributaria>
    <infoFactura>
        <fechaEmision>{fecha_fmt}</fechaEmision>
        <dirEstablecimiento>{config.get('direccion_sucursal', config.get('direccion_matriz', ''))}</dirEstablecimiento>
        <tipoIdentificacionComprador>{factura.get('tipo_identificacion', '05')}</tipoIdentificacionComprador>
        <razonSocialComprador>{factura['razon_social']}</razonSocialComprador>
        <identificacionComprador>{factura['identificacion']}</identificacionComprador>
        <direccionComprador>{factura.get('direccion', 'N/A')}</direccionComprador>
        <totalSinImpuestos>{subtotal_0 + subtotal_15:.2f}</totalSinImpuestos>
        <totalDescuento>{descuento:.2f}</totalDescuento>
        <totalConImpuestos>
            <totalImpuesto>
                <codigo>2</codigo>
                <codigoPorcentaje>0</codigoPorcentaje>
                <baseImponible>{subtotal_0:.2f}</baseImponible>
                <valor>0.00</valor>
            </totalImpuesto>
            <totalImpuesto>
                <codigo>2</codigo>
                <codigoPorcentaje>4</codigoPorcentaje>
                <baseImponible>{subtotal_15:.2f}</baseImponible>
                <valor>{iva_15:.2f}</valor>
            </totalImpuesto>
        </totalConImpuestos>
        <propina>0.00</propina>
        <importeTotal>{total:.2f}</importeTotal>
        <moneda>DOLAR</moneda>
        <pagos>
            <pago>
                <formaPago>01</formaPago>
                <total>{total:.2f}</total>
                <plazo>0</plazo>
                <unidadTiempo>dias</unidadTiempo>
            </pago>
        </pagos>
    </infoFactura>
    <detalles>{detalles_xml}
    </detalles>
    <infoAdicional>
        <campoAdicional nombre="Telefono">{factura.get('telefono', '')}</campoAdicional>
        <campoAdicional nombre="Email">{factura.get('correo', '')}</campoAdicional>
    </infoAdicional>
</factura>"""

    return xml, clave_acceso, secuencial