[Setup]
AppName=Clair
AppVersion=1.0
DefaultDirName={pf}\Clair
DefaultGroupName=Clair
OutputBaseFilename=ClairInstaller

[Files]
; bundle the EXE we built with PyInstaller
Source: "dist\Clair.exe";          DestDir: "{app}"; Flags: ignoreversion
; include our config files from the project root
Source: "categories.json";        DestDir: "{app}"; Flags: ignoreversion
Source: "presets.json";           DestDir: "{app}"; Flags: ignoreversion

[Icons]
; create a Start-Menu shortcut
Name: "{group}\Clair";            Filename: "{app}\Clair.exe"
