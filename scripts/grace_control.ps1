# Grace Master Control Script (PowerShell)

function Show-Menu {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "     GRACE MASTER CONTROL CENTER" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Start Grace (Backend + Frontend)" -ForegroundColor Green
    Write-Host "2. Start Backend Only" -ForegroundColor Green
    Write-Host "3. Chat with Grace (Terminal)" -ForegroundColor Yellow
    Write-Host "4. View Logs (One-time)" -ForegroundColor Yellow
    Write-Host "5. Watch Logs (Auto-refresh 5min)" -ForegroundColor Yellow
    Write-Host "6. Watch Healing (Real-time)" -ForegroundColor Yellow
    Write-Host "7. Check Health" -ForegroundColor Magenta
    Write-Host "8. Enable Autonomy" -ForegroundColor Magenta
    Write-Host "9. System Dashboard" -ForegroundColor Cyan
    Write-Host "0. Exit" -ForegroundColor Red
    Write-Host ""
}

Set-Location $PSScriptRoot

while ($true) {
    Show-Menu
    $choice = Read-Host "Select option (0-9)"
    
    switch ($choice) {
        "1" {
            Write-Host "`nStarting Grace (Backend + Frontend)..." -ForegroundColor Green
            Start-Process "start_both.bat"
            Start-Sleep -Seconds 2
        }
        "2" {
            Write-Host "`nStarting Backend..." -ForegroundColor Green
            Start-Process "restart_backend.bat"
            Start-Sleep -Seconds 2
        }
        "3" {
            Write-Host "`nOpening chat with Grace..." -ForegroundColor Yellow
            & ".\chat_with_grace.ps1"
        }
        "4" {
            Write-Host "`nViewing logs..." -ForegroundColor Yellow
            & ".\view_logs.ps1"
        }
        "5" {
            Write-Host "`nStarting auto-refresh log viewer..." -ForegroundColor Yellow
            & ".\watch_all_logs.ps1"
        }
        "6" {
            Write-Host "`nStarting healing monitor..." -ForegroundColor Yellow
            & ".\watch_healing.ps1"
        }
        "7" {
            Write-Host "`nChecking Grace health..." -ForegroundColor Magenta
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
                Write-Host "`n✅ Backend is healthy" -ForegroundColor Green
                $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
            } catch {
                Write-Host "`n❌ Backend not running. Start it first (option 1 or 2)" -ForegroundColor Red
            }
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "8" {
            Write-Host "`nEnabling autonomy..." -ForegroundColor Magenta
            try {
                $body = @{ tier = 2 } | ConvertTo-Json
                $response = Invoke-RestMethod -Uri "http://localhost:8000/api/healing/autonomy/enable" `
                    -Method Post -Body $body -ContentType "application/json"
                Write-Host "`n✅ Autonomy enabled at Tier 2" -ForegroundColor Green
                $response | ConvertTo-Json -Depth 10
            } catch {
                Write-Host "`n❌ Failed. Backend not running?" -ForegroundColor Red
            }
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "9" {
            Write-Host "`nFetching system dashboard..." -ForegroundColor Cyan
            try {
                $dashboard = Invoke-RestMethod -Uri "http://localhost:8000/api/healing/analytics/summary"
                Write-Host "`n📊 GRACE SYSTEM DASHBOARD" -ForegroundColor Cyan
                Write-Host "========================" -ForegroundColor Cyan
                $dashboard | ConvertTo-Json -Depth 10
            } catch {
                Write-Host "`n❌ Backend not running" -ForegroundColor Red
            }
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "0" {
            Write-Host "`nGoodbye!" -ForegroundColor Cyan
            exit
        }
        default {
            Write-Host "`nInvalid choice" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}
