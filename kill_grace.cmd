@echo off
echo.
echo ====================================================================
echo KILLING ALL GRACE PROCESSES
echo ====================================================================
echo.

echo Finding Python processes using ports 8000-8100...
echo.

for /L %%p in (8000,1,8100) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p ^| findstr LISTENING') do (
        echo Found process using port %%p: PID %%a
        taskkill /PID %%a /F
    )
)

echo.
echo Killing any remaining Python processes named "serve.py"...
tasklist | findstr /I "python.exe" && (
    for /f "tokens=2" %%a in ('tasklist ^| findstr /I "python.exe"') do (
        echo Checking PID %%a...
    )
)

echo.
echo ====================================================================
echo CLEANUP COMPLETE
echo ====================================================================
echo.
echo All Grace processes should be stopped.
echo Ports 8000-8100 should now be free.
echo.
echo You can now start Grace:
echo   python serve.py
echo.
pause
