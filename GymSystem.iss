; ============================================================
;  GymSystem — Inno Setup Script
;  Genera: installer_output\GymSystem_Installer.exe
;
;  IMPORTANTE: este script SOLO empaqueta el .exe ya compilado.
;  Antes de compilar el instalador, recompila el .exe con PyInstaller:
;      pyinstaller GymSystem.spec --noconfirm
;  Eso deja el ejecutable nuevo en dist\GymSystem.exe (modo onefile).
; ============================================================

#define AppName      "GymSystem"
#define AppVersion   "1.1"
#define AppPublisher "Software de Control A&D"
#define AppExeName   "GymSystem.exe"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppId={{B7A2C4E1-3F9D-4B2A-8C1E-5D6F7A8B9C0D}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=installer_output
OutputBaseFilename=GymSystem_Installer
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Icono del instalador
SetupIconFile=assets\logo_gym.ico
; Icono que se muestra en "Agregar o quitar programas"
UninstallDisplayIcon={app}\{#AppExeName}
; Requiere permisos de administrador para instalar en Archivos de programa
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
; Python 3.12 (PyInstaller) requiere Windows 8.1 o superior
MinVersion=6.3
; Si la app está abierta al instalar/actualizar, cerrarla para poder
; reemplazar el .exe (evita el error "archivo en uso"). No la reabre sola.
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

; ──────────────────────────────────────────────────────────
;  Carpetas
; ──────────────────────────────────────────────────────────
[Dirs]
; Carpeta de datos del usuario — nunca se borra al desinstalar
Name: "{userappdata}\{#AppName}";                        Flags: uninsneveruninstall
Name: "{userappdata}\{#AppName}\backups";                Flags: uninsneveruninstall
Name: "{userappdata}\{#AppName}\assets";                 Flags: uninsneveruninstall
; Carpeta donde la app guarda los XML/RIDE de facturas emitidas
Name: "{userappdata}\{#AppName}\facturas";               Flags: uninsneveruninstall
Name: "{userappdata}\{#AppName}\facturas\xml";           Flags: uninsneveruninstall

; ──────────────────────────────────────────────────────────
;  Archivos
; ──────────────────────────────────────────────────────────
[Files]
; ── Ejecutable principal (onefile generado por PyInstaller) ──
Source: "dist\{#AppExeName}";      DestDir: "{app}";                       Flags: ignoreversion

; ── Base de datos inicial (solo si NO existe ya una del usuario) ──
;    En una actualización NO se sobrescribe: se conservan los datos del gimnasio.
Source: "gym.db";                  DestDir: "{userappdata}\{#AppName}";    Flags: onlyifdoesntexist uninsneveruninstall

; ── Configuración inicial (solo si NO existe ya) ──
Source: "Config.JSON";             DestDir: "{userappdata}\{#AppName}";    Flags: onlyifdoesntexist uninsneveruninstall

; ── Assets (logo, avatar por defecto, etc.) ──
Source: "assets\*";                DestDir: "{userappdata}\{#AppName}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs uninsneveruninstall

; ──────────────────────────────────────────────────────────
;  Accesos directos
; ──────────────────────────────────────────────────────────
[Icons]
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{commondesktop}\{#AppName}";      Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}";  Filename: "{uninstallexe}"

; ──────────────────────────────────────────────────────────
;  Ejecutar al terminar la instalación
; ──────────────────────────────────────────────────────────
[Run]
Filename: "{app}\{#AppExeName}"; Description: "Ejecutar {#AppName} ahora"; Flags: nowait postinstall skipifsilent

; ──────────────────────────────────────────────────────────
;  Desinstalación (no toca los datos del usuario en {userappdata})
; ──────────────────────────────────────────────────────────
[UninstallDelete]
Type: filesandordirs; Name: "{app}"
