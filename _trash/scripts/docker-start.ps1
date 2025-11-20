# Start Grace with Docker Compose - PowerShell

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Starting Grace with Docker Compose" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠ .env file not found, creating from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env created - Please add your AMP_API_KEY" -ForegroundColor Green
    Write-Host ""
}

# Start services
Write-Host "→ Starting all Grace services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Grace services started!" -ForegroundColor Green
    Write-Host ""
    
    # Wait for services
    Write-Host "→ Waiting for services to be healthy..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Show status
    Write-Host ""
    docker-compose ps
    
    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "Grace is Running!" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Access Grace:" -ForegroundColor Cyan
    Write-Host "  • Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "  • API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  • Frontend: http://localhost:5173" -ForegroundColor White
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Cyan
    Write-Host "  docker-compose logs -f grace-backend" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop:" -ForegroundColor Cyan
    Write-Host "  docker-compose down" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "✗ Failed to start services" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs with:" -ForegroundColor Yellow
    Write-Host "  docker-compose logs" -ForegroundColor White
    Write-Host ""
}
