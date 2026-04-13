@echo off
REM Quick start script for the Web UI

echo.
echo ========================================
echo Parallel Computing Web UI - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Start the Flask app
echo.
echo ========================================
echo Starting Flask application...
echo ========================================
echo.
echo Open your browser and go to:
echo http://127.0.0.1:5000
echo.
python app/app.py

pause
