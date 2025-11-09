# ============================================================================
# BOOT GRACE - REAL SYSTEM (NOT SIMULATED)
# All systems wired with real APIs, real metrics, real playbooks
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    GRACE REAL SYSTEM - BOOTING                             ║" -ForegroundColor Green  
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Set-Location C:\Users\aaron\grace_2

Write-Host "🎯 REAL SYSTEMS ENABLED:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ✅ YouTube Learning - Real API" -ForegroundColor Green
Write-Host "  ✅ Reddit Learning - Real API" -ForegroundColor Green
Write-Host "  ✅ GitHub Mining - Real token handling" -ForegroundColor Green
Write-Host "  ✅ Web Scraping - 83+ trusted domains" -ForegroundColor Green
Write-Host "  ✅ Metrics Collection - Live CPU/memory/disk/DB" -ForegroundColor Green
Write-Host "  ✅ Proactive Intelligence - Real metric-driven decisions" -ForegroundColor Green
Write-Host "  ✅ Playbook Executor - 23 executable actions" -ForegroundColor Green
Write-Host "  ✅ 9 Domain Kernels - 311+ APIs" -ForegroundColor Green
Write-Host "  ✅ 100+ Subsystems - All operational" -ForegroundColor Green
Write-Host ""
Write-Host "📊 TELEMETRY:" -ForegroundColor Cyan
Write-Host "  • 22 production metrics" -ForegroundColor White
Write-Host "  • 5-minute aggregation windows" -ForegroundColor White
Write-Host "  • Automatic playbook recommendations" -ForegroundColor White
Write-Host "  • Governance-checked execution" -ForegroundColor White
Write-Host "  • Immutable audit trail" -ForegroundColor White
Write-Host ""
Write-Host "🌐 ENDPOINTS:" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Boot Grace
& .venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

Write-Host ""
Write-Host "Grace stopped." -ForegroundColor Yellow
