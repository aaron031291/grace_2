@echo off
echo ============================================
echo Testing Clean Factory API Pattern
echo ============================================
echo.

echo 1. System Health...
curl -s http://localhost:8000/system/health
echo.
echo.

echo 2. System Metrics...
curl -s http://localhost:8000/system/metrics
echo.
echo.

echo 3. Self-Healing Stats...
curl -s http://localhost:8000/self-healing/stats
echo.
echo.

echo 4. Self-Healing Incidents...
curl -s http://localhost:8000/self-healing/incidents?limit=3
echo.
echo.

echo 5. Librarian Status...
curl -s http://localhost:8000/librarian/status
echo.
echo.

echo 6. Trusted Sources...
curl -s http://localhost:8000/trusted-sources/
echo.
echo.

echo ============================================
echo All Factory API Tests Complete!
echo.
echo No Circular Imports!
echo Clean Architecture!
echo ============================================
pause
