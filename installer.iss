; Preprocessor definitions for easy versioning
#define MyAppName "Sistema Reservas de Salas"
#define MyAppVersion "1.0.0"
#define MyPublisher "Rinaldi"

[Setup]
AppId={{E0F0ABD5-6D4B-4ED8-B0E1-9D4E427CE79B}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=Sistema_Reservas_Salas-{#MyAppVersion}-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=resources\icone_completo.ico
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
VersionInfoVersion={#MyAppVersion}

[Files]
Source: "dist\Sistema_Reservas_Salas.exe"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; Flags: unchecked

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\Sistema_Reservas_Salas.exe"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\Sistema_Reservas_Salas.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Sistema_Reservas_Salas.exe"; Description: "Executar {#MyAppName}"; Flags: postinstall nowait skipifsilent
