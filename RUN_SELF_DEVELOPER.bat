@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  set /p REQUEST=What should Jarvis develop? 
) else (
  set REQUEST=%*
)
".venv\Scripts\python.exe" developer_agent.py "%REQUEST%"
pause
