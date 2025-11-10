# Verify GitHub Token Handling Fix
# Quick verification that all changes are working

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "GitHub Token Handling - Verification Script" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check files exist
Write-Host "📁 Checking Modified Files:" -ForegroundColor Yellow
Write-Host ""

$files = @(
    "backend\secrets_vault.py",
    "backend\github_knowledge_miner.py",
    ".env.example",
    "test_github_token.py",
    "test_with_token.py",
    "docs\GITHUB_TOKEN_SETUP.md",
    "GITHUB_TOKEN_CHANGES.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (MISSING)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📝 Key Changes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. secrets_vault.py - Added get_secret() method" -ForegroundColor White
Write-Host "  2. github_knowledge_miner.py - Enhanced token loading" -ForegroundColor White
Write-Host "  3. github_knowledge_miner.py - Added rate limit checking" -ForegroundColor White
Write-Host "  4. .env.example - Added token documentation" -ForegroundColor White
Write-Host ""

# Check .env exists
Write-Host "🔧 Environment Configuration:" -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".env") {
    Write-Host "  ✅ .env file exists" -ForegroundColor Green
    
    # Check if GITHUB_TOKEN is set (without showing value)
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "GITHUB_TOKEN=") {
        Write-Host "  ✅ GITHUB_TOKEN configured in .env" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  GITHUB_TOKEN not set in .env (will use anonymous mode)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️  .env file not found (using environment variables only)" -ForegroundColor Yellow
    Write-Host "     Run: cp .env.example .env" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🧪 Running Tests:" -ForegroundColor Yellow
Write-Host ""

# Run test
Write-Host "  Testing token loading mechanism..." -ForegroundColor White
Write-Host ""

& .venv\Scripts\python.exe test_github_token.py 2>&1 | Out-String | Write-Host

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Verification Complete!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Read docs/GITHUB_TOKEN_SETUP.md for setup instructions" -ForegroundColor Cyan
Write-Host "📋 Read GITHUB_TOKEN_CHANGES.md for detailed change list" -ForegroundColor Cyan
Write-Host ""
