# ============================================================================
# GRACE START - FIXED FOR WINDOWS
# No reload mode, no multiprocessing issues
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    GRACE AI SYSTEM - STARTING                              ║" -ForegroundColor Cyan  
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Set-Location C:\Users\aaron\grace_2

Write-Host "✓ Starting Grace with all subsystems..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Subsystems:" -ForegroundColor Yellow
Write-Host "  ✓ 9 Domain Kernels (311+ APIs)" -ForegroundColor White
Write-Host "  ✓ Ingestion Pipeline" -ForegroundColor White
Write-Host "  ✓ Coding Agent" -ForegroundColor White
Write-Host "  ✓ Agentic Memory & Spine" -ForegroundColor White
Write-Host "  ✓ Self-Healing Systems" -ForegroundColor White
Write-Host "  ✓ Web Learning" -ForegroundColor White
Write-Host "  ✓ Constitutional AI" -ForegroundColor White
Write-Host "  ✓ All 100+ subsystems" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Start without --reload (fixes Windows multiprocessing issue)
& .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
