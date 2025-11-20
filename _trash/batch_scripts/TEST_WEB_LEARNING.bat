@echo off
echo ====================================================================
echo Testing Grace Web Learning Capabilities
echo ====================================================================
echo.

REM Wait a moment for Grace to be fully started
timeout /t 2 /nobreak >nul

echo Testing web learning stats...
curl -s http://localhost:8000/api/web-learning/stats
echo.
echo.

echo ====================================================================
echo Test complete! If you saw JSON output above, web learning is working.
echo ====================================================================
echo.
echo Next steps:
echo   - Search: POST http://localhost:8000/api/web-learning/search
echo   - Learn: POST http://localhost:8000/api/web-learning/learn-topic
echo   - Explore: GET http://localhost:8000/api/web-learning/explore/programming
echo.

pause
