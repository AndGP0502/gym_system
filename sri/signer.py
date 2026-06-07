import subprocess
import os
import tempfile


def firmar_xml(xml_content: str, ruta_p12: str, clave_p12: str) -> str:
    """
    Firma el XML usando OpenSSL via subprocess.
    Devuelve el XML firmado como string.
    """
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
            "-passin", f"pass:{clave_p12}"
        ], capture_output=True, text=True)

        if resultado.returncode != 0:
            print("ERROR OPENSSL CERTIFICADO:")
            print(resultado.stderr)
            raise Exception("No se pudo extraer el certificado del .p12")

        # Extraer llave privada
        resultado2 = subprocess.run([
            "openssl", "pkcs12", "-in", p12_path,
            "-nocerts", "-nodes", "-out", key_path,
            "-passin", f"pass:{clave_p12}"
        ], capture_output=True, text=True)

        if resultado2.returncode != 0:
            print("ERROR OPENSSL LLAVE:")
            print(resultado2.stderr)
            raise Exception("No se pudo extraer la llave privada del .p12")

        # Firmar con signxml (Python)
        _firmar_con_python(xml_content, cert_path, key_path, out_path)

        with open(out_path, "r", encoding="utf-8") as f:
            return f.read()


def _firmar_con_python(xml_content, cert_path, key_path, out_path):
    """Firma usando la librería signxml de Python."""
    from signxml import XMLSigner, methods
    from lxml import etree

    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
    )

    with open(cert_path, "rb") as f:
        cert_pem = f.read()
    with open(key_path, "rb") as f:
        key_pem = f.read()

    root   = etree.fromstring(xml_content.encode("utf-8"))
    signed = signer.sign(root, key=key_pem, cert=cert_pem)

    with open(out_path, "wb") as f:
        f.write(etree.tostring(signed, pretty_print=True))