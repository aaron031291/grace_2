#!/usr/bin/env pwsh
# Grace Universal Installer - Works anywhere, installs everything

param(
    [string]$InstallPath = "$env:USERPROFILE\grace",
    [switch]$Global
)

Write-Host "🚀 Grace Universal Installer" -ForegroundColor Cyan
Write-Host "Installing to: $InstallPath" -ForegroundColor Yellow

# Create install directory
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null

# Check/Install Python
Write-Host "📦 Checking Python..." -ForegroundColor Yellow
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
    try {
        winget install Python.Python.3.11 --silent
        $env:PATH += ";$env:LOCALAPPDATA\Programs\Python\Python311;$env:LOCALAPPDATA\Programs\Python\Python311\Scripts"
        $pythonCmd = "python"
        Write-Host "✓ Python installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install Python. Please install manually from python.org" -ForegroundColor Red
        exit 1
    }
}

# Download/Clone Grace
Write-Host "📥 Getting Grace..." -ForegroundColor Yellow
Set-Location $InstallPath

if (Get-Command git -ErrorAction SilentlyContinue) {
    git clone https://github.com/yourusername/grace.git . 2>$null
} else {
    # Download as ZIP if no git
    $url = "https://github.com/yourusername/grace/archive/main.zip"
    Invoke-WebRequest -Uri $url -OutFile "grace.zip"
    Expand-Archive -Path "grace.zip" -DestinationPath "." -Force
    Move-Item "grace-main\*" "." -Force
    Remove-Item "grace-main", "grace.zip" -Recurse -Force
}

# Create virtual environment and install dependencies
Write-Host "🐍 Setting up Python environment..." -ForegroundColor Yellow
& $pythonCmd -m venv .venv
& ".venv\Scripts\Activate.ps1"
& $pythonCmd -m pip install --upgrade pip

# Find and install requirements
$requirementsFiles = @(
    "txt\requirements.txt",
    "backend\requirements.txt", 
    "requirements.txt"
)

$requirementsFound = $false
foreach ($reqFile in $requirementsFiles) {
    if (Test-Path $reqFile) {
        Write-Host "📦 Installing dependencies from $reqFile..." -ForegroundColor Yellow
        & $pythonCmd -m pip install -r $reqFile
        $requirementsFound = $true
        break
    }
}

if (-not $requirementsFound) {
    Write-Host "⚠️ No requirements.txt found. Installing core dependencies..." -ForegroundColor Yellow
    & $pythonCmd -m pip install fastapi uvicorn sqlalchemy aiosqlite pydantic httpx rich
}

# Create global launcher
$launcherContent = @"
#!/usr/bin/env pwsh
Set-Location '$InstallPath'
if (Test-Path '.venv\Scripts\Activate.ps1') {
    & '.venv\Scripts\Activate.ps1'
}
python -m backend.unified_grace_orchestrator `$args
"@

if ($Global) {
    $globalPath = "$env:ProgramFiles\Grace"
    New-Item -ItemType Directory -Path $globalPath -Force | Out-Null
    $launcherContent | Out-File "$globalPath\grace.ps1" -Encoding UTF8
    
    # Add to PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ($currentPath -notlike "*$globalPath*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$globalPath", "Machine")
    }
    Write-Host "✓ Grace installed globally. Run 'grace' from anywhere." -ForegroundColor Green
} else {
    $launcherContent | Out-File "$InstallPath\grace.ps1" -Encoding UTF8
    Write-Host "✓ Grace installed locally. Run from: $InstallPath\grace.ps1" -ForegroundColor Green
}

Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host "Test with: grace --help" -ForegroundColor Yellow
