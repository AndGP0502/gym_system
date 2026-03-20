[Setup]
AppName=GymSystem
AppVersion=1.0
DefaultDirName={autopf}\GymSystem
DefaultGroupName=GymSystem
OutputDir=installer_output
OutputBaseFilename=GymSystem_Installer
Compression=lzma
SolidCompression=yes

[Dirs]
Name: "{userappdata}\GymSystem"; Flags: uninsneveruninstall

[Files]
Source: "dist\GymSystem.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "gym.db"; DestDir: "{userappdata}\GymSystem"; Flags: ignoreversion uninsneveruninstall

[Icons]
Name: "{group}\GymSystem"; Filename: "{app}\GymSystem.exe"
Name: "{commondesktop}\GymSystem"; Filename: "{app}\GymSystem.exe"

[Run]
Filename: "{app}\GymSystem.exe"; Description: "Ejecutar GymSystem"; Flags: nowait postinstall skipifsilent