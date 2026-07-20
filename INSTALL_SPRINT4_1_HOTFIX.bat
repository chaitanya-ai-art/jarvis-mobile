@echo off
setlocal
set "SOURCE=%~dp0"
set "TARGET=D:\Jarvis"
if not exist "%TARGET%" (
  echo ERROR: D:\Jarvis was not found.
  pause
  exit /b 1
)
echo.
echo ============================================================
echo JARVIS SPRINT 4.1 AUTHENTICATION HOTFIX
echo ============================================================
echo Stop Jarvis with Ctrl+C before continuing.
echo.
robocopy "%SOURCE%app" "%TARGET%\app" /E /R:2 /W:1 >nul
robocopy "%SOURCE%tests" "%TARGET%\tests" /E /R:2 /W:1 >nul
copy /Y "%SOURCE%README_SPRINT4_1.md" "%TARGET%\README_SPRINT4_1.md" >nul
if exist "%SOURCE%requirements.txt" copy /Y "%SOURCE%requirements.txt" "%TARGET%\requirements.txt" >nul

REM Update only the version in the user's existing settings; preserve token and all other values.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='%TARGET%\config\settings.json'; if(Test-Path $p){$j=Get-Content $p -Raw|ConvertFrom-Json; $j.version='7.3.1'; $j|ConvertTo-Json -Depth 10|Set-Content $p -Encoding UTF8}"

echo.
echo Hotfix installed. Existing token, database, memories, and settings were preserved.
echo Start D:\Jarvis\START_JARVIS_V7.bat and open the NEW PHONE APP URL.
pause
