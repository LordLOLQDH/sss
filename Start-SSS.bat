@echo off
setlocal
title SchoolServer Security
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.10+ ist nicht installiert oder nicht im PATH.
  echo Installiere Python von https://www.python.org/downloads/windows/
  echo Beim Setup "Add Python to PATH" aktivieren.
  pause
  exit /b 1
)
if not exist ".venv\\Scripts\\python.exe" (
  echo Erstelle lokale Python-Umgebung ...
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
echo Pruefe/installiere SSS-Abhaengigkeiten ...
".venv\\Scripts\\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto failed
echo Starte SchoolServer Security ...
start "" ".venv\\Scripts\\pythonw.exe" "%~dp0sss_gui.py"
exit /b 0
:failed
echo SSS konnte nicht vorbereitet werden. Pruefe Python und deine Internetverbindung.
pause
exit /b 1
