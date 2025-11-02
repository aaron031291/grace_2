@echo off
echo ========================================
echo Starting Grace Backend Server
echo ========================================
echo.
echo Checking dependencies...
python -m pip install -q -r requirements.txt
echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python main.py
