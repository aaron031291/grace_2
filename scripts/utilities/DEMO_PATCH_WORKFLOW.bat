@echo off
echo ============================================
echo  Self-Healing to Coding Agent Demo
echo ============================================
echo.

echo Step 1: Check system health...
curl -s http://localhost:8000/health | python -m json.tool | findstr "healthy\|log_watcher\|event_bus"
echo.
pause

echo.
echo Step 2: Trigger a playbook that DOES NOT need code patch...
curl -s -X POST http://localhost:8000/patches/trigger -H "Content-Type: application/json" -d "{\"description\":\"Database connection lost\",\"error_type\":\"database_connection\"}"
echo.
pause

echo.
echo Step 3: Trigger a playbook that DOES need code patch...
curl -s -X POST http://localhost:8000/patches/trigger -H "Content-Type: application/json" -d "{\"description\":\"Pipeline validation timeout\",\"error_type\":\"pipeline_timeout\"}" | python -m json.tool
echo.
pause

echo.
echo Step 4: Check work orders (should show the escalated patch)...
curl -s http://localhost:8000/patches/work-orders | python -m json.tool
echo.
pause

echo.
echo Step 5: Check playbook runs...
curl -s http://localhost:8000/patches/runs | python -m json.tool
echo.
pause

echo.
echo Step 6: Get patch statistics...
curl -s http://localhost:8000/patches/stats | python -m json.tool
echo.
pause

echo.
echo Step 7: Check recent events...
curl -s http://localhost:8000/events/recent?limit=10 | python -m json.tool
echo.
pause

echo.
echo ============================================
echo Demo Complete!
echo.
echo The workflow demonstrates:
echo  1. Error detection
echo  2. Playbook selection
echo  3. Conditional escalation to coding agent
echo  4. Work order tracking
echo  5. Status synchronization
echo ============================================
pause
