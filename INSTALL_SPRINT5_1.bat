@echo off
setlocal
set "SOURCE=%~dp0"
set "TARGET=D:\Jarvis"
if not exist "%TARGET%" (
  echo ERROR: D:\Jarvis was not found.
  pause
  exit /b 1
)
echo Installing Jarvis Sprint 5.1 Command Router...
robocopy "%SOURCE%app" "%TARGET%\app" /E /NFL /NDL /NJH /NJS /NP >nul
copy /Y "%SOURCE%requirements.txt" "%TARGET%\requirements.txt" >nul
copy /Y "%SOURCE%run_server.py" "%TARGET%\run_server.py" >nul
copy /Y "%SOURCE%START_JARVIS_V7.bat" "%TARGET%\START_JARVIS_V7.bat" >nul
copy /Y "%SOURCE%RUN_TESTS.bat" "%TARGET%\RUN_TESTS.bat" >nul
if exist "%SOURCE%tests" robocopy "%SOURCE%tests" "%TARGET%\tests" /E /NFL /NDL /NJH /NJS /NP >nul
if not exist "%TARGET%\config\settings.json" copy /Y "%SOURCE%config\settings.json" "%TARGET%\config\settings.json" >nul
echo.
echo Sprint 5.1 installed. Existing token and database were preserved.
echo Start D:\Jarvis\START_JARVIS_V7.bat
pause
