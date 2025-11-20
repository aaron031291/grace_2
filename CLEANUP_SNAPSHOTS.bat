@echo off
echo ========================================
echo  Grace Snapshot Cleanup
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run cleanup script (keep last 5 snapshots, dry-run first)
echo Running in DRY-RUN mode first...
python scripts\cleanup_snapshots.py --keep 5 --keep-days 7 --dry-run

echo.
echo ========================================
echo.
set /p CONFIRM="Do you want to proceed with deletion? (y/n): "

if /i "%CONFIRM%"=="y" (
    echo.
    echo Running actual cleanup...
    python scripts\cleanup_snapshots.py --keep 5 --keep-days 7
) else (
    echo Cleanup cancelled.
)

echo.
pause
