@echo off
setlocal
set "TARGET=D:\Jarvis"
if not exist "%TARGET%\app\web\index.html" (
  echo Jarvis was not found at D:\Jarvis
  pause
  exit /b 1
)
echo Installing Jarvis Sprint 5.2 Secure Voice...
copy /Y "%~dp0app\web\index.html" "%TARGET%\app\web\index.html" >nul
copy /Y "%~dp0generate_https_cert.py" "%TARGET%\generate_https_cert.py" >nul
copy /Y "%~dp0run_server_https.py" "%TARGET%\run_server_https.py" >nul
copy /Y "%~dp0START_JARVIS_SECURE_VOICE.bat" "%TARGET%\START_JARVIS_SECURE_VOICE.bat" >nul
copy /Y "%~dp0README_SPRINT5_2_SECURE_VOICE.md" "%TARGET%\README_SPRINT5_2_SECURE_VOICE.md" >nul
copy /Y "%~dp0requirements.txt" "%TARGET%\requirements.txt" >nul
"%TARGET%\.venv\Scripts\python.exe" -m pip install -r "%TARGET%\requirements.txt"
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)
"%TARGET%\.venv\Scripts\python.exe" "%TARGET%\generate_https_cert.py"
echo.
echo Sprint 5.2 installed successfully.
echo Start Jarvis using D:\Jarvis\START_JARVIS_SECURE_VOICE.bat
pause
