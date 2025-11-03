@echo off
echo ========================================
echo Grace Rebuild - Backend Server
echo ========================================
echo.
echo Installing dependencies...
py -m pip install -q -r requirements.txt
echo.
echo Starting server on http://localhost:8000
echo.
uvicorn backend.main:app --reload
