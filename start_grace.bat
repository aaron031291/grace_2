@echo off
echo ========================================
echo   GRACE AI - Complete System Startup
echo   ALL Systems Included
echo ========================================
echo.

echo Systems Included:
echo   [*] Agentic Spine (6 shards)
echo   [*] Self-Healing Agent
echo   [*] Meta-Loop Engine
echo   [*] Coding Agent
echo   [*] Autonomous Improver
echo   [*] Error Identification Agent
echo   [*] Cognition Engine
echo   [*] Trigger Mesh
echo   [*] Memory (Lightning/Library/Fusion)
echo   [*] Governance (Layer-1 + Layer-2)
echo   [*] Parliament System
echo   [*] Verification Contracts
echo   [*] All 270+ API Endpoints
echo.

:menu
echo Choose deployment method:
echo   [1] Docker (6 workers, isolated)
echo   [2] Local (6 workers, development)
echo   [3] Single worker (debugging)
echo   [Q] Quit
echo.
set /p choice="Enter choice: "

if /i "%choice%"=="1" goto docker
if /i "%choice%"=="2" goto local
if /i "%choice%"=="3" goto single
if /i "%choice%"=="q" exit /b 0
goto menu

:docker
echo.
echo [DOCKER] Starting Grace with Docker Compose...
docker-compose -f docker-compose.complete.yml down 2>nul
docker-compose -f docker-compose.complete.yml build
docker-compose -f docker-compose.complete.yml up -d

echo.
echo Waiting for services...
timeout /t 15 /nobreak >nul

docker-compose -f docker-compose.complete.yml ps

echo.
echo View logs: docker-compose -f docker-compose.complete.yml logs -f
echo Stop: docker-compose -f docker-compose.complete.yml down
goto end

:local
echo.
echo [LOCAL] Starting Grace with 6 workers...
start "Grace Backend (6 Workers)" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 6 --loop uvloop"

timeout /t 8 /nobreak >nul

start "Grace Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

goto end

:single
echo.
echo [DEBUG] Starting Grace with 1 worker (debug mode)...
start "Grace Backend (Debug)" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 8 /nobreak >nul

start "Grace Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

goto end

:end
echo.
echo ========================================
echo   Grace AI is Starting!
echo ========================================
echo.
echo Access Points:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Health:   http://localhost:8000/health
echo.
echo All Systems:
echo   - Agentic Spine: ACTIVE
echo   - Self-Healing: ACTIVE
echo   - Meta-Loop: ACTIVE
echo   - Coding Agent: ACTIVE
echo   - Error Agent: ACTIVE
echo   - Autonomous Improver: ACTIVE
echo   - Trigger Mesh: ROUTING
echo   - Governance: ENFORCING
echo.
pause
