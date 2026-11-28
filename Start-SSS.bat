@echo off
setlocal
title SchoolServer Security - Einrichtung
cd /d "%~dp0"
set "APP_INSTALL=%LOCALAPPDATA%\Programs\SchoolServer Security"
set "VENV=%APP_INSTALL%\.venv"
set "PY_CMD=py -3"
where py >nul 2>nul
if errorlevel 1 set "PY_CMD=python"
%PY_CMD% -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
if errorlevel 1 goto python_missing
if not exist "%APP_INSTALL%" mkdir "%APP_INSTALL%"
if not exist "%VENV%\Scripts\python.exe" (
  echo [SSS] Erstelle private Python-Umgebung ...
  %PY_CMD% -m venv "%VENV%"
  if errorlevel 1 goto venv_failed
)
"%VENV%\Scripts\python.exe" -c "import PySide6" >nul 2>nul
if errorlevel 1 (
  echo [SSS] Installiere benoetigte Bibliotheken ohne Administratorrechte ...
  "%VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check -r "%~dp0SSS_Data\requirements.txt"
  if errorlevel 1 goto pip_failed
)
if exist "%VENV%\Scripts\pythonw.exe" (
  start "" "%VENV%\Scripts\pythonw.exe" "%~dp0sss_main.py"
) else (
  start "" "%VENV%\Scripts\python.exe" "%~dp0sss_main.py"
)
exit /b 0

:python_missing
echo.
echo Python 3.11 oder neuer wird benoetigt.
echo Installiere Python von https://www.python.org/downloads/windows/
echo Waehle "Install Now". Eine Installation fuer den aktuellen Benutzer reicht.
echo Administratorrechte sind fuer SSS nicht erforderlich.
pause
exit /b 1

:venv_failed
echo.
echo Die private Python-Umgebung konnte nicht erstellt werden.
echo Pruefe, ob Python 3.11+ installiert ist und dein Benutzerordner beschreibbar ist.
pause
exit /b 1

:pip_failed
echo.
echo Die Bibliothek PySide6 konnte nicht installiert werden.
echo Pruefe deine Internetverbindung und starte Start-SSS.bat erneut.
pause
exit /b 1
