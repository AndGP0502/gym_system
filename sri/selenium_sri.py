"""
Automatización del Facturador SRI con Selenium.
Abre Chrome, inicia sesión y llena el formulario de factura automáticamente.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


URL_SRI = "https://facturadorsri.sri.gob.ec/portal-facturadorsri-internet/pages/inicio.html"


def _iniciar_driver():
    """Inicia Chrome con opciones óptimas."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def _esperar(driver, by, selector, timeout=15):
    """Espera a que un elemento esté presente y lo devuelve."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )


def _esperar_clickable(driver, by, selector, timeout=15):
    """Espera a que un elemento sea clickeable y lo devuelve."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )


def emitir_factura_sri(ruc: str, clave: str, factura: dict, detalles: list) -> dict:
    """
    Abre el facturador del SRI, inicia sesión y emite una factura.
    
    factura: {
        "identificacion": "cedula/ruc del cliente",
        "razon_social": "nombre del cliente",
        "direccion": "dirección del cliente",
        "correo": "correo del cliente",
        "telefono": "teléfono del cliente",
        "tipo_identificacion": "05" (cedula) / "04" (ruc)
    }
    
    detalles: [
        {
            "descripcion": "descripción del servicio",
            "cantidad": 1,
            "precio_unitario": 20.00,
            "descuento": 0,
            "porcentaje_iva": 15
        }
    ]
    """
    driver = None
    try:
        driver = _iniciar_driver()
        wait   = WebDriverWait(driver, 20)

        # 1. Abrir facturador SRI
        driver.get(URL_SRI)
        time.sleep(2)

        # 2. Iniciar sesión
        campo_ruc   = _esperar(driver, By.NAME, "ruc")
        campo_clave = driver.find_element(By.NAME, "clave")
        campo_ruc.clear()
        campo_ruc.send_keys(ruc)
        campo_clave.clear()
        campo_clave.send_keys(clave)
        driver.find_element(By.XPATH, "//input[@value='Ingresar'] | //button[contains(text(),'Ingresar')]").click()
        time.sleep(3)

        # 3. Ir a Emisión → Factura
        menu_emision = _esperar_clickable(driver, By.XPATH, "//a[contains(text(),'Emisión')]")
        menu_emision.click()
        time.sleep(1)

        opcion_factura = _esperar_clickable(driver, By.XPATH, "//a[contains(text(),'Factura')]")
        opcion_factura.click()
        time.sleep(2)

        # 4. Llenar datos del receptor
        # Tipo de identificación
        try:
            select_tipo = Select(_esperar(driver, By.XPATH,
                "//select[contains(@id,'tipoIdentificacion') or contains(@name,'tipoIdentificacion')]"))
            tipo = factura.get("tipo_identificacion", "05")
            select_tipo.select_by_value(tipo)
            time.sleep(0.5)
        except Exception:
            pass

        # Identificación (cédula/RUC)
        campo_id = _esperar(driver, By.XPATH,
            "//input[contains(@id,'identificacion') or contains(@name,'identificacion')]")
        campo_id.clear()
        campo_id.send_keys(factura["identificacion"])
        time.sleep(1)

        # Razón social
        try:
            campo_razon = driver.find_element(By.XPATH,
                "//input[contains(@id,'razonSocial') or contains(@name,'razonSocial')]")
            if not campo_razon.get_attribute("value"):
                campo_razon.clear()
                campo_razon.send_keys(factura.get("razon_social", "CONSUMIDOR FINAL"))
        except Exception:
            pass

        # Dirección
        try:
            campo_dir = driver.find_element(By.XPATH,
                "//input[contains(@id,'direccion') or contains(@name,'direccion')]")
            campo_dir.clear()
            campo_dir.send_keys(factura.get("direccion", "N/A"))
        except Exception:
            pass

        # Correo
        try:
            campo_correo = driver.find_element(By.XPATH,
                "//input[contains(@id,'correo') or contains(@name,'correo') or contains(@type,'email')]")
            campo_correo.clear()
            campo_correo.send_keys(factura.get("correo", ""))
        except Exception:
            pass

        time.sleep(1)

        # 5. Agregar detalles
        for detalle in detalles:
            try:
                # Descripción
                campo_desc = _esperar_clickable(driver, By.XPATH,
                    "//input[contains(@id,'descripcion') or contains(@placeholder,'Descripción') or contains(@placeholder,'descripcion')]")
                campo_desc.clear()
                campo_desc.send_keys(detalle["descripcion"])
                time.sleep(0.3)

                # Cantidad
                try:
                    campo_cant = driver.find_element(By.XPATH,
                        "//input[contains(@id,'cantidad') or contains(@name,'cantidad')]")
                    campo_cant.clear()
                    campo_cant.send_keys(str(detalle["cantidad"]))
                except Exception:
                    pass

                # Precio unitario
                try:
                    campo_precio = driver.find_element(By.XPATH,
                        "//input[contains(@id,'precioUnitario') or contains(@name,'precioUnitario')]")
                    campo_precio.clear()
                    campo_precio.send_keys(str(detalle["precio_unitario"]))
                except Exception:
                    pass

                # Descuento
                try:
                    campo_desc_val = driver.find_element(By.XPATH,
                        "//input[contains(@id,'descuento') or contains(@name,'descuento')]")
                    campo_desc_val.clear()
                    campo_desc_val.send_keys(str(detalle.get("descuento", 0)))
                except Exception:
                    pass

                # IVA
                try:
                    select_iva = Select(driver.find_element(By.XPATH,
                        "//select[contains(@id,'iva') or contains(@name,'iva') or contains(@id,'porcentaje')]"))
                    pct = detalle.get("porcentaje_iva", 15)
                    if pct == 15:
                        select_iva.select_by_visible_text("15%")
                    else:
                        select_iva.select_by_visible_text("0%")
                except Exception:
                    pass

                # Botón agregar detalle
                try:
                    btn_agregar = _esperar_clickable(driver, By.XPATH,
                        "//button[contains(text(),'Agregar') or contains(@id,'agregar') or contains(@onclick,'agregar')]")
                    btn_agregar.click()
                    time.sleep(1)
                except Exception:
                    pass

            except Exception as e:
                return {"ok": False, "error": f"Error llenando detalle: {e}"}

        # 6. Emitir factura
        time.sleep(1)
        try:
            btn_emitir = _esperar_clickable(driver, By.XPATH,
                "//button[contains(text(),'Emitir') or contains(text(),'Guardar') or contains(text(),'Enviar')]")
            btn_emitir.click()
            time.sleep(3)
        except Exception as e:
            return {"ok": False, "error": f"No se encontró el botón de emitir: {e}"}

        # 7. Confirmar si hay popup de confirmación
        try:
            btn_confirmar = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(text(),'Sí') or contains(text(),'Aceptar') or contains(text(),'Confirmar')]"))
            )
            btn_confirmar.click()
            time.sleep(3)
        except Exception:
            pass

        # Dejar el navegador abierto para que el usuario vea el resultado
        return {"ok": True, "mensaje": "Factura enviada. Revisa el navegador para confirmar."}

    except Exception as e:
        return {"ok": False, "error": str(e)}