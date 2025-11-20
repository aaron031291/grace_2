@echo off
echo Testing Comprehensive API Endpoints
echo =====================================
echo.

echo 1. Testing Self-Healing Stats...
curl -s http://localhost:8000/api/self-healing/stats
echo.
echo.

echo 2. Testing Immutable Logs...
curl -s http://localhost:8000/api/librarian/logs/immutable?limit=5
echo.
echo.

echo 3. Testing Log Tail...
curl -s http://localhost:8000/api/librarian/logs/tail?lines=10
echo.
echo.

echo 4. Testing System Health...
curl -s http://localhost:8000/api/system/health
echo.
echo.

echo 5. Testing Comprehensive Metrics...
curl -s http://localhost:8000/api/metrics/comprehensive
echo.
echo.

echo =====================================
echo All tests complete!
echo.
pause
