@echo off
setlocal
set "TARGET=D:\Jarvis"

echo ==========================================================
echo JARVIS SPRINT 3 MOBILE DASHBOARD HOTFIX
echo ==========================================================

if not exist "%TARGET%\app" (
  echo ERROR: %TARGET% was not found or is not a Jarvis project.
  echo Extract your Jarvis project to D:\Jarvis first.
  pause
  exit /b 1
)

echo Stop the running Jarvis window before continuing.
echo Installing into %TARGET% ...

xcopy "%~dp0app" "%TARGET%\app\" /E /I /Y >nul
copy /Y "%~dp0requirements.txt" "%TARGET%\requirements.txt" >nul
copy /Y "%~dp0run_server.py" "%TARGET%\run_server.py" >nul
copy /Y "%~dp0START_JARVIS_V7.bat" "%TARGET%\START_JARVIS_V7.bat" >nul
copy /Y "%~dp0RUN_TESTS.bat" "%TARGET%\RUN_TESTS.bat" >nul

if errorlevel 1 (
  echo Installation failed. Check permissions and try again.
  pause
  exit /b 1
)

echo.
echo SUCCESS: Sprint 3 hotfix installed.
echo Your config\settings.json and data\jarvis.db were not replaced.
echo Start: D:\Jarvis\START_JARVIS_V7.bat
pause
