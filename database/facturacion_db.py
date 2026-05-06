import sqlite3
import os
from modulos.rutas import get_db_path

DB_PATH = get_db_path()


def inicializar_tablas_facturacion():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_sri (
            id                  INTEGER PRIMARY KEY DEFAULT 1,
            ruc                 TEXT NOT NULL,
            razon_social        TEXT NOT NULL,
            nombre_comercial    TEXT,
            direccion_matriz    TEXT,
            direccion_sucursal  TEXT,
            codigo_establecimiento TEXT DEFAULT '001',
            punto_emision       TEXT DEFAULT '001',
            ambiente            INTEGER DEFAULT 1,  -- 1=pruebas, 2=produccion
            tipo_emision        INTEGER DEFAULT 1,
            ruta_certificado    TEXT,
            clave_certificado   TEXT,
            siguiente_secuencial INTEGER DEFAULT 1,
            correo_remitente    TEXT,
            smtp_host           TEXT,
            smtp_port           INTEGER DEFAULT 587,
            smtp_usuario        TEXT,
            smtp_clave          TEXT,
            ruta_xmls           TEXT,
            ruta_rides          TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            clave_acceso        TEXT UNIQUE,
            numero_autorizacion TEXT,
            estado              TEXT DEFAULT 'BORRADOR',
            ambiente            INTEGER DEFAULT 2,
            fecha_emision       TEXT,
            fecha_autorizacion  TEXT,
            -- Emisor
            ruc_emisor          TEXT,
            razon_social_emisor TEXT,
            -- Receptor
            tipo_identificacion TEXT DEFAULT '05',
            identificacion      TEXT,
            razon_social        TEXT,
            correo              TEXT,
            telefono            TEXT,
            direccion           TEXT,
            -- Totales
            subtotal_0          REAL DEFAULT 0,
            subtotal_15         REAL DEFAULT 0,
            subtotal_no_iva     REAL DEFAULT 0,
            descuento_total     REAL DEFAULT 0,
            iva_15              REAL DEFAULT 0,
            total               REAL DEFAULT 0,
            -- Secuencial
            establecimiento     TEXT DEFAULT '001',
            punto_emision       TEXT DEFAULT '001',
            secuencial          TEXT,
            -- Archivos
            ruta_xml            TEXT,
            ruta_xml_autorizado TEXT,
            ruta_ride           TEXT,
            -- Referencia cliente
            cliente_id          INTEGER,
            observacion         TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS factura_detalle (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            factura_id      INTEGER NOT NULL,
            descripcion     TEXT NOT NULL,
            cantidad        REAL NOT NULL,
            precio_unitario REAL NOT NULL,
            descuento       REAL DEFAULT 0,
            tiene_iva       INTEGER DEFAULT 1,
            porcentaje_iva  REAL DEFAULT 15,
            subtotal        REAL NOT NULL,
            iva             REAL NOT NULL,
            total           REAL NOT NULL,
            FOREIGN KEY(factura_id) REFERENCES facturas(id)
        )
    """)

    con.commit()
    con.close()
    print("Tablas de facturación creadas.")


inicializar_tablas_facturacion()