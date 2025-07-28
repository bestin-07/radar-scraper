@echo off
echo.
echo ======================================================
echo    Kerala Radar Data Collection System - Enhanced
echo ======================================================
echo.

REM Check if virtual environment exists and set Python command
if exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment detected: .venv
    echo [INFO] Using isolated Python environment for better dependency management
    set PYTHON_CMD=.venv\Scripts\python.exe
    echo [DEBUG] Python command set to: .venv\Scripts\python.exe
    echo.
) else if exist "venv\Scripts\python.exe" (
    echo [INFO] Virtual environment detected: venv
    echo [INFO] Using isolated Python environment for better dependency management
    set PYTHON_CMD=venv\Scripts\python.exe
    echo [DEBUG] Python command set to: venv\Scripts\python.exe
    echo.
) else (
    echo [WARN] No virtual environment found. Using system Python.
    echo [WARN] Consider creating a virtual environment for better isolation.
    set PYTHON_CMD=python
    echo [DEBUG] Python command set to: python
    echo.
)

:start
echo.
echo ===============================================
echo            AVAILABLE OPTIONS
echo ===============================================
echo.
echo 1. Download ALL radar types (6 types: CAZ, PPZ, PPI, ZDR, VP2, 3DS)
echo 2. Download MOSDAC data only (Kochi radar with pattern matching)
echo 3. Start hourly automated scheduler (all types)
echo 4. Start 30-minute automated scheduler (all types)
echo 5. Run flake8 code quality check
echo 6. Install/Update requirements
echo 7. Exit
echo.
echo ===============================================
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo.
    echo ===============================================
    echo         DOWNLOADING ALL RADAR TYPES
    echo ===============================================
    echo [INFO] Starting comprehensive radar download...
    echo [INFO] This will download 6 types: CAZ, PPZ, PPI, ZDR, VP2, 3DS
    echo [INFO] Plus MOSDAC pattern-matched data
    echo.
    %PYTHON_CMD% radar_scraper.py
    echo.
    echo [DONE] Download session completed!
    pause
    goto start
) else if "%choice%"=="2" (
    echo.
    echo ===============================================
    echo         DOWNLOADING MOSDAC DATA ONLY
    echo ===============================================
    echo [INFO] Starting MOSDAC-only download...
    echo [INFO] Using smart pattern matching for Kochi radar
    echo [INFO] Checking last hour with flexible timestamp matching
    echo.
    %PYTHON_CMD% mosdac_only.py
    echo.
    echo [DONE] MOSDAC download completed!
    pause
    goto start
) else if "%choice%"=="3" (
    echo.
    echo ===============================================
    echo         STARTING HOURLY SCHEDULER
    echo ===============================================
    echo [INFO] Starting automated hourly scheduler...
    echo [INFO] Will download all radar types every hour
    echo [WARN] Press Ctrl+C to stop the scheduler
    echo.
    %PYTHON_CMD% radar_scheduler.py
    goto start
) else if "%choice%"=="4" (
    echo.
    echo ===============================================
    echo       STARTING 30-MINUTE SCHEDULER
    echo ===============================================
    echo [INFO] Starting automated 30-minute scheduler...
    echo [INFO] Will download all radar types every 30 minutes
    echo [WARN] Press Ctrl+C to stop the scheduler
    echo.
    %PYTHON_CMD% -c "from radar_scheduler import run_custom_interval; run_custom_interval(30)"
    goto start
) else if "%choice%"=="5" (
    echo.
    echo ===============================================
    echo         RUNNING CODE QUALITY CHECK
    echo ===============================================
    echo [INFO] Running flake8 linting on Python files...
    echo [INFO] Checking code style, syntax, and best practices
    echo.
    %PYTHON_CMD% -m flake8 *.py --max-line-length=100 --show-source --statistics
    echo.
    echo [DONE] Code quality check completed!
    pause
    goto start
) else if "%choice%"=="6" (
    echo.
    echo ===============================================
    echo       INSTALLING/UPDATING REQUIREMENTS
    echo ===============================================
    echo [INFO] Installing required Python packages...
    echo [INFO] This may take a few moments depending on your connection
    echo.
    %PYTHON_CMD% -m pip install -r requirements.txt --upgrade
    echo.
    echo [DONE] Requirements installation completed!
    pause
    goto start
) else if "%choice%"=="7" (
    echo.
    echo ===============================================
    echo [INFO] Thank you for using Kerala Radar System!
    echo [INFO] All downloaded files are stored in 'radar_images' folder
    echo ===============================================
    echo.
    exit
) else (
    echo.
    echo ===============================================
    echo [ERROR] Invalid choice entered: "%choice%"
    echo [INFO] Please enter a number between 1-7
    echo ===============================================
    pause
    goto start
)
