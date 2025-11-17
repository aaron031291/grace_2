@echo off
echo ========================================
echo   Grace Console - Automated Setup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Installing dependencies...
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: npm install failed
    pause
    exit /b 1
)
echo.

echo [2/4] Checking TypeScript compilation...
call npm run type-check
if errorlevel 1 (
    echo.
    echo WARNING: Type check has errors, but build may still work
    echo.
)

echo [3/4] Testing build...
call npm run build
if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo.

echo [4/4] Setup complete!
echo.
echo ========================================
echo   ✅ Grace Console is ready!
echo ========================================
echo.
echo To start the console:
echo   npm run dev
echo.
echo Then open: http://localhost:5173
echo.
echo Features available:
echo   💬 Chat (unified with /ask and /rag commands)
echo   📊 Workspace (dynamic tabs)
echo   🧠 Memory (upload file/text/voice)
echo   ⚖️ Governance (approvals and audit)
echo   🔧 MCP Tools (protocol interface)
echo   🔐 Vault (secure credentials)
echo   🎯 Tasks (mission Kanban)
echo   📋 Logs (real-time monitoring)
echo.
echo Documentation: See frontend/INDEX.md
echo.

pause
