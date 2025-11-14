@echo off
REM Start Grace Frontend

echo ================================================================================
echo GRACE FRONTEND - STARTING
echo ================================================================================
echo.

cd frontend

echo Starting Grace frontend...
echo Frontend will run on: http://localhost:5173
echo.
echo Available pages:
echo   - Control Center:  http://localhost:5173/control
echo   - Activity Monitor: http://localhost:5173/activity
echo   - ML/AI Integrations: http://localhost:5173/integrations/ml-apis
echo.
echo Press Ctrl+C to stop
echo.
echo ================================================================================
echo.

npm run dev

pause
