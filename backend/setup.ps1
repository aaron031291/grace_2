# Grace 3.0 - Quick Setup Script
# Run this script to set up the backend environment

Write-Host "🚀 Grace 3.0 Backend Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is installed
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version
    Write-Host "✅ PostgreSQL found: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PostgreSQL not found. Please install it first." -ForegroundColor Red
    Write-Host "   Download from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

# Check if Redis is installed
Write-Host "Checking Redis..." -ForegroundColor Yellow
try {
    $redisCheck = Get-Process redis-server -ErrorAction SilentlyContinue
    if ($redisCheck) {
        Write-Host "✅ Redis is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Redis not running. Starting Redis..." -ForegroundColor Yellow
        Start-Process redis-server -WindowStyle Hidden
        Start-Sleep -Seconds 2
        Write-Host "✅ Redis started" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Redis not found. Please install it first." -ForegroundColor Red
    Write-Host "   Download from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "Setting up Python environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env and set your DATABASE_PASSWORD" -ForegroundColor Yellow
    Write-Host ""
    $password = Read-Host "Enter PostgreSQL password (or press Enter to skip)"
    if ($password) {
        (Get-Content .env) -replace 'DATABASE_PASSWORD=your_password_here', "DATABASE_PASSWORD=$password" | Set-Content .env
        Write-Host "✅ Password updated in .env" -ForegroundColor Green
    }
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create database
Write-Host "Setting up database..." -ForegroundColor Yellow
$dbExists = psql -U postgres -lqt | Select-String -Pattern "grace_memory"
if (!$dbExists) {
    Write-Host "Creating database 'grace_memory'..." -ForegroundColor Yellow
    psql -U postgres -c "CREATE DATABASE grace_memory;"
    Write-Host "✅ Database created" -ForegroundColor Green
} else {
    Write-Host "✅ Database 'grace_memory' already exists" -ForegroundColor Green
}

# Run schema
Write-Host "Initializing database schema..." -ForegroundColor Yellow
psql -U postgres -d grace_memory -f database/schema.sql -q
Write-Host "✅ Schema initialized" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "  python server.py" -ForegroundColor Cyan
Write-Host ""
