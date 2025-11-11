#!/usr/bin/env pwsh
# Grace Universal Script - Install, Start, Stop, Status - Everything in one

param(
    [string]$Action = "start",
    [string]$InstallPath = "$env:USERPROFILE\grace_2",
    [switch]$Force,
    [switch]$Global
)

$ErrorActionPreference = "Stop"

function Write-GraceHeader {
    Write-Host ""
    Write-Host "🚀 GRACE UNIVERSAL SCRIPT" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Gray
}

function Install-Grace {
    Write-Host "📦 Installing Grace..." -ForegroundColor Yellow
    
    # Check/Install Python
    $pythonCmd = $null
    $pythonCommands = @("python", "python3", "py")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>$null
            if ($version -and $LASTEXITCODE -eq 0) {
                $pythonCmd = $cmd
                Write-Host "✓ Found Python: $version" -ForegroundColor Green
                break
            }
        } catch { continue }
    }
    
    if (-not $pythonCmd) {
        Write-Host "Installing Python..." -ForegroundColor Yellow
        winget install Python.Python.3.11 --silent
        $pythonCmd = "python"
    }
    
    # Create install directory if it doesn't exist
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Host "✓ Created directory: $InstallPath" -ForegroundColor Green
    }
    
    Set-Location $InstallPath
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path ".venv")) {
        Write-Host "🐍 Creating virtual environment..." -ForegroundColor Yellow
        & $pythonCmd -m venv .venv
        & ".venv\Scripts\Activate.ps1"
        & $pythonCmd -m pip install --upgrade pip
        
        # Install core dependencies
        Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
        & $pythonCmd -m pip install fastapi uvicorn sqlalchemy aiosqlite pydantic httpx rich psutil aiohttp
    }
    
    # Create the grace launcher
    $launcherContent = @"
#!/usr/bin/env pwsh
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}
python -m backend.unified_grace_orchestrator `$args
"@
    
    $launcherContent | Out-File "grace.ps1" -Encoding UTF8
    
    Write-Host "✅ Grace installation complete!" -ForegroundColor Green
    Write-Host "Location: $InstallPath" -ForegroundColor Yellow
}

function Start-Grace {
    if (-not (Test-Path "grace.ps1")) {
        Write-Host "❌ Grace not found. Installing first..." -ForegroundColor Red
        Install-Grace
    }
    
    Write-Host "🚀 Starting Grace..." -ForegroundColor Green
    & ".\grace.ps1"
}

function Stop-Grace {
    Write-Host "🛑 Stopping Grace..." -ForegroundColor Yellow
    if (Test-Path "grace.ps1") {
        & ".\grace.ps1" --stop $(if ($Force) { "--force" })
    } else {
        Write-Host "❌ Grace not found at current location" -ForegroundColor Red
    }
}

function Show-Status {
    Write-Host "📊 Grace Status..." -ForegroundColor Yellow
    if (Test-Path "grace.ps1") {
        & ".\grace.ps1" --status
    } else {
        Write-Host "❌ Grace not found at current location" -ForegroundColor Red
    }
}

function Show-Help {
    Write-Host @"
Grace Universal Script - One script for everything

USAGE:
  .\grace-universal.ps1 [action] [options]

ACTIONS:
  install     Install Grace (auto-detects Python, creates venv)
  start       Start Grace (installs if needed) - DEFAULT
  stop        Stop Grace services
  status      Show Grace status
  help        Show this help

OPTIONS:
  -InstallPath    Custom install path (default: $env:USERPROFILE\grace_2)
  -Force          Force stop services
  -Global         Install globally (requires admin)

EXAMPLES:
  .\grace-universal.ps1                    # Start Grace (install if needed)
  .\grace-universal.ps1 install            # Just install
  .\grace-universal.ps1 stop               # Stop services
  .\grace-universal.ps1 stop -Force        # Force stop
  .\grace-universal.ps1 status             # Show status

QUICK START:
  1. Download this script
  2. Run: .\grace-universal.ps1
  3. Access: http://localhost:5173

"@ -ForegroundColor White
}

# Main execution
Write-GraceHeader

switch ($Action.ToLower()) {
    "install" { 
        Set-Location $InstallPath
        Install-Grace 
    }
    "start" { 
        Set-Location $InstallPath
        Start-Grace 
    }
    "stop" { 
        Set-Location $InstallPath
        Stop-Grace 
    }
    "status" { 
        Set-Location $InstallPath
        Show-Status 
    }
    "help" { Show-Help }
    default { 
        Set-Location $InstallPath
        Start-Grace 
    }
}