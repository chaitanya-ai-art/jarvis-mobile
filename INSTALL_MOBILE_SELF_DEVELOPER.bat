@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo JARVIS MOBILE SELF-DEVELOPER V1 INSTALLER
echo ==================================================

if not exist "D:\Jarvis\app" (
  echo ERROR: D:\Jarvis\app was not found.
  pause
  exit /b 1
)

set BACKUP=D:\Jarvis_Backup_MobileSelfDeveloper
if not exist "%BACKUP%" mkdir "%BACKUP%"
copy /Y "D:\Jarvis\app\main.py" "%BACKUP%\main.py" >nul

xcopy /E /I /Y "%~dp0patch\app" "D:\Jarvis\app" >nul

findstr /I /C:"openai" "D:\Jarvis\requirements.txt" >nul || echo openai^>=1.0.0>>"D:\Jarvis\requirements.txt"
findstr /I /C:"httpx" "D:\Jarvis\requirements.txt" >nul || echo httpx^>=0.27.0>>"D:\Jarvis\requirements.txt"

echo.
echo Installed active files into D:\Jarvis\app
echo Backup: %BACKUP%
echo.
echo Next:
echo 1. Configure Render variables OPENAI_API_KEY, GITHUB_TOKEN, GITHUB_REPO
echo 2. git add .
echo 3. git commit -m "Add mobile self developer"
echo 4. git push
echo.
pause
