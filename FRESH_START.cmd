@echo off
cls
echo.
echo ====================================================================
echo GRACE - FRESH START (Kill All First)
echo ====================================================================
echo.
echo Killing all existing Grace processes...
echo.

python find_grace_process.py > temp_pids.txt 2>&1

echo Killing processes...
for /L %%p in (8000,1,8010) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p ^| findstr LISTENING 2^>nul') do (
        taskkill /PID %%a /F >nul 2>&1
    )
)

timeout /t 2 >nul

echo.
echo All processes killed. Starting Grace...
echo.
python serve.py
