# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

# ── Datos que deben ir dentro del .exe ──────────────────────────────────────
datas = [
    ('assets',      'assets'),       # logo, avatar, etc.
    ('Config.JSON', '.'),            # config inicial
    ('gym.db',      '.'),            # base de datos inicial
    ('sri/xsd',     'sri/xsd'),      # esquemas XSD del SRI
]

binaries   = []
hiddenimports = [
    # UI
    'customtkinter',
    'ttkbootstrap',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',

    # BD / datos
    'sqlite3',
    'unittest',
    'unittest.mock',
    'unittest.case',
    'unittest.suite',
    'unittest.runner',
    'unittest.loader',
    'openpyxl',
    'openpyxl.styles',

    # PDF
    'reportlab',
    'reportlab.lib',
    'reportlab.platypus',
    'reportlab.lib.styles',
    'reportlab.lib.enums',

    # Facturación / firma
    'cryptography',
    'cryptography.hazmat.primitives.serialization.pkcs12',
    'OpenSSL',
    'lxml',
    'lxml.etree',
    'signxml',
    'zeep',

    # Red
    'requests',
    'urllib3',
    'certifi',

    # Selenium
    'selenium',
    'selenium.webdriver.chrome.options',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.support',
    'selenium.webdriver.remote.webelement',
    'selenium.webdriver.remote.command',
    'webdriver_manager',

    # Stdlib que PyInstaller puede omitir
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'tkinter.simpledialog',
    'json',
    'uuid',
    'subprocess',
    'shutil',
    'traceback',
    'time',
    'xml.sax.saxutils',
]

# Recoger paquetes completos con sus metadatos y hooks
for pkg in ('zeep', 'certifi', 'signxml', 'cryptography', 'ttkbootstrap',
            'customtkinter', 'reportlab', 'openpyxl', 'PIL', 'matplotlib'):
    d, b, h = collect_all(pkg)
    datas    += d
    binaries += b
    hiddenimports += h

# Submódulos de módulos propios
hiddenimports += collect_submodules('modulos')
hiddenimports += collect_submodules('database')
hiddenimports += collect_submodules('services')
hiddenimports += collect_submodules('sri')
hiddenimports += collect_submodules('ui')

# ── Análisis ────────────────────────────────────────────────────────────────
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'IPython', 'notebook'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GymSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                   # sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets\\logo_gym.ico',     # icono del .exe
)