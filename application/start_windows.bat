@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -m pip install -r requirements.txt
  if errorlevel 1 goto error
  py run_echoeats.py
) else (
  python -m pip install -r requirements.txt
  if errorlevel 1 goto error
  python run_echoeats.py
)
pause
exit /b 0
:error
echo Could not install or run. Please install Python 3 and retry.
pause
