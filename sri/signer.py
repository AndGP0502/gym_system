"""
Firmador XAdES-BES para comprobantes electrónicos del SRI Ecuador.

Python puro (cryptography + lxml). Sin Java, sin OpenSSL externo.
Compatible con certificados .p12 de TODAS las entidades acreditadas:
BCE, Security Data, Lazzate, Uanataca, ANF, Datil, etc.

Puntos clave:
- Carga robusta del .p12: busca la entrada cuya clave privada corresponda
  al certificado de firma, sin asumir el orden interno del archivo
  (los .p12 de Lazzate/Uanataca traen la cadena CA en posiciones variables).
- Estructura XAdES-BES exactamente como la exige la ficha técnica del SRI:
  3 referencias (SignedProperties, KeyInfo/Certificate, #comprobante),
  RSA-SHA1, digest SHA1, c14n inclusivo.
"""

import base64
import hashlib
import random
from datetime import datetime, timezone, timedelta

from lxml import etree
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates


# ──────────────────────────────────────────────────────────────────────────────
# Carga robusta del certificado .p12
# ──────────────────────────────────────────────────────────────────────────────

def cargar_p12(ruta_p12: str, clave_p12: str):
    """
    Devuelve (clave_privada, certificado_de_firma).

    Maneja todas las variantes de estructura interna:
    - BCE / Security Data: el cert de firma viene como certificado principal.
    - Lazzate / Uanataca: el cert principal puede venir None o ser uno de la
      cadena CA; el cert de firma real está en additional_certificates.
    Estrategia: el certificado correcto es el ÚNICO cuya clave pública
    coincide con la clave privada del .p12.
    """
    with open(ruta_p12, "rb") as f:
        datos = f.read()

    try:
        clave_privada, cert, extras = load_key_and_certificates(
            datos, clave_p12.encode("utf-8")
        )
    except ValueError as e:
        raise Exception(
            f"No se pudo abrir el certificado .p12. Verifica que la clave sea correcta. Detalle: {e}"
        )

    if clave_privada is None:
        raise Exception("El archivo .p12 no contiene una clave privada.")

    pub_key_der = clave_privada.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )

    candidatos = []
    if cert is not None:
        candidatos.append(cert)
    if extras:
        candidatos.extend(extras)

    cert_firma = None
    for c in candidatos:
        c_pub = c.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        if c_pub == pub_key_der:
            cert_firma = c
            break

    if cert_firma is None:
        raise Exception(
            "El .p12 no contiene un certificado que corresponda a la clave privada. "
            "El archivo puede estar corrupto o ser solo una cadena de CA."
        )

    return clave_privada, cert_firma


def info_certificado(ruta_p12: str, clave_p12: str) -> dict:
    """Información del certificado para mostrar en la UI de configuración."""
    _, cert = cargar_p12(ruta_p12, clave_p12)
    return {
        "sujeto": cert.subject.rfc4514_string(),
        "emisor": cert.issuer.rfc4514_string(),
        "valido_desde": cert.not_valid_before_utc.isoformat(),
        "valido_hasta": cert.not_valid_after_utc.isoformat(),
        "vigente": cert.not_valid_before_utc <= datetime.now(timezone.utc) <= cert.not_valid_after_utc,
        "serial": str(cert.serial_number),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Utilidades de firma
# ──────────────────────────────────────────────────────────────────────────────

def _sha1_b64(data: bytes) -> str:
    return base64.b64encode(hashlib.sha1(data).digest()).decode()


def _c14n(xml_str: str) -> bytes:
    """Canonicalización XML inclusiva (xml-c14n-20010315), la que usa el SRI."""
    parser = etree.XMLParser(remove_blank_text=False)
    node = etree.fromstring(xml_str.encode("utf-8"), parser=parser)
    return etree.tostring(node, method="c14n", exclusive=False, with_comments=False)


def _partir_b64(b64: str, ancho: int = 76) -> str:
    return "\n".join(b64[i:i + ancho] for i in range(0, len(b64), ancho))


def _rand_id() -> int:
    return random.randint(990, 999000)


# ──────────────────────────────────────────────────────────────────────────────
# Firma XAdES-BES
# ──────────────────────────────────────────────────────────────────────────────

XMLNS_DS = 'xmlns:ds="http://www.w3.org/2000/09/xmldsig#"'
XMLNS_ETSI = 'xmlns:etsi="http://uri.etsi.org/01903/v1.3.2#"'


def firmar_xml(xml_content: str, ruta_p12: str, clave_p12: str) -> str:
    """
    Firma un comprobante electrónico con XAdES-BES según la ficha técnica
    del SRI. Mantiene la misma interfaz que el firmador anterior.
    """
    clave_privada, cert = cargar_p12(ruta_p12, clave_p12)

    if not isinstance(clave_privada, rsa.RSAPrivateKey):
        raise Exception("El SRI requiere certificados con clave RSA.")

    # ── Preparar documento ────────────────────────────────────────────────
    parser = etree.XMLParser(remove_blank_text=False)
    doc = etree.fromstring(xml_content.encode("utf-8"), parser=parser)

    # Digest del comprobante (referencia enveloped: documento sin firma)
    comprobante_c14n = etree.tostring(doc, method="c14n", exclusive=False, with_comments=False)
    sha1_comprobante = _sha1_b64(comprobante_c14n)

    # ── Datos del certificado ─────────────────────────────────────────────
    cert_der = cert.public_bytes(serialization.Encoding.DER)
    cert_b64 = _partir_b64(base64.b64encode(cert_der).decode())
    sha1_cert = _sha1_b64(cert_der)

    issuer_name = cert.issuer.rfc4514_string()
    serial_number = str(cert.serial_number)

    pub = clave_privada.public_key().public_numbers()
    modulo_b64 = _partir_b64(base64.b64encode(
        pub.n.to_bytes((pub.n.bit_length() + 7) // 8, "big")).decode())
    exponente_b64 = base64.b64encode(
        pub.e.to_bytes((pub.e.bit_length() + 7) // 8, "big")).decode()

    # ── IDs aleatorios (estilo ficha técnica SRI) ─────────────────────────
    signature_id = _rand_id()
    signedinfo_id = _rand_id()
    signedprops_id = _rand_id()
    signedprops_ref_id = _rand_id()
    keyinfo_id = _rand_id()
    sigvalue_id = _rand_id()
    object_id = _rand_id()
    comprobante_ref_id = _rand_id()

    # Hora local de Ecuador (UTC-5)
    tz_ec = timezone(timedelta(hours=-5))
    signing_time = datetime.now(tz_ec).strftime("%Y-%m-%dT%H:%M:%S%z")
    signing_time = signing_time[:-2] + ":" + signing_time[-2:]  # -0500 → -05:00

    # ── SignedProperties ──────────────────────────────────────────────────
    signed_properties = (
        f'<etsi:SignedProperties Id="Signature{signature_id}-SignedProperties{signedprops_id}">'
        f'<etsi:SignedSignatureProperties>'
        f'<etsi:SigningTime>{signing_time}</etsi:SigningTime>'
        f'<etsi:SigningCertificate>'
        f'<etsi:Cert>'
        f'<etsi:CertDigest>'
        f'<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod>'
        f'<ds:DigestValue>{sha1_cert}</ds:DigestValue>'
        f'</etsi:CertDigest>'
        f'<etsi:IssuerSerial>'
        f'<ds:X509IssuerName>{issuer_name}</ds:X509IssuerName>'
        f'<ds:X509SerialNumber>{serial_number}</ds:X509SerialNumber>'
        f'</etsi:IssuerSerial>'
        f'</etsi:Cert>'
        f'</etsi:SigningCertificate>'
        f'</etsi:SignedSignatureProperties>'
        f'<etsi:SignedDataObjectProperties>'
        f'<etsi:DataObjectFormat ObjectReference="#Reference-ID-{comprobante_ref_id}">'
        f'<etsi:Description>contenido comprobante</etsi:Description>'
        f'<etsi:MimeType>text/xml</etsi:MimeType>'
        f'</etsi:DataObjectFormat>'
        f'</etsi:SignedDataObjectProperties>'
        f'</etsi:SignedProperties>'
    )

    # Digest de SignedProperties: se canonicaliza CON los namespaces heredados
    sp_para_digest = signed_properties.replace(
        "<etsi:SignedProperties ",
        f"<etsi:SignedProperties {XMLNS_DS} {XMLNS_ETSI} ",
        1,
    )
    sha1_signed_properties = _sha1_b64(_c14n(sp_para_digest))

    # ── KeyInfo ───────────────────────────────────────────────────────────
    key_info = (
        f'<ds:KeyInfo Id="Certificate{keyinfo_id}">'
        f'<ds:X509Data>'
        f'<ds:X509Certificate>\n{cert_b64}\n</ds:X509Certificate>'
        f'</ds:X509Data>'
        f'<ds:KeyValue>'
        f'<ds:RSAKeyValue>'
        f'<ds:Modulus>\n{modulo_b64}\n</ds:Modulus>'
        f'<ds:Exponent>{exponente_b64}</ds:Exponent>'
        f'</ds:RSAKeyValue>'
        f'</ds:KeyValue>'
        f'</ds:KeyInfo>'
    )
    ki_para_digest = key_info.replace(
        "<ds:KeyInfo ", f"<ds:KeyInfo {XMLNS_DS} {XMLNS_ETSI} ", 1
    )
    sha1_key_info = _sha1_b64(_c14n(ki_para_digest))

    # ── SignedInfo ────────────────────────────────────────────────────────
    signed_info = (
        f'<ds:SignedInfo Id="Signature-SignedInfo{signedinfo_id}">'
        f'<ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></ds:CanonicalizationMethod>'
        f'<ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ds:SignatureMethod>'
        f'<ds:Reference Id="SignedPropertiesID{signedprops_ref_id}" '
        f'Type="http://uri.etsi.org/01903#SignedProperties" '
        f'URI="#Signature{signature_id}-SignedProperties{signedprops_id}">'
        f'<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod>'
        f'<ds:DigestValue>{sha1_signed_properties}</ds:DigestValue>'
        f'</ds:Reference>'
        f'<ds:Reference URI="#Certificate{keyinfo_id}">'
        f'<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod>'
        f'<ds:DigestValue>{sha1_key_info}</ds:DigestValue>'
        f'</ds:Reference>'
        f'<ds:Reference Id="Reference-ID-{comprobante_ref_id}" URI="#comprobante">'
        f'<ds:Transforms>'
        f'<ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform>'
        f'</ds:Transforms>'
        f'<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ds:DigestMethod>'
        f'<ds:DigestValue>{sha1_comprobante}</ds:DigestValue>'
        f'</ds:Reference>'
        f'</ds:SignedInfo>'
    )

    # Firmar SignedInfo canonicalizado con namespaces heredados
    si_para_firma = signed_info.replace(
        "<ds:SignedInfo ", f"<ds:SignedInfo {XMLNS_DS} {XMLNS_ETSI} ", 1
    )
    firma = clave_privada.sign(_c14n(si_para_firma), padding.PKCS1v15(), hashes.SHA1())
    signature_value = _partir_b64(base64.b64encode(firma).decode())

    # ── Ensamblar firma completa ──────────────────────────────────────────
    xades = (
        f'<ds:Signature {XMLNS_DS} {XMLNS_ETSI} Id="Signature{signature_id}">'
        f'{signed_info}'
        f'<ds:SignatureValue Id="SignatureValue{sigvalue_id}">\n{signature_value}\n</ds:SignatureValue>'
        f'{key_info}'
        f'<ds:Object Id="Signature{signature_id}-Object{object_id}">'
        f'<etsi:QualifyingProperties Target="#Signature{signature_id}">'
        f'{signed_properties}'
        f'</etsi:QualifyingProperties>'
        f'</ds:Object>'
        f'</ds:Signature>'
    )

    # Insertar la firma antes del cierre del elemento raíz
    xml_sin_decl = etree.tostring(doc, encoding="unicode")
    pos_cierre = xml_sin_decl.rfind("</")
    xml_firmado = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        + xml_sin_decl[:pos_cierre]
        + xades
        + xml_sin_decl[pos_cierre:]
    )

    return xml_firmado