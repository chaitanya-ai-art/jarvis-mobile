@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo JARVIS V9 MOBILE-FIRST ACTIVATION
echo ==================================================

if not exist "D:\Jarvis\app" (
  echo ERROR: D:\Jarvis\app not found.
  pause
  exit /b 1
)

set BACKUP=D:\Jarvis_Backup_V9_Mobile_First
if not exist "%BACKUP%\app\api" mkdir "%BACKUP%\app\api"
if not exist "%BACKUP%\app\web" mkdir "%BACKUP%\app\web"

copy /Y "D:\Jarvis\app\api\dashboard.py" "%BACKUP%\app\api\dashboard.py" >nul
if exist "D:\Jarvis\app\web\assistant.html" copy /Y "D:\Jarvis\app\web\assistant.html" "%BACKUP%\app\web\assistant.html" >nul

xcopy /E /I /Y "%~dp0patch\app" "D:\Jarvis\app" >nul
xcopy /E /I /Y "%~dp0patch\tests" "D:\Jarvis\tests" >nul

echo.
echo Active Jarvis files updated.
echo Backup created at: %BACKUP%
echo.
echo Next commands:
echo   cd /d D:\Jarvis
echo   .venv\Scripts\python.exe -m pytest -q
echo   git add app\api\dashboard.py app\web\assistant.html tests\test_v9_mobile_first.py
echo   git commit -m "Activate Jarvis V9 mobile first"
echo   git push
echo.
pause
