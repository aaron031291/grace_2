@echo off
echo ================================================================================
echo GRACE SAFE CONSOLIDATION (Review Only)
echo ================================================================================
echo.
echo This script will SHOW what will be consolidated (safe, no changes)
echo.
pause

echo.
echo === Current Structure ===
echo.
echo Root directories:
dir /A:D /B | findstr /V "grace_rebuild .git node_modules __pycache__"
echo.

echo === grace_rebuild structure ===
echo.
dir /A:D /B grace_rebuild | findstr /V "node_modules __pycache__ .pytest"
echo.

echo === Files to consolidate ===
echo.
echo Backend modules:
dir /B grace_rebuild\backend\*.py 2>nul | find /C ".py"
echo.
echo Frontend components:
dir /S /B grace_rebuild\grace-frontend\src\components\*.tsx 2>nul | find /C ".tsx"
echo.
echo Documentation files:
dir /B grace_rebuild\docs\*.md 2>nul | find /C ".md"
echo.
echo Test scripts:
dir /B grace_rebuild\scripts\test*.py 2>nul | find /C ".py"
echo.

echo === Differences ===
echo.
echo Root scripts/ vs grace_rebuild/scripts/:
echo   Root has: 13 files
dir /B scripts 2>nul
echo.
echo   grace_rebuild has: 38 files
dir /B grace_rebuild\scripts 2>nul | find /C ".py"
echo.

echo grace_rebuild has MORE and NEWER code.
echo.
echo === Recommendation ===
echo.
echo SAFE TO CONSOLIDATE:
echo   - grace_rebuild has all the new code
echo   - Root has old duplicates
echo   - Frontend in grace_rebuild is more complete (20+ components vs 4)
echo.
echo To proceed:
echo   Run: CONSOLIDATE.bat
echo.
pause
