@echo off
echo.
echo ========================================
echo  Grace Book System - Verification
echo ========================================
echo.

echo [1/4] Checking database...
python -c "import sqlite3; conn = sqlite3.connect('databases/memory_fusion.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); tables = cursor.fetchall(); print(f'  Found {len(tables)} tables'); conn.close()"
if errorlevel 1 (
    echo   ERROR: Database not initialized
    echo   Run: python scripts\init_book_tables_simple.py
    pause
    exit /b 1
)

echo [2/4] Checking directories...
if not exist "grace_training\documents\books" (
    echo   ERROR: Books directory missing
    echo   Run: python scripts\init_book_tables_simple.py
    pause
    exit /b 1
)
echo   Books directory exists

echo [3/4] Checking backend dependencies...
python -c "import aiosqlite; print('  aiosqlite installed')" 2>nul
if errorlevel 1 (
    echo   WARNING: aiosqlite not installed
    echo   Run: pip install aiosqlite
)

echo [4/4] Checking frontend...
if not exist "frontend\node_modules" (
    echo   WARNING: Frontend dependencies not installed
    echo   Run: cd frontend ^&^& npm install
) else (
    echo   Frontend dependencies installed
)

echo.
echo ========================================
echo  System Status: READY
echo ========================================
echo.
echo Next steps:
echo   1. Start backend: python serve.py
echo   2. Start frontend: cd frontend ^&^& npm run dev
echo   3. Open browser: http://localhost:5173
echo.
echo Features to test:
echo   - Memory Studio ^> File Organizer (undo button)
echo   - Memory Studio ^> Books (book ingestion)
echo   - Bottom-right: Librarian Co-pilot button
echo   - Top-right: Notification toasts
echo.
pause
