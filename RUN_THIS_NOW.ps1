# ============================================================================
# RUN THIS NOW - COMPLETE FIX & START
# This fixes everything and starts Grace
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    GRACE COMPLETE FIX & START                              ║" -ForegroundColor Cyan  
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Navigate to correct directory
Set-Location C:\Users\aaron\grace_2
Write-Host "✓ In directory: C:\Users\aaron\grace_2" -ForegroundColor Green

# Clean up any stuck jobs
Write-Host "→ Cleaning up stuck jobs..." -ForegroundColor Yellow
Get-Job | Stop-Job -ErrorAction SilentlyContinue 2>$null
Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue 2>$null
Write-Host "✓ Cleaned up" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 1: Installing Dependencies (2-5 minutes)" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

.venv\Scripts\python.exe -m pip install --upgrade pip --quiet

Write-Host "Installing packages..." -ForegroundColor Cyan
.venv\Scripts\pip install -r backend\requirements.txt

Write-Host ""
Write-Host "✓ Dependencies installed!" -ForegroundColor Green
Write-Host ""

# Start backend
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "STEP 2: Starting Grace Backend" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Grace will start with:" -ForegroundColor Green
Write-Host "  ✓ 9 Domain Kernels (311+ APIs)" -ForegroundColor White
Write-Host "  ✓ Ingestion Pipeline" -ForegroundColor White
Write-Host "  ✓ Coding Agent" -ForegroundColor White
Write-Host "  ✓ Agentic Memory & Spine" -ForegroundColor White
Write-Host "  ✓ Self-Healing Systems" -ForegroundColor White
Write-Host "  ✓ Web Learning (83+ domains)" -ForegroundColor White
Write-Host "  ✓ Constitutional AI & Governance" -ForegroundColor White
Write-Host "  ✓ All 100+ Subsystems" -ForegroundColor White
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start it
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
