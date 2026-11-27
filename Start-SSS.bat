@echo off
setlocal
title SchoolServer Security
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.10 oder neuer wurde nicht gefunden.
  echo Installiere Python von https://www.python.org/downloads/windows/
  echo Aktiviere beim Setup die Option "Add python.exe to PATH".
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo SSS wird einmalig vorbereitet. Das ist kein Installer.
  py -3 -m venv .venv
  if errorlevel 1 goto failed
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto failed
)
".venv\Scripts\pythonw.exe" sss_gui.py
if errorlevel 1 (
  ".venv\Scripts\python.exe" sss_gui.py
)
exit /b 0
:failed
echo SSS konnte nicht vorbereitet werden. Pruefe deine Internetverbindung und Python-Installation.
pause
exit /b 1
