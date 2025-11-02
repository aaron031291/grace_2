@echo off
echo ========================================
echo Grace Speech Pipeline Test Suite
echo ========================================
echo.

echo Running speech pipeline tests...
python -m pytest tests/test_speech_pipeline.py -v --tb=short

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo All speech tests passed!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Some tests failed. Check output above.
    echo ========================================
)

echo.
pause
