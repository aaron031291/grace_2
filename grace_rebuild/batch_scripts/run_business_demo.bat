@echo off
echo ========================================
echo Grace AI - Business Automation Demo
echo ========================================
echo.

cd /d "%~dp0"

echo Running AI Consulting Automation Demo...
echo.

python demo_business_automation.py

echo.
echo ========================================
echo Demo Complete!
echo ========================================
echo.
echo To test via API:
echo   1. Start backend: start_backend.bat
echo   2. Test endpoints:
echo      curl -X POST http://localhost:8000/api/business/leads -H "Content-Type: application/json" -d "{...}"
echo      curl http://localhost:8000/api/business/pipeline
echo.

pause
