@echo off
cls
echo.
echo ====================================================================
echo GRACE - KILL AND RESTART
echo ====================================================================
echo.
echo This will:
echo   1. Kill all Grace processes
echo   2. Free up all ports
echo   3. Restart Grace
echo.
pause
echo.
echo Step 1: Killing processes...
python kill_grace.py
echo.
echo Step 2: Starting Grace...
echo.
python serve.py
