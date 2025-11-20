@echo off
echo ========================================
echo  GRACE: ACHIEVING 100%% UNIFICATION
echo ========================================
echo.

cd /d %~dp0

echo Step 1: Running fast migration...
python -u scripts/fast_migrate_all.py

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Migration failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Verifying changes...
python -c "import subprocess; subprocess.run(['git', 'diff', '--stat'])"

echo.
echo ========================================
echo  ✅ 100%% UNIFICATION COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Review changes with: git diff
echo 2. Test the system
echo 3. Commit: git commit -am "Achieve 100%% unification"
echo.
pause
