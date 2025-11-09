# Grace Startup Script - PowerShell
# Starts Grace backend with all systems integrated

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Grace Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "Starting Grace with all systems..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Grace will start with:" -ForegroundColor Green
Write-Host "  ✓ Web Learning (83+ domains)" -ForegroundColor Green
Write-Host "  ✓ GitHub Mining" -ForegroundColor Green
Write-Host "  ✓ YouTube Learning" -ForegroundColor Green
Write-Host "  ✓ Reddit Learning (38+ subreddits)" -ForegroundColor Green
Write-Host "  ✓ API Discovery" -ForegroundColor Green
Write-Host "  ✓ Amp API (Last Resort + Verification)" -ForegroundColor Green
Write-Host "  ✓ Visual Ingestion Logs" -ForegroundColor Green
Write-Host "  ✓ ML/DL Reliability Learning" -ForegroundColor Green
Write-Host "  ✓ Complete Governance" -ForegroundColor Green
Write-Host ""
Write-Host "Backend will be available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host "  http://localhost:8000/docs (API Documentation)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
}
catch {
    Write-Host ""
    Write-Host "Error starting Grace: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Write-Host "Grace stopped." -ForegroundColor Yellow
Write-Host ""
