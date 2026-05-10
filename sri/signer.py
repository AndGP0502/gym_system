import subprocess
import os
import tempfile


def firmar_xml(xml_content: str, ruta_p12: str, clave_p12: str) -> str:
    """
    Firma el XML usando OpenSSL via subprocess.
    Requiere que OpenSSL esté instalado en el sistema.
    Devuelve el XML firmado como string.
    """
    # Extraer certificado y llave del .p12
    with tempfile.TemporaryDirectory() as tmpdir:
        p12_path  = ruta_p12
        cert_path = os.path.join(tmpdir, "cert.pem")
        key_path  = os.path.join(tmpdir, "key.pem")
        xml_path  = os.path.join(tmpdir, "factura.xml")
        out_path  = os.path.join(tmpdir, "factura_firmada.xml")

        # Escribir XML sin firmar
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        # Extraer certificado
        resultado = subprocess.run([
            "openssl", "pkcs12", "-in", p12_path,
            "-nokeys", "-clcerts", "-out", cert_path,
            "-passin", f"pass:{clave_p12}", "-legacy"
        ], capture_output=True, text=True)

        if resultado.returncode != 0:
            print("ERROR OPENSSL CERTIFICADO:")
            print(resultado.stderr)
            raise Exception("No se pudo extraer el certificado del .p12")

        # Extraer llave privada
        subprocess.run([
            "openssl", "pkcs12", "-in", p12_path,
            "-nocerts", "-nodes", "-out", key_path,
            "-passin", f"pass:{clave_p12}", "-legacy"
        ], check=True, capture_output=True)

        # Firmar usando xmlsec1 si está disponible, sino usar python-xmlsec
        try:
            _firmar_con_xmlsec1(xml_path, cert_path, key_path, out_path)
        except Exception:
            _firmar_con_python(xml_content, cert_path, key_path, out_path)

        with open(out_path, "r", encoding="utf-8") as f:
            return f.read()


def _firmar_con_xmlsec1(xml_path, cert_path, key_path, out_path):
    """Firma usando xmlsec1 (más compatible con el SRI)."""
    subprocess.run([
        "xmlsec1", "--sign",
        "--pkcs8-pem", key_path,
        "--pwd", "",
        "--output", out_path,
        xml_path
    ], check=True, capture_output=True)


def _firmar_con_python(xml_content, cert_path, key_path, out_path):
    """Fallback: firma usando la librería signxml de Python."""
    from signxml import XMLSigner
    from lxml import etree

    from signxml import methods

    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
    )

    with open(cert_path, "rb") as f:
        cert_pem = f.read()
    with open(key_path, "rb") as f:
        key_pem = f.read()

    root = etree.fromstring(xml_content.encode("utf-8"))
    signed = signer.sign(root, key=key_pem, cert=cert_pem)

    with open(out_path, "wb") as f:
        f.write(etree.tostring(signed, pretty_print=True))