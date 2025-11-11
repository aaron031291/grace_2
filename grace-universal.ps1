#!/usr/bin/env pwsh
# Grace Universal Script - Install, Start, Stop, Status - Everything in one

param(
    [string]$Action = "start",
    [string]$InstallPath = "$env:USERPROFILE\grace_2",
    [string]$Environment = "dev",
    [string]$Profile = "native",
    [switch]$Force,
    [switch]$Global,
    [switch]$SafeMode,
    [switch]$DryRun,
    [switch]$Verbose,
    [int]$Timeout = 60
)

$ErrorActionPreference = "Stop"

# Create logs directory
$LogsDir = Join-Path $InstallPath "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}
$LogFile = Join-Path $LogsDir "boot.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    if ($Verbose) { Write-Host $logEntry -ForegroundColor Gray }
}

function Write-GraceHeader {
    Write-Host ""
    Write-Host "🚀 GRACE UNIVERSAL SCRIPT" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Gray
    Write-Log "Grace Universal Script started - Action: $Action, Environment: $Environment, Profile: $Profile"
}

function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-WithWinget {
    param([string]$Package, [string]$Name)
    
    try {
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            Write-Host "❌ Winget not available. Please install $Name manually or run as administrator." -ForegroundColor Red
            Write-Log "Winget not available for $Name installation" "ERROR"
            return $false
        }
        
        Write-Host "Installing $Name..." -ForegroundColor Yellow
        Write-Log "Installing $Name via winget: $Package"
        
        $result = & winget install $Package --silent --accept-package-agreements --accept-source-agreements 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $Name installed successfully" -ForegroundColor Green
            Write-Log "$Name installed successfully"
            return $true
        } else {
            Write-Host "⚠️ $Name installation may have failed. Exit code: $LASTEXITCODE" -ForegroundColor Yellow
            Write-Log "$Name installation failed with exit code: $LASTEXITCODE" "WARN"
            return $false
        }
    } catch {
        Write-Host "❌ Failed to install $Name`: $_" -ForegroundColor Red
        Write-Log "Exception installing $Name: $_" "ERROR"
        return $false
    }
}

function Install-Grace {
    Write-Host "📦 Installing Grace..." -ForegroundColor Yellow
    Write-Log "Starting Grace installation"
    
    # Check admin rights for winget
    if (-not (Test-AdminRights)) {
        Write-Host "⚠️ Running without admin rights. Some installations may fail." -ForegroundColor Yellow
        Write-Log "Running without admin rights" "WARN"
    }
    
    # LESSON 1: Always check multiple Python commands and handle installation properly
    $pythonCmd = $null
    $pythonCommands = @("python", "python3", "py")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>$null
            if ($version -and $LASTEXITCODE -eq 0) {
                $pythonCmd = $cmd
                Write-Host "✓ Found Python: $version" -ForegroundColor Green
                Write-Log "Found Python: $version using command: $cmd"
                break
            }
        } catch { 
            Write-Log "Python command '$cmd' not found or failed" "DEBUG"
            continue 
        }
    }
    
    if (-not $pythonCmd) {
        Write-Log "Python not found, attempting installation"
        if (-not (Install-WithWinget "Python.Python.3.11" "Python")) {
            Write-Host "❌ Python installation failed. Please install Python 3.11+ manually." -ForegroundColor Red
            return $false
        }
        # LESSON 2: Refresh PATH after Python installation
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        $pythonCmd = "python"
    }
    
    # Check/Install Node.js for frontend
    $nodeCmd = $null
    try {
        $nodeVersion = & node --version 2>$null
        if ($nodeVersion -and $LASTEXITCODE -eq 0) {
            $nodeCmd = "node"
            Write-Host "✓ Found Node.js: $nodeVersion" -ForegroundColor Green
            Write-Log "Found Node.js: $nodeVersion"
        }
    } catch { 
        Write-Log "Node.js not found" "DEBUG"
    }
    
    if (-not $nodeCmd) {
        Write-Log "Node.js not found, attempting installation"
        if (-not (Install-WithWinget "OpenJS.NodeJS" "Node.js")) {
            Write-Host "⚠️ Node.js installation failed. Frontend may not work." -ForegroundColor Yellow
        } else {
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            $nodeCmd = "node"
        }
    }
    
    # Create install directory if it doesn't exist
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Host "✓ Created directory: $InstallPath" -ForegroundColor Green
        Write-Log "Created install directory: $InstallPath"
    }
    
    Set-Location $InstallPath
    
    # LESSON 3: Handle virtual environment creation properly
    if (-not (Test-Path ".venv")) {
        Write-Host "🐍 Creating virtual environment..." -ForegroundColor Yellow
        Write-Log "Creating virtual environment"
        
        try {
            & $pythonCmd -m venv .venv
            Write-Log "Virtual environment created successfully"
        } catch {
            Write-Host "❌ Failed to create virtual environment: $_" -ForegroundColor Red
            Write-Log "Failed to create virtual environment: $_" "ERROR"
            return $false
        }
        
        # LESSON 4: Always activate venv before installing packages
        $venvPython = Join-Path $InstallPath ".venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            Write-Log "Using venv Python: $venvPython"
            & $venvPython -m pip install --upgrade pip
            
            # LESSON 5: Install dependencies from requirements.txt if exists, fallback to core deps
            $requirementsFiles = @("txt\requirements.txt", "backend\requirements.txt", "requirements.txt")
            $requirementsFound = $false
            
            foreach ($reqFile in $requirementsFiles) {
                if (Test-Path $reqFile) {
                    Write-Host "📦 Installing dependencies from $reqFile..." -ForegroundColor Yellow
                    Write-Log "Installing dependencies from $reqFile"
                    try {
                        & $venvPython -m pip install -r $reqFile
                        $requirementsFound = $true
                        Write-Log "Dependencies installed from $reqFile"
                        break
                    } catch {
                        Write-Host "⚠️ Failed to install from $reqFile`: $_" -ForegroundColor Yellow
                        Write-Log "Failed to install from $reqFile`: $_" "WARN"
                    }
                }
            }
            
            if (-not $requirementsFound) {
                Write-Host "📦 Installing core backend dependencies..." -ForegroundColor Yellow
                Write-Log "Installing core backend dependencies"
                try {
                    & $venvPython -m pip install fastapi uvicorn sqlalchemy aiosqlite pydantic httpx rich psutil aiohttp
                    Write-Log "Core dependencies installed successfully"
                } catch {
                    Write-Host "❌ Failed to install core dependencies: $_" -ForegroundColor Red
                    Write-Log "Failed to install core dependencies: $_" "ERROR"
                    return $false
                }
            }
        } else {
            Write-Host "❌ Virtual environment Python not found" -ForegroundColor Red
            Write-Log "Virtual environment Python not found" "ERROR"
            return $false
        }
    }
    
    # Create basic backend structure
    Write-Host "🏗️ Setting up backend structure..." -ForegroundColor Yellow
    Write-Log "Setting up backend structure"
    New-Item -ItemType Directory -Path "backend" -Force | Out-Null
    
    # LESSON 6: Create orchestrator that handles async properly (no event loop errors)
    $orchestratorContent = @"
#!/usr/bin/env python3
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sys
import os
import signal
import psutil
import json
from pathlib import Path
import argparse
from datetime import datetime

app = FastAPI(title="Grace AI System", version="1.0.0")

# LESSON 7: Proper CORS setup for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Grace AI System is running", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy", "backend": "running", "frontend": "available"}

@app.get("/api/status")
async def api_status():
    return {
        "backend": {"status": "running", "port": 8000},
        "frontend": {"status": "available", "port": 5173},
        "services": ["api", "orchestrator", "ui"]
    }

# LESSON 8: Proper process management with state persistence
class GraceProcessManager:
    def __init__(self):
        self.frontend_process = None
        self.state_file = Path("grace_state.json")
        
    def save_state(self):
        \"\"\"Save current state to JSON file\"\"\"
        state = {
            "backend_pid": os.getpid(),
            "backend_port": 8000,
            "frontend_pid": self.frontend_process.pid if self.frontend_process else None,
            "frontend_port": 5173,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        \"\"\"Load state from JSON file\"\"\"
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def clear_state(self):
        \"\"\"Clear state file\"\"\"
        if self.state_file.exists():
            self.state_file.unlink()
        
    def start_frontend(self):
        \"\"\"Start the frontend development server\"\"\"
        frontend_dir = Path(__file__).parent.parent / "frontend"
        if frontend_dir.exists() and (frontend_dir / "package.json").exists():
            try:
                self.frontend_process = subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=frontend_dir,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print("✓ Frontend started on http://localhost:5173")
                self.save_state()
                return True
            except Exception as e:
                print(f"⚠️ Could not start frontend: {e}")
                return False
        else:
            print("⚠️ Frontend directory not found or package.json missing")
            return False
    
    def stop_services(self, force=False):
        \"\"\"Stop all Grace services properly\"\"\"
        print("🛑 Stopping Grace services...")
        
        # Load state to find processes
        state = self.load_state()
        if state:
            # Stop processes by PID
            for pid_key in ["backend_pid", "frontend_pid"]:
                if state.get(pid_key):
                    try:
                        proc = psutil.Process(state[pid_key])
                        proc.terminate()
                        if force:
                            proc.kill()
                    except psutil.NoSuchProcess:
                        pass
                    except Exception as e:
                        print(f"⚠️ Error stopping process {state[pid_key]}: {e}")
        
        # Stop frontend process
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except:
                if force:
                    self.frontend_process.kill()
        
        # Kill any remaining processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if ('uvicorn' in cmdline and 'grace' in cmdline.lower()) or \
                   ('npm' in cmdline and 'dev' in cmdline):
                    proc.terminate()
                    if force:
                        proc.kill()
            except:
                continue
        
        self.clear_state()
        print("✓ Grace services stopped")

process_manager = GraceProcessManager()

def signal_handler(signum, frame):
    \"\"\"Handle shutdown signals properly\"\"\"
    process_manager.stop_services(force=True)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    parser = argparse.ArgumentParser(description="Grace Unified Orchestrator")
    parser.add_argument("--stop", action="store_true", help="Stop Grace services")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--force", action="store_true", help="Force stop")
    parser.add_argument("--env", default="dev", help="Environment (dev/prod/test)")
    parser.add_argument("--profile", default="native", help="Profile (native/docker/k8s)")
    parser.add_argument("--safe-mode", action="store_true", help="Safe mode")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    if args.stop:
        process_manager.stop_services(force=args.force)
        return
    
    if args.status:
        state = process_manager.load_state()
        if state:
            print("📊 Grace Status:")
            print(f"  Backend: http://localhost:{state.get('backend_port', 8000)} (PID: {state.get('backend_pid', 'unknown')})")
            print(f"  Frontend: http://localhost:{state.get('frontend_port', 5173)} (PID: {state.get('frontend_pid', 'unknown')})")
            print(f"  Started: {state.get('started_at', 'unknown')}")
            print(f"  Status: {state.get('status', 'unknown')}")
        else:
            print("📊 Grace Status: Not running")
        return
    
    print("🚀 Starting Grace AI System...")
    print(f"  Environment: {args.env}")
    print(f"  Profile: {args.profile}")
    print(f"  Safe Mode: {args.safe_mode}")
    print(f"  Backend: http://localhost:8000")
    print(f"  Frontend: http://localhost:5173")
    print(f"  API Docs: http://localhost:8000/docs")
    print("")
    print("Press Ctrl+C to stop")
    
    # Start frontend in background (unless safe mode)
    if not args.safe_mode:
        process_manager.start_frontend()
    
    # Start backend with proper error handling
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        process_manager.stop_services()
    except Exception as e:
        print(f"❌ Backend error: {e}")
        process_manager.stop_services()

if __name__ == "__main__":
    main()
"@
    
    $orchestratorContent | Out-File "backend\unified_grace_orchestrator.py" -Encoding UTF8
    Write-Log "Created unified_grace_orchestrator.py"
    
    # Create basic frontend structure
    Write-Host "🎨 Setting up frontend structure..." -ForegroundColor Yellow
    Write-Log "Setting up frontend structure"
    New-Item -ItemType Directory -Path "frontend" -Force | Out-Null
    
    # LESSON 9: Create proper package.json with all needed dependencies
    $packageJson = @"
{
  "name": "grace-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --port 5173 --host 0.0.0.0",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vite": "^4.0.0"
  }
}
"@
    
    $packageJson | Out-File "frontend\package.json" -Encoding UTF8
    Write-Log "Created package.json"
    
    # Create enhanced index.html with error handling
    $indexHtml = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace AI System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .status { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .endpoint { background: #333; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .success { color: #4CAF50; }
        .error { color: #f44336; }
        .info { color: #2196F3; }
        .loading { color: #ff9800; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Grace AI System</h1>
            <p>Autonomous AI Platform</p>
        </div>
        
        <div class="status" id="status">
            <h2>System Status</h2>
            <p class="loading" id="backend-status">⏳ Checking Backend...</p>
            <p class="success" id="frontend-status">✓ Frontend Running on Port 5173</p>
        </div>
        
        <div class="endpoint">
            <h3>API Endpoints</h3>
            <p><strong>Health Check:</strong> <a href="http://localhost:8000/health" target="_blank">http://localhost:8000/health</a></p>
            <p><strong>API Documentation:</strong> <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a></p>
            <p><strong>System Status:</strong> <a href="http://localhost:8000/api/status" target="_blank">http://localhost:8000/api/status</a></p>
        </div>
        
        <div class="endpoint">
            <h3>Quick Actions</h3>
            <p>• Backend API: <code>http://localhost:8000</code></p>
            <p>• Frontend UI: <code>http://localhost:5173</code></p>
            <p>• Stop Grace: <code>.\grace-universal.ps1 stop</code></p>
        </div>
    </div>
    
    <script>
        // LESSON 10: Proper error handling for backend connectivity
        async function checkBackendStatus() {
            try {
                const response = await fetch('http://localhost:8000/health');
                if (response.ok) {
                    document.getElementById('backend-status').innerHTML = '✓ Backend Running on Port 8000';
                    document.getElementById('backend-status').className = 'success';
                } else {
                    throw new Error('Backend not responding');
                }
            } catch (error) {
                document.getElementById('backend-status').innerHTML = '❌ Backend Connection Error - Check if backend is running';
                document.getElementById('backend-status').className = 'error';
            }
        }
        
        // Check backend status on load
        checkBackendStatus();
        
        // Recheck every 10 seconds
        setInterval(checkBackendStatus, 10000);
    </script>
</body>
</html>
"@
    
    $indexHtml | Out-File "frontend\index.html" -Encoding UTF8
    Write-Log "Created index.html"
    
    # Create vite.config.js
    $viteConfig = @"
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 5173,
    host: '0.0.0.0'
  }
})
"@
    
    $viteConfig | Out-File "frontend\vite.config.js" -Encoding UTF8
    Write-Log "Created vite.config.js"
    
    # LESSON 11: Install frontend dependencies with proper error handling
    if ($nodeCmd) {
        Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
        Write-Log "Installing frontend dependencies"
        Set-Location "frontend"
        try {
            & npm install --silent
            Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
            Write-Log "Frontend dependencies installed successfully"
        } catch {
            Write-Host "⚠️ Frontend dependency installation failed, but Grace will still work" -ForegroundColor Yellow
            Write-Log "Frontend dependency installation failed: $_" "WARN"
        }
        Set-Location ".."
    }
    
    # LESSON 12: Create launcher that anchors venv execution
    $launcherContent = @"
#!/usr/bin/env pwsh
# Anchor venv execution to avoid PATH ambiguity
`$ScriptRoot = Split-Path -Parent `$MyInvocation.MyCommand.Path
`$VenvPython = Join-Path `$ScriptRoot ".venv\Scripts\python.exe"

if (Test-Path `$VenvPython) {
    & `$VenvPython -m backend.unified_grace_orchestrator @args
} else {
    Write-Host "❌ Virtual environment not found. Run installation first." -ForegroundColor Red
    exit 1
}
"@
    
    $launcherContent | Out-File "grace.ps1" -Encoding UTF8
    Write-Log "Created grace.ps1 launcher"
    
    Write-Host "✅ Grace installation complete!" -ForegroundColor Green
    Write-Host "📍 Location: $InstallPath" -ForegroundColor Yellow
    Write-Host "🌐 Backend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "🎨 Frontend: http://localhost:5173" -ForegroundColor Cyan
    Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "📋 Logs: $LogFile" -ForegroundColor Gray
    Write-Host "" 
    Write-Host "🎯 All lessons learned from previous errors have been incorporated!" -ForegroundColor Green
    Write-Log "Grace installation completed successfully"
    return $true
}

function Start-Grace {
    Write-Log "Starting Grace with args: Environment=$Environment, Profile=$Profile, SafeMode=$SafeMode, DryRun=$DryRun"
    
    if (-not (Test-Path "grace.ps1")) {
        Write-Host "❌ Grace not found. Installing first..." -ForegroundColor Red
        if (-not (Install-Grace)) {
            Write-Host "❌ Installation failed. Cannot start Grace." -ForegroundColor Red
            return
        }
    }
    
    # Build arguments for orchestrator
    $orchestratorArgs = @()
    if ($Environment -ne "dev") { $orchestratorArgs += "--env", $Environment }
    if ($Profile -ne "native") { $orchestratorArgs += "--profile", $Profile }
    if ($SafeMode) { $orchestratorArgs += "--safe-mode" }
    if ($DryRun) { $orchestratorArgs += "--dry-run" }
    if ($Timeout -ne 60) { $orchestratorArgs += "--timeout", $Timeout }
    
    Write-Host "🚀 Starting Grace..." -ForegroundColor Green
    Write-Log "Executing grace.ps1 with args: $orchestratorArgs"
    
    if ($orchestratorArgs.Count -gt 0) {
        & ".\grace.ps1" @orchestratorArgs
    } else {
        & ".\grace.ps1"
    }
}

function Stop-Grace {
    Write-Host "🛑 Stopping Grace..." -ForegroundColor Yellow
    Write-Log "Stopping Grace with Force=$Force"
    
    if (Test-Path "grace.ps1") {
        $stopArgs = @("--stop")
        if ($Force) { $stopArgs += "--force" }
        & ".\grace.ps1" @stopArgs
    } else {
        Write-Host "❌ Grace not found at current location" -ForegroundColor Red
        Write-Log "Grace not found at current location" "ERROR"
    }
}

function Show-Status {
    Write-Host "📊 Grace Status..." -ForegroundColor Yellow
    Write-Log "Checking Grace status"
    
    if (Test-Path "grace.ps1") {
        & ".\grace.ps1" --status
    } else {
        Write-Host "❌ Grace not found at current location" -ForegroundColor Red
        Write-Log "Grace not found at current location" "ERROR"
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
  -Environment    Environment (dev/prod/test) - default: dev
  -Profile        Profile (native/docker/k8s) - default: native
  -Force          Force stop services
  -Global         Install globally (requires admin)
  -SafeMode       Start in safe mode (backend only)
  -DryRun         Dry run mode
  -Verbose        Verbose logging
  -Timeout        Timeout in seconds - default: 60

EXAMPLES:
  .\grace-universal.ps1                              # Start Grace (install if needed)
  .\grace-universal.ps1 install                      # Just install
  .\grace-universal.ps1 start -Environment prod      # Start in production mode
  .\grace-universal.ps1 start -Profile docker        # Start with Docker profile
  .\grace-universal.ps1 start -SafeMode              # Start backend only
  .\grace-universal.ps1 stop                         # Stop services
  .\grace-universal.ps1 stop -Force                  # Force stop
  .\grace-universal.ps1 status                       # Show status

MULTI-OS SUPPORT:
  Windows: .\grace-universal.ps1
  Linux:   ./grace-universal.sh (coming soon)
  macOS:   ./grace-universal.sh (coming soon)

QUICK START:
  1. Download this script
  2. Run: .\grace-universal.ps1
  3. Access: http://localhost:5173

LOGS:
  All operations logged to: logs/boot.log

"@ -ForegroundColor White
}

# Main execution
Write-GraceHeader

# Ensure we're in the right directory
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}
Set-Location $InstallPath

switch ($Action.ToLower()) {
    "install" { 
        Install-Grace 
    }
    "start" { 
        Start-Grace 
    }
    "stop" { 
        Stop-Grace 
    }
    "status" { 
        Show-Status 
    }
    "help" { Show-Help }
    default { 
        Start-Grace 
    }
}

Write-Log "Grace Universal Script completed - Action: $Action"

