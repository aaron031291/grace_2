@echo off
REM Monitor Book Upload Progress

echo ============================================================
echo GRACE - BOOK INGESTION MONITOR
echo ============================================================
echo.

:LOOP

echo [%TIME%] Checking system status...
echo.

echo --- Self-Healing Stats ---
curl -s http://localhost:8000/api/self-healing/stats
echo.
echo.

echo --- Model Registry Status ---
curl -s http://localhost:8000/api/model-registry/stats
echo.
echo.

echo --- Librarian Flashcards ---
curl -s http://localhost:8000/api/librarian/flashcards
echo.
echo.

echo --- System Health ---
curl -s http://localhost:8000/health
echo.
echo.

echo ============================================================
echo Press Ctrl+C to stop monitoring
echo Refreshing in 10 seconds...
echo ============================================================
timeout /t 10 /nobreak

cls
goto LOOP
