@echo off
setlocal
set "TARGET=D:\Jarvis"
if not exist "%TARGET%\app\main.py" (
  echo ERROR: Jarvis project was not found at D:\Jarvis
  pause
  exit /b 1
)
set "BACKUP=%TARGET%\backup_v8_1"
if not exist "%BACKUP%" mkdir "%BACKUP%"
copy /Y "%TARGET%\app\core\config.py" "%BACKUP%\config.py" >nul
copy /Y "%TARGET%\app\services\chat_service.py" "%BACKUP%\chat_service.py" >nul
copy /Y "%TARGET%\app\web\index.html" "%BACKUP%\index.html" >nul
copy /Y "%~dp0update\app\core\config.py" "%TARGET%\app\core\config.py" >nul
copy /Y "%~dp0update\app\services\chat_service.py" "%TARGET%\app\services\chat_service.py" >nul
copy /Y "%~dp0update\app\web\index.html" "%TARGET%\app\web\index.html" >nul

echo Jarvis V8.1 Voice AI files installed.
echo Backup saved in D:\Jarvis\backup_v8_1
pause
