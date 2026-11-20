[Setup]
AppId={{C91A0B16-3D25-4AC3-A3A1-SSS200000001}
AppName=SchoolServer Security
AppVersion=2.0.0
AppPublisher=Adam Gabriel Kraus
DefaultDirName={autopf}\SchoolServer Security
DefaultGroupName=SchoolServer Security
OutputDir=dist
OutputBaseFilename=SSS-Setup-2.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
Uninstallable=yes

[Files]
Source: "..\dist\SSS.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SchoolServer Security"; Filename: "{app}\SSS.exe"
Name: "{autodesktop}\SchoolServer Security"; Filename: "{app}\SSS.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Verknüpfungen:"

[Run]
Filename: "{app}\SSS.exe"; Description: "SchoolServer Security starten"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\SchoolServer Security"
