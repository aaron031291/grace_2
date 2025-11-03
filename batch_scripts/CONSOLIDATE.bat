@echo off
echo ================================================================================
echo GRACE CODEBASE CONSOLIDATION
echo ================================================================================
echo.
echo This will:
echo   1. Delete old duplicate files in root
echo   2. Move grace_rebuild contents to root
echo   3. Create clean single-source structure
echo.
echo Press CTRL+C to cancel, or
pause

echo.
echo [1/5] Creating backup...
git add -A 2>nul
git commit -m "Backup before consolidation" 2>nul
git branch backup-pre-consolidation 2>nul
echo   Done

echo.
echo [2/5] Removing old duplicate directories...
rmdir /S /Q docs 2>nul
rmdir /S /Q scripts 2>nul
rmdir /S /Q batch_scripts 2>nul
rmdir /S /Q txt 2>nul
rmdir /S /Q databases 2>nul
rmdir /S /Q grace-frontend 2>nul
echo   Done

echo.
echo [3/5] Moving grace_rebuild/backend to root...
xcopy /E /I /Y grace_rebuild\backend backend
echo   Done

echo.
echo [4/5] Moving other directories...
xcopy /E /I /Y grace_rebuild\docs docs
xcopy /E /I /Y grace_rebuild\scripts scripts
xcopy /E /I /Y grace_rebuild\batch_scripts batch_scripts
xcopy /E /I /Y grace_rebuild\txt txt
xcopy /E /I /Y grace_rebuild\tests tests
xcopy /E /I /Y grace_rebuild\cli cli
xcopy /E /I /Y grace_rebuild\config config
xcopy /E /I /Y grace_rebuild\databases databases
xcopy /E /I /Y grace_rebuild\grace-frontend frontend
xcopy /E /I /Y grace_rebuild\reports reports
echo   Done

echo.
echo [5/5] Moving key files...
copy /Y grace_rebuild\minimal_backend.py .
copy /Y grace_rebuild\metrics.db .
copy /Y grace_rebuild\*.bat . 2>nul
echo   Done

echo.
echo [6/6] Removing grace_rebuild folder...
rmdir /S /Q grace_rebuild
echo   Done

echo.
echo ================================================================================
echo CONSOLIDATION COMPLETE
echo ================================================================================
echo.
echo New structure:
echo   grace_2/
echo   ├── backend/          (Production code)
echo   ├── frontend/         (React UI)
echo   ├── cli/              (CLI tools)
echo   ├── scripts/          (Utilities)
echo   ├── docs/             (Documentation)
echo   ├── tests/            (Test suite)
echo   └── minimal_backend.py
echo.
echo Test it:
echo   py minimal_backend.py
echo.
pause
