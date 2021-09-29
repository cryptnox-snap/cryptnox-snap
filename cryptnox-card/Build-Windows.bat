REM Build CryptnoxCLI package for Windows
@echo off

RMDIR /S /Q dist

"%UserProfile%\AppData\Local\Programs\Python\Python36\Scripts\pyinstaller.exe" .\cryptnoxcli.spec

"%ProgramFiles(x86)%\NSIS\makensis.exe" cryptnoxcli.nsi

echo(
echo dist/CryptnoxCLI-setup.exe package DONE
PAUSE
