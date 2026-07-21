@echo off
setlocal
cd /d "%~dp0"

echo Installing Jarvis Self Developer V1...
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv was not found in this Jarvis folder.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade openai
if errorlevel 1 (
  echo ERROR: Failed to install OpenAI SDK.
  pause
  exit /b 1
)

echo.
echo Installed successfully.
echo.
echo Before use, set OPENAI_API_KEY as a Windows environment variable.
echo Then run:
echo   .venv\Scripts\python.exe developer_agent.py "Hide PC controls in cloud mode"
echo.
pause
