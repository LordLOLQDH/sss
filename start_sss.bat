@echo off
cd /d %~dp0
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto failed
py -3 sss_gui.py
exit /b 0
:failed
echo Setup failed. Check Python 3 and your internet connection.
pause
