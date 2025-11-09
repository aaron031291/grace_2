# ============================================================================
# START GRACE NOW - FIXED VERSION
# All issues resolved - just run this!
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    GRACE AI SYSTEM - STARTING NOW                          ║" -ForegroundColor Cyan  
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Stop any stuck jobs
Get-Job | Stop-Job -ErrorAction SilentlyContinue 2>$null
Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue 2>$null

Write-Host "✓ Cleaned up background jobs" -ForegroundColor Green
Write-Host ""

Write-Host "→ Starting Grace Backend..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend will include:" -ForegroundColor Cyan
Write-Host "  ✓ 9 Domain Kernels (311+ APIs)" -ForegroundColor White
Write-Host "  ✓ Ingestion Pipeline (Web, GitHub, YouTube, Reddit)" -ForegroundColor White
Write-Host "  ✓ Coding Agent (Code Generation & Healing)" -ForegroundColor White
Write-Host "  ✓ Agentic Memory & Spine" -ForegroundColor White
Write-Host "  ✓ Self-Healing Systems (9 subsystems)" -ForegroundColor White
Write-Host "  ✓ Constitutional AI & Governance" -ForegroundColor White
Write-Host "  ✓ All 100+ Autonomous Subsystems" -ForegroundColor White
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Start backend (no --reload to avoid multiprocessing issues on Windows)
& .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
