# Check Backend Job Output
# Run this to see what's actually happening

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "CHECKING BACKEND OUTPUT" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Get all jobs
$jobs = Get-Job

if ($jobs.Count -eq 0) {
    Write-Host "No jobs found. Backend not running." -ForegroundColor Yellow
    exit
}

Write-Host "Found $($jobs.Count) job(s):" -ForegroundColor Green
$jobs | Format-Table Id, Name, State

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "BACKEND OUTPUT (Last 50 lines):" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Get output from each job
foreach ($job in $jobs) {
    Write-Host "Job $($job.Id) - $($job.Name) - State: $($job.State)" -ForegroundColor Yellow
    Write-Host "-" * 80 -ForegroundColor Gray
    
    $output = Receive-Job -Id $job.Id -Keep
    if ($output) {
        $output | Select-Object -Last 50
    } else {
        Write-Host "(No output yet)" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "To stop all jobs: Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
