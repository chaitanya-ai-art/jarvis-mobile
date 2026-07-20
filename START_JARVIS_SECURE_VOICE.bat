@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Jarvis virtual environment was not found.
  echo Run INSTALL_SPRINT5_2_SECURE_VOICE.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" run_server_https.py
pause
