@echo off
setlocal
set "SOURCE=%~dp0"
set "TARGET=D:\Jarvis"
if not exist "%TARGET%" (
  echo ERROR: D:\Jarvis was not found.
  pause
  exit /b 1
)
echo Stopping Jarvis first is required.
echo Installing Sprint 4 into %TARGET% ...
robocopy "%SOURCE%app" "%TARGET%\app" /E /R:2 /W:1 >nul
robocopy "%SOURCE%tests" "%TARGET%\tests" /E /R:2 /W:1 >nul
copy /Y "%SOURCE%README_SPRINT4.md" "%TARGET%\README_SPRINT4.md" >nul
if exist "%SOURCE%requirements.txt" copy /Y "%SOURCE%requirements.txt" "%TARGET%\requirements.txt" >nul
echo.
echo Sprint 4 installed. Your config, token, and database were not replaced.
echo Start D:\Jarvis\START_JARVIS_V7.bat
pause
