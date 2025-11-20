@echo off
cls
echo.
echo ========================================
echo   GRACE E2E DIAGNOSTIC
echo ========================================
echo.

set BACKEND=http://localhost:8000
set RESULTS=0
set FAILURES=0

echo [TEST 1] Backend Health Check
curl -s %BACKEND%/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running
    set /a RESULTS+=1
) else (
    echo ❌ Backend is NOT running
    set /a FAILURES+=1
)

echo.
echo [TEST 2] Metrics API
curl -s %BACKEND%/api/metrics/summary | findstr /i "success" > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ /api/metrics/summary
    set /a RESULTS+=1
) else (
    echo ❌ /api/metrics/summary FAILED
    set /a FAILURES+=1
)

echo.
echo [TEST 3] Mission Control API
curl -s %BACKEND%/api/mission-control/missions | findstr /i "missions total" > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ /api/mission-control/missions
    set /a RESULTS+=1
) else (
    curl -s %BACKEND%/api/mission-control/missions | findstr /i "detail" > nul 2>&1
    if %errorlevel% equ 0 (
        echo ❌ /api/mission-control/missions - 404 Not Found
        set /a FAILURES+=1
    ) else (
        echo ⚠️  /api/mission-control/missions - Unknown response
        set /a FAILURES+=1
    )
)

echo.
echo [TEST 4] Self-Healing API
curl -s %BACKEND%/api/self-healing/stats | findstr /i "total_incidents" > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ /api/self-healing/stats
    set /a RESULTS+=1
) else (
    echo ❌ /api/self-healing/stats FAILED
    set /a FAILURES+=1
)

echo.
echo [TEST 5] Ingestion API
curl -s %BACKEND%/api/ingestion/stats | findstr /i "total_files" > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ /api/ingestion/stats
    set /a RESULTS+=1
) else (
    echo ❌ /api/ingestion/stats FAILED
    set /a FAILURES+=1
)

echo.
echo [TEST 6] Learning API
curl -s %BACKEND%/api/learning/status | findstr /i "system mode" > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ /api/learning/status
    set /a RESULTS+=1
) else (
    echo ❌ /api/learning/status FAILED
    set /a FAILURES+=1
)

echo.
echo [TEST 7] Snapshots API
curl -s %BACKEND%/api/snapshots/list | findstr /i "snapshots" > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ /api/snapshots/list
    set /a RESULTS+=1
) else (
    echo ❌ /api/snapshots/list FAILED
    set /a FAILURES+=1
)

echo.
echo [TEST 8] Memory Files API
curl -s %BACKEND%/api/memory/files/list > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ /api/memory/files/list
    set /a RESULTS+=1
) else (
    echo ❌ /api/memory/files/list FAILED
    set /a FAILURES+=1
)

echo.
echo [TEST 9] Mentor API
curl -s %BACKEND%/api/mentor/status > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ /api/mentor/status
    set /a RESULTS+=1
) else (
    echo ❌ /api/mentor/status FAILED
    set /a FAILURES+=1
)

echo.
echo ========================================
echo   DIAGNOSTIC SUMMARY
echo ========================================
echo.
echo Tests Passed: %RESULTS%/9
echo Tests Failed: %FAILURES%/9
echo.

if %FAILURES% equ 0 (
    echo ✅ ALL TESTS PASSED!
    echo.
    echo Your backend is fully connected.
    echo Refresh browser to see updates.
) else (
    echo ❌ SOME TESTS FAILED
    echo.
    echo Action Required:
    echo 1. Stop backend (Ctrl+C)
    echo 2. Run: python server.py
    echo 3. Run this diagnostic again
)

echo.
pause
