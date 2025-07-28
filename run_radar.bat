@echo off
echo.
echo ======================================================
echo    Kerala Radar Data Collection System
echo ======================================================
echo.
echo Choose an option:
echo.
echo 1. Download radar data once (all 6 types)
echo 2. Start hourly automated scheduler
echo 3. Start 30-minute automated scheduler
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting single radar download...
    python radar_scraper.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Starting hourly scheduler...
    echo Press Ctrl+C to stop
    python radar_scheduler.py
) else if "%choice%"=="3" (
    echo.
    echo Starting 30-minute scheduler...
    echo Press Ctrl+C to stop
    python -c "from radar_scheduler import run_custom_interval; run_custom_interval(30)"
) else if "%choice%"=="4" (
    echo.
    echo Goodbye!
    exit
) else (
    echo.
    echo Invalid choice. Please try again.
    pause
    goto start
)

:start
call %0
