@echo off
echo ========================================
echo Emergency Database Fix for Grace
echo ========================================
echo.

echo [1/4] Killing all Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 3 /nobreak >nul

echo [2/4] Backing up database...
if exist databases\grace.db (
    copy databases\grace.db databases\grace.db.backup >nul
    echo Backup created: databases\grace.db.backup
)

echo [3/4] Clearing database locks...
del /F /Q databases\*.db-wal 2>nul
del /F /Q databases\*.db-shm 2>nul
del /F /Q databases\*.db-journal 2>nul

echo [4/4] Resetting database with WAL mode...
.venv\Scripts\python.exe -c "import sqlite3; conn = sqlite3.connect('databases/grace.db'); conn.execute('PRAGMA journal_mode=WAL'); conn.execute('PRAGMA busy_timeout=30000'); conn.commit(); conn.close(); print('WAL mode enabled')"

echo.
echo ========================================
echo Database fixed! Starting Grace...
echo ========================================
echo.

.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
