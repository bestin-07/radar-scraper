@echo off
echo Testing radar scraper batch functionality...
echo.

REM Check if virtual environment exists and set Python command
if exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment detected: .venv
    set PYTHON_CMD=.venv\Scripts\python.exe
) else if exist "venv\Scripts\python.exe" (
    echo [INFO] Virtual environment detected: venv
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    echo [WARN] No virtual environment found. Using system Python.
    set PYTHON_CMD=python
)

echo [INFO] Using Python command: %PYTHON_CMD%
echo.

echo [TEST] Running MOSDAC script...
echo.
%PYTHON_CMD% mosdac_only.py
echo.
echo [TEST] MOSDAC script completed!
pause
