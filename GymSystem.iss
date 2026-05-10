; ============================================================
;  GymSystem — Inno Setup Script
;  Genera: installer_output\GymSystem_Installer.exe
; ============================================================

#define AppName      "GymSystem"
#define AppVersion   "1.0"
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
; Requiere permisos de administrador para instalar en Archivos de programa
PrivilegesRequired=admin
; Crea carpeta de datos del usuario al instalar
; (la app la crea sola, pero lo forzamos aquí también)
ArchitecturesInstallIn64BitMode=x64compatible

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

; ──────────────────────────────────────────────────────────
;  Archivos
; ──────────────────────────────────────────────────────────
[Files]
; ── Ejecutable principal ──
Source: "dist\{#AppExeName}";      DestDir: "{app}";                       Flags: ignoreversion

; ── Base de datos inicial (solo si NO existe ya una del usuario) ──
Source: "gym.db";                  DestDir: "{userappdata}\{#AppName}";    Flags: ignoreversion onlyifdoesntexist uninsneveruninstall

; ── Configuración inicial (solo si NO existe ya) ──
Source: "Config.JSON";             DestDir: "{userappdata}\{#AppName}";    Flags: ignoreversion onlyifdoesntexist uninsneveruninstall

; ── Assets (logo, avatar por defecto, etc.) ──
Source: "assets\*";                DestDir: "{userappdata}\{#AppName}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs uninsneveruninstall

; ──────────────────────────────────────────────────────────
;  Accesos directos
; ──────────────────────────────────────────────────────────
[Icons]
Name: "{group}\{#AppName}";        Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"

; ──────────────────────────────────────────────────────────
;  Ejecutar al terminar la instalación
; ──────────────────────────────────────────────────────────
[Run]
Filename: "{app}\{#AppExeName}"; Description: "Ejecutar {#AppName} ahora"; Flags: nowait postinstall skipifsilent

; ──────────────────────────────────────────────────────────
;  Desinstalación (no toca los datos del usuario)
; ──────────────────────────────────────────────────────────
[UninstallDelete]
Type: filesandordirs; Name: "{app}"