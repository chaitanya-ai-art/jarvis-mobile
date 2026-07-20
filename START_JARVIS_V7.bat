@echo off
setlocal
cd /d "%~dp0"
title Jarvis V7 Unified Core

where py >nul 2>nul
if %errorlevel%==0 (
    set PYTHON=py
) else (
    set PYTHON=python
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

python run_server.py
exit /b 0

:error
echo.
echo Jarvis could not start. Review the error above.
pause
exit /b 1
