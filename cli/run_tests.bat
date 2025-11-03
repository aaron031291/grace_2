@echo off
REM Grace CLI Test Runner for Windows

echo ========================================
echo Grace CLI - Running Tests
echo ========================================
echo.

REM Check if pytest is installed
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo [ERROR] pytest not installed
    echo Installing pytest...
    pip install pytest pytest-asyncio pytest-mock
    echo.
)

REM Run tests
echo Running test suite...
echo.
python -m pytest tests/ -v --tb=short

echo.
echo ========================================
echo Test run complete
echo ========================================

pause
