@echo off
echo ===================================
echo GRACE 100%% UNIFICATION MIGRATION
echo ===================================
echo.

cd /d "%~dp0"

echo Running unification migrator...
python scripts\complete_unification.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo ✅ MIGRATION SUCCESSFUL
    echo ===================================
) else (
    echo.
    echo ===================================
    echo ❌ MIGRATION FAILED
    echo ===================================
)

pause
