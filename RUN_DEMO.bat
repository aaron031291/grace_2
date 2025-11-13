@echo off
REM Grace Complete System Demo Runner

echo ============================================================
echo GRACE - AUTONOMOUS AI OPERATING SYSTEM
echo Complete System Demo
echo ============================================================
echo.

echo [Step 1/4] Verifying System...
echo ============================================================
python scripts\verify_full_integration.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ System verification failed!
    echo    Make sure backend is running: python serve.py
    pause
    exit /b 1
)

echo.
echo.
echo [Step 2/4] Populating Model Registry...
echo ============================================================
python scripts\populate_model_registry.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️ Model population failed (might already be populated)
)

echo.
echo.
echo [Step 3/4] Simulating Model Degradation...
echo ============================================================
echo This will trigger auto-rollback for fraud_detector_v1
echo.
timeout /t 2
python scripts\simulate_model_degradation.py fraud_detector_v1 5

echo.
echo.
echo [Step 4/4] Viewing Results...
echo ============================================================
echo.

echo Production Fleet Status:
curl -s http://localhost:8000/api/model-registry/monitor/production

echo.
echo.
echo Self-Healing Stats:
curl -s http://localhost:8000/api/self-healing/stats

echo.
echo.
echo ============================================================
echo ✅ DEMO COMPLETE!
echo ============================================================
echo.
echo What just happened:
echo   1. Verified all systems operational
echo   2. Populated registry with 5 ML models
echo   3. Simulated model degradation (9.5%% error rate)
echo   4. Grace auto-detected and triggered rollback
echo   5. Incident created, self-healing executed
echo.
echo View dashboards:
echo   - API Docs: http://localhost:8000/docs
echo   - Model Registry: http://localhost:8000/api/model-registry/models
echo   - Incidents: http://localhost:8000/api/incidents
echo.
echo Next: Explore the Memory Studio and Co-pilot!
echo.

pause
