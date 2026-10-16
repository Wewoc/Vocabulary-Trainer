@echo off
:: start.bat - Vokabeltrainer launcher
:: Starts the GUI from src/. Window stays open after exit or a crash so
:: any error message can be read (pattern from Garmin Local Archive's
:: src/bat/run_T1.bat).

cd /d "%~dp0.."

python start.py
if errorlevel 1 (
    echo.
    echo === App exited with an error ^(errorlevel %errorlevel%^) ===
)
pause
