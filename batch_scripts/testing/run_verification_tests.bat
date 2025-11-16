@echo off
REM Comprehensive verification test runner for Windows
REM Can be run locally or in CI

echo ======================================================================
echo GRACE VERIFICATION SYSTEM - COMPREHENSIVE TEST SUITE
echo ======================================================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Step 1: Ensure schema is up to date
echo [1] Applying migrations...
python -m alembic upgrade head
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Migration failed
    exit /b 1
)

REM Step 2: Create learning tables
echo.
echo [2] Creating learning tables...
python create_learning_tables.py
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Learning tables creation failed
    exit /b 1
)

REM Step 3: Create cube schema
echo.
echo [3] Creating data cube schema...
python -m backend.data_cube.schema
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Cube schema creation failed
    exit /b 1
)

REM Step 4: Run simple verification test
echo.
echo [4] Running simple verification test...
python test_verification_simple.py
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Simple test failed
    exit /b 1
)

REM Step 5: Run comprehensive test suite
echo.
echo [5] Running comprehensive test suite...
set PYTHONPATH=%CD%
python tests\test_verification_comprehensive.py
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Comprehensive tests failed
    exit /b 1
)

echo.
echo ======================================================================
echo ALL TESTS PASSED
echo ======================================================================
echo.
echo Verification system is fully operational:
echo   - Happy path: PASS
echo   - Rollback path: PASS
echo   - Mission tracking: PASS
echo   - Concurrent execution: PASS
echo   - Database persistence: PASS
echo.

exit /b 0
