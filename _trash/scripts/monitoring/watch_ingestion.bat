@echo off
cls
echo.
echo ========================================
echo Grace Knowledge Ingestion Monitor
echo ========================================
echo.
echo Watching for new knowledge ingestions...
echo Press Ctrl+C to stop
echo.
echo Visual log: logs\ingestion.html
echo Terminal log: logs\ingestion_visual.log
echo.
echo ----------------------------------------
echo.

:loop
type logs\ingestion_visual.log 2>nul | find "KNOWLEDGE INGESTION" | find /v /c "" >nul
if errorlevel 1 (
    echo Waiting for ingestions...
) else (
    echo.
    type logs\ingestion_visual.log | more
)

timeout /t 5 >nul
goto loop
