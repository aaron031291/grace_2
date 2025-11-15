@echo off
cls
echo.
echo ====================================================================
echo GRACE - AUTO PORT MODE
echo ====================================================================
echo.
echo This will automatically find an available port and start Grace.
echo.
echo If port 8001 is busy, it will try 8002, 8003, etc.
echo.
pause
echo.
python start_grace_auto_port.py
