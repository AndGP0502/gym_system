import sqlite3
import os
import json
from datetime import datetime
from modulos.rutas import get_db_path, get_app_dir

DB_PATH = get_db_path()


def obtener_config_sri() -> dict | None:
    con = sqlite3.connect(DB_PATH)
    cur = con.execute("SELECT * FROM configuracion_sri WHERE id = 1")
    fila = cur.fetchone()
    con.close()
    if not fila:
        return None
    cols = ["id","ruc","razon_social","nombre_comercial","direccion_matriz",
            "direccion_sucursal","codigo_establecimiento","punto_emision",
            "ambiente","tipo_emision","ruta_certificado","clave_certificado",
            "siguiente_secuencial","correo_remitente","smtp_host","smtp_port",
            "smtp_usuario","smtp_clave","ruta_xmls","ruta_rides"]
    return dict(zip(cols, fila))


def guardar_factura(factura: dict, detalles: list) -> int:
    """Guarda factura y detalles en la BD. Devuelve el ID."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO facturas (
            fecha_emision, tipo_identificacion, identificacion,
            razon_social, correo, telefono, direccion,
            subtotal_0, subtotal_15, iva_15, descuento_total,
            total, establecimiento, punto_emision, secuencial,
            cliente_id, observacion, estado, ambiente,
            ruc_emisor, razon_social_emisor
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        factura["fecha_emision"],
        factura.get("tipo_identificacion", "05"),
        factura["identificacion"],
        factura["razon_social"],
        factura.get("correo", ""),
        factura.get("telefono", ""),
        factura.get("direccion", ""),
        factura.get("subtotal_0", 0),
        factura.get("subtotal_15", 0),
        factura.get("iva_15", 0),
        factura.get("descuento_total", 0),
        factura["total"],
        factura.get("establecimiento", "001"),
        factura.get("punto_emision", "001"),
        factura["secuencial"],
        factura.get("cliente_id"),
        factura.get("observacion", ""),
        "BORRADOR",
        factura.get("ambiente", 2),
        factura.get("ruc_emisor", ""),
        factura.get("razon_social_emisor", ""),
    ))
    factura_id = cur.lastrowid

    for d in detalles:
        cur.execute("""
            INSERT INTO factura_detalle (
                factura_id, descripcion, cantidad, precio_unitario,
                descuento, tiene_iva, porcentaje_iva, subtotal, iva, total
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            factura_id, d["descripcion"], d["cantidad"],
            d["precio_unitario"], d["descuento"],
            1 if d["porcentaje_iva"] > 0 else 0,
            d["porcentaje_iva"], d["subtotal"], d["iva"], d["total"]
        ))

    # Incrementar secuencial
    con.execute("""
        UPDATE configuracion_sri
        SET siguiente_secuencial = siguiente_secuencial + 1
        WHERE id = 1
    """)
    con.commit()
    con.close()
    return factura_id


def procesar_factura_completa(factura_id: int) -> dict:
    """
    Flujo completo: XML → Firmar → Enviar → Consultar → Guardar.
    Devuelve resultado con estado final.
    """
    from sri.xml_generator import generar_xml_factura
    from sri.signer import firmar_xml
    from sri.sri_client import enviar_comprobante, consultar_autorizacion
    import time

    config = obtener_config_sri()
    if not config:
        return {"ok": False, "error": "No hay configuración SRI guardada."}

    con = sqlite3.connect(DB_PATH)

    # Cargar factura
    fila = con.execute("SELECT * FROM facturas WHERE id = ?", (factura_id,)).fetchone()
    cols_f = ["id","clave_acceso","numero_autorizacion","estado","ambiente",
              "fecha_emision","fecha_autorizacion","ruc_emisor","razon_social_emisor",
              "tipo_identificacion","identificacion","razon_social","correo",
              "telefono","direccion","subtotal_0","subtotal_15","subtotal_no_iva",
              "descuento_total","iva_15","total","establecimiento","punto_emision",
              "secuencial","ruta_xml","ruta_xml_autorizado","ruta_ride",
              "cliente_id","observacion"]
    factura = dict(zip(cols_f, fila))

    # Cargar detalles
    filas_d = con.execute(
        "SELECT * FROM factura_detalle WHERE factura_id = ?", (factura_id,)
    ).fetchall()
    cols_d = ["id","factura_id","descripcion","cantidad","precio_unitario",
              "descuento","tiene_iva","porcentaje_iva","subtotal","iva","total"]
    detalles = [dict(zip(cols_d, d)) for d in filas_d]
    con.close()

    # 1. Generar XML
    try:
        xml_content, clave_acceso, secuencial = generar_xml_factura(
            config, factura, detalles
        )
    except Exception as e:
        return {"ok": False, "error": f"Error generando XML: {e}"}

    # 2. Guardar XML sin firmar
    ruta_xmls = config.get("ruta_xmls") or os.path.join(get_app_dir(), "facturas", "xml")
    os.makedirs(ruta_xmls, exist_ok=True)
    ruta_xml = os.path.join(ruta_xmls, f"{clave_acceso}.xml")
    with open(ruta_xml, "w", encoding="utf-8") as f:
        f.write(xml_content)

    # 3. Firmar XML
    try:
        xml_firmado = firmar_xml(
            xml_content,
            config["ruta_certificado"],
            config["clave_certificado"]
        )
    except Exception as e:
        return {"ok": False, "error": f"Error firmando XML: {e}"}

    # 4. Enviar al SRI
    resultado_envio = enviar_comprobante(xml_firmado, config["ambiente"])
    if not resultado_envio["ok"]:
        _actualizar_estado_factura(factura_id, "RECHAZADA", clave_acceso)
        return {"ok": False, "error": f"SRI rechazó: {resultado_envio['mensajes']}"}

    # 5. Esperar y consultar autorización
    time.sleep(3)
    resultado_auth = consultar_autorizacion(clave_acceso, config["ambiente"])

    # 6. Guardar XML autorizado
    ruta_xml_auth = None
    if resultado_auth.get("xml_autorizado"):
        ruta_xml_auth = os.path.join(ruta_xmls, f"{clave_acceso}_autorizado.xml")
        with open(ruta_xml_auth, "w", encoding="utf-8") as f:
            f.write(resultado_auth["xml_autorizado"])

    # 7. Actualizar BD
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        UPDATE facturas SET
            clave_acceso        = ?,
            numero_autorizacion = ?,
            fecha_autorizacion  = ?,
            estado              = ?,
            ruta_xml            = ?,
            ruta_xml_autorizado = ?,
            secuencial          = ?
        WHERE id = ?
    """, (
        clave_acceso,
        resultado_auth.get("numero_autorizacion", ""),
        resultado_auth.get("fecha_autorizacion", ""),
        resultado_auth.get("estado", "PENDIENTE"),
        ruta_xml,
        ruta_xml_auth,
        secuencial,
        factura_id
    ))
    con.commit()
    con.close()

    return {
        "ok":                  resultado_auth.get("ok", False),
        "estado":              resultado_auth.get("estado", "PENDIENTE"),
        "clave_acceso":        clave_acceso,
        "numero_autorizacion": resultado_auth.get("numero_autorizacion", ""),
        "factura_id":          factura_id,
    }


def _actualizar_estado_factura(factura_id: int, estado: str, clave_acceso: str = None):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "UPDATE facturas SET estado=?, clave_acceso=? WHERE id=?",
        (estado, clave_acceso, factura_id)
    )
    con.commit()
    con.close()