@echo off
echo ============================================================
echo Grace Quick Setup
echo ============================================================
echo.

echo [1/4] Installing Python dependencies...
py -m pip install -r requirements.txt
echo.

echo [2/4] Installing frontend dependencies...
cd grace-frontend
call npm install
cd ..
echo.

echo [3/4] Initializing database...
py reset_db.py
echo.

echo [4/4] Verifying system...
py verify_startup.py
echo.

echo ============================================================
echo SETUP COMPLETE
echo ============================================================
echo.
echo To start Grace:
echo   python grace_cli.py start
echo.
echo Or manually:
echo   Terminal 1: py -m uvicorn backend.main:app --reload
echo   Terminal 2: cd grace-frontend ^&^& npm run dev
echo.
pause
