@echo off
echo Starting Pediatric Doctor Management System...
echo Please wait while the application loads...

REM Navigate to the application directory
cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the application
echo Application starting at http://localhost:5000
echo Press Ctrl+C to stop the application
python src\main.py

pause
