@echo off
echo ========================================
echo   Grace Integration Tests
echo ========================================
echo.

cd /d "%~dp0"

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

echo Running complete integration tests...
echo.

python -m pytest tests/test_complete_integration.py -v

echo.
pause
