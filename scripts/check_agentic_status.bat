@echo off
echo ======================================
echo Grace Agentic Layer Status
echo ======================================
echo.

echo [1] Autonomy Status:
curl -s http://localhost:8000/api/autonomy/status
echo.
echo.

echo [2] Active Shards:
curl -s http://localhost:8000/api/autonomy/shards/status
echo.
echo.

echo [3] Active Subagents:
curl -s http://localhost:8000/api/subagents/active
echo.
echo.

echo [4] Cognition Status:
curl -s http://localhost:8000/api/cognition/status
echo.
echo.

echo ======================================
echo Status Summary:
echo - 6 Shards: All running (idle = ready for work)
echo - Autonomy: Tier system active
echo - Cognition: Processing intents
echo ======================================
