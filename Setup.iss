[Setup]
AppId={{54863722-45F6-43C3-B636-366A0D97C81B}
AppName=CopyTo-MoveTo
AppVersion=1.0
AppPublisher=Emboiko
AppPublisherURL=https://github.com/emboiko/CopyTo-MoveTo
AppSupportURL=https://github.com/emboiko/CopyTo-MoveTo
AppUpdatesURL=https://github.com/emboiko/CopyTo-MoveTo
DefaultDirName={commonpf64}\CopyTo-MoveTo
DisableProgramGroupPage=yes
OutputDir=C:\Programming\Python\Projects\CopyTo-MoveTo
OutputBaseFilename=CopyTo-MoveTo Installer
SetupIconFile=C:\Programming\Python\Projects\CopyTo-MoveTo\dist\CopyTo-MoveTo\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Programming\Python\Projects\CopyTo-MoveTo\dist\CopyTo-MoveTo\CopyTo-MoveTo.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Programming\Python\Projects\CopyTo-MoveTo\dist\CopyTo-MoveTo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\CopyTo-MoveTo"; Filename: "{app}\CopyTo-MoveTo.exe"
Name: "{autodesktop}\CopyTo-MoveTo"; Filename: "{app}\CopyTo-MoveTo.exe"; Tasks: desktopicon

[Registry]

;Sources:
;--------

;Files:
Root: HKCR64; Subkey: "*\shell\CopyTo-MoveTo as source"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR64; Subkey: "*\shell\CopyTo-MoveTo as source\command"; ValueType: string; ValueName: ""; ValueData:"""{app}\CopyTo-MoveTo.exe"" ""s|%1"""; Flags: uninsdeletekey
;Directories:
Root: HKCR64; Subkey: "directory\shell\CopyTo-MoveTo as source"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR64; Subkey: "directory\shell\CopyTo-MoveTo as source\command"; ValueType: string; ValueName: ""; ValueData:"""{app}\CopyTo-MoveTo.exe"" ""s|%1"""; Flags: uninsdeletekey
;Directory Background:
Root: HKCR64; Subkey: "directory\background\shell\CopyTo-MoveTo as source"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR64; Subkey: "directory\background\shell\CopyTo-MoveTo as source\command"; ValueType: string; ValueName: ""; ValueData:"""{app}\CopyTo-MoveTo.exe"" ""s|%v"""; Flags: uninsdeletekey

;Destinations:
;-------------

;Directories:
Root: HKCR64; Subkey: "directory\shell\CopyTo-MoveTo as destination"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR64; Subkey: "directory\shell\CopyTo-MoveTo as destination\command"; ValueType: string; ValueName: ""; ValueData:"""{app}\CopyTo-MoveTo.exe"" ""d|%1"""; Flags: uninsdeletekey
;Directory background:
Root: HKCR64; Subkey: "directory\background\shell\CopyTo-MoveTo as destination"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR64; Subkey: "directory\background\shell\CopyTo-MoveTo as destination\command"; ValueType: string; ValueName: ""; ValueData:"""{app}\CopyTo-MoveTo.exe"" ""d|%v"""; Flags: uninsdeletekey

[Run]
Filename: "{app}\CopyTo-MoveTo.exe"; Description: "{cm:LaunchProgram,CopyTo-MoveTo}"; Flags: 64bit nowait postinstall skipifsilent 