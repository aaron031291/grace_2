@echo off
REM Verify integrity of all 20 Grace models

echo ============================================================
echo GRACE MODEL INTEGRITY VERIFICATION
echo ============================================================
echo.
echo Verifying all 20 models...
echo This will take a few minutes...
echo.

python scripts/utilities/trust_framework_cli.py list-health

echo.
echo ============================================================
echo VERIFICATION COMPLETE
echo ============================================================
echo.
echo Check individual model details:
echo   python scripts/utilities/trust_framework_cli.py integrity MODEL_NAME
echo.
echo Run stress test to map execution windows:
echo   python scripts/utilities/trust_framework_cli.py stress-test MODEL_NAME
echo.

pause
