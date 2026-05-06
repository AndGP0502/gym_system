import requests
import base64
from datetime import datetime


WSDL_RECEPCION = {
    1: "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
    2: "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
}

WSDL_AUTORIZACION = {
    1: "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
    2: "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
}


def enviar_comprobante(xml_firmado: str, ambiente: int = 1) -> dict:
    """
    Envía el XML firmado al SRI.
    Devuelve dict con estado y mensajes.
    """
    try:
        from zeep import Client
        xml_b64 = base64.b64encode(xml_firmado.encode("utf-8")).decode("utf-8")
        client   = Client(WSDL_RECEPCION[ambiente])
        response = client.service.validarComprobante(xml=xml_b64)

        estado    = response.estado
        mensajes  = []
        if hasattr(response, "comprobantes") and response.comprobantes:
            for comp in response.comprobantes.comprobante:
                if hasattr(comp, "mensajes"):
                    for m in comp.mensajes.mensaje:
                        mensajes.append({
                            "identificador": m.identificador,
                            "mensaje":       m.mensaje,
                            "tipo":          m.tipo,
                        })

        return {"estado": estado, "mensajes": mensajes, "ok": estado == "RECIBIDA"}

    except Exception as e:
        return {"estado": "ERROR", "mensajes": [str(e)], "ok": False}


def consultar_autorizacion(clave_acceso: str, ambiente: int = 1) -> dict:
    """
    Consulta la autorización de un comprobante en el SRI.
    Devuelve dict con estado, número de autorización y fecha.
    """
    try:
        from zeep import Client
        client   = Client(WSDL_AUTORIZACION[ambiente])
        response = client.service.autorizacionComprobante(
            claveAccesoComprobante=clave_acceso
        )

        autorizaciones = response.autorizaciones
        if not autorizaciones or not autorizaciones.autorizacion:
            return {"estado": "PENDIENTE", "ok": False}

        auth = autorizaciones.autorizacion[0]
        return {
            "estado":               auth.estado,
            "numero_autorizacion":  auth.numeroAutorizacion,
            "fecha_autorizacion":   str(auth.fechaAutorizacion),
            "xml_autorizado":       auth.comprobante if hasattr(auth, "comprobante") else "",
            "ok":                   auth.estado == "AUTORIZADO",
        }

    except Exception as e:
        return {"estado": "ERROR", "mensajes": [str(e)], "ok": False}