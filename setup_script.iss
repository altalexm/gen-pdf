[Setup]
AppName=StarPDF
AppId={{StarPDF}}
AppVersion=3.0.1
AppPublisher=STAR SOFTWARE
DefaultDirName={autopf}\StarPDF
DefaultGroupName=StarPDF
UninstallDisplayIcon={app}\StarPDF.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
OutputBaseFilename=StarPDF-3.0.1-setup
LicenseFile=LICENSE
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\StarPDF.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\StarPDF"; Filename: "{app}\StarPDF.exe"
Name: "{group}\{cm:UninstallProgram,StarPDF}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\StarPDF"; Filename: "{app}\StarPDF.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\StarPDF.exe"; Description: "{cm:LaunchProgram,StarPDF}"; Flags: nowait postinstall skipifsilent
