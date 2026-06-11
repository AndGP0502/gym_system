"""
Firma el XML de facturas electrónicas para el SRI Ecuador.
Usa Java (FirmadorSRI.class) para firmar — compatible con .p12 del Banco Central.
"""

import subprocess
import os
import tempfile
import sys


def _get_java_signer_dir() -> str:
    """Obtiene la ruta al directorio java_signer."""
    if getattr(sys, 'frozen', False):
        # Modo .exe (PyInstaller)
        base = os.path.dirname(sys.executable)
    else:
        # Modo desarrollo
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "java_signer")


def firmar_xml(xml_content: str, ruta_p12: str, clave_p12: str) -> str:
    """
    Firma el XML usando Java (FirmadorSRI).
    Devuelve el XML firmado como string.
    """
    java_signer_dir = _get_java_signer_dir()
    firmador_class  = os.path.join(java_signer_dir, "FirmadorSRI.class")

    if not os.path.exists(firmador_class):
        raise Exception(
            f"No se encontró FirmadorSRI.class en: {java_signer_dir}\n"
            "Copia la carpeta java_signer a sri/"
        )

    # Crear archivos temporales
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.xml', delete=False) as f:
        f.write(xml_content.encode('utf-8'))
        xml_temp = f.name

    xml_out = xml_temp + "_firmado.xml"

    try:
        result = subprocess.run(
            [
                "java",
                "-Dfile.encoding=UTF-8",
                "-cp", java_signer_dir,
                "FirmadorSRI",
                xml_temp,
                ruta_p12,
                clave_p12,
                xml_out
            ],
            capture_output=True,
            timeout=30
        )

        stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''

        if result.returncode != 0:
            raise Exception(f"Error Java al firmar: {stderr}")

        if os.path.exists(xml_out):
            with open(xml_out, 'r', encoding='utf-8') as f:
                xml_firmado = f.read().strip()
        else:
            xml_firmado = result.stdout.decode('utf-8', errors='replace').strip()

        if not xml_firmado or "<Signature" not in xml_firmado:
            raise Exception(f"Java no generó firma válida. Stderr: {stderr[:300]}")

        return xml_firmado

    finally:
        if os.path.exists(xml_temp):
            os.unlink(xml_temp)
        if os.path.exists(xml_out):
            os.unlink(xml_out)