# Build Grace Docker Images - PowerShell

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Building Grace Docker Images" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Build backend
Write-Host "→ Building Grace Backend..." -ForegroundColor Yellow
docker build -t grace-backend:latest -f Dockerfile .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Backend image built successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Backend build failed" -ForegroundColor Red
    exit 1
}

# Build frontend (if Dockerfile exists)
if (Test-Path "frontend\Dockerfile") {
    Write-Host ""
    Write-Host "→ Building Grace Frontend..." -ForegroundColor Yellow
    docker build -t grace-frontend:latest -f frontend\Dockerfile ./frontend
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frontend image built successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Frontend build failed" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Docker images ready!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start Grace:" -ForegroundColor White
Write-Host "  docker-compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or with Kubernetes:" -ForegroundColor White
Write-Host "  kubectl apply -f kubernetes/" -ForegroundColor Cyan
Write-Host ""
