@echo off
cd /d "%~dp0"
py -3 sss_scanner.py
if errorlevel 1 (
  echo.
  echo SSS konnte nicht gestartet werden. Ist Python 3 installiert?
  pause
)
