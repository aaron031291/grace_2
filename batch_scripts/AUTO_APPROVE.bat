@echo off
echo ========================================
echo Grace - Single Approval Mode
echo ========================================
echo.
echo Using SINGLE APPROVAL POINT for all operations
echo (No more 6 separate approvals)
echo.
set GRACE_AUTO_APPROVE=true
set GRACE_ENV=development
set GRACE_SINGLE_APPROVAL=true
set GRACE_BATCH_CONSENT=true
set GRACE_SKIP_CONSENT_PROMPTS=true
echo.
echo [OK] Single approval granted for ALL operations
echo.
echo Starting Grace...
echo.
python serve.py
