# Batch resolve simple merge conflicts in backend Python files
# Pattern 1: Base import conflicts

$backendFiles = Get-ChildItem -Path "backend" -Recurse -Include *.py -File
$resolved = 0
$modified = @()

foreach ($file in $backendFiles) {
    $content = Get-Content $file.FullName -Raw
    $original = $content
    
    # Pattern 1: from .models import Base -> from .base_models import Base
    $content = $content -replace '<<<<<<< HEAD\r?\nfrom \.models import Base\r?\n=======\r?\nfrom \.base_models import Base\r?\n>>>>>>> origin/main', 'from .base_models import Base'
    
    # Pattern 2: Import with whitespace variations
    $content = $content -replace '<<<<<<< HEAD\s+from \.models import Base\s+=======\s+from \.base_models import Base\s+>>>>>>> origin/main', 'from .base_models import Base'
    
    if ($content -ne $original) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        $resolved++
        $modified += $file.FullName
        Write-Host "Resolved: $($file.FullName)"
    }
}

Write-Host "`n========================================="
Write-Host "Batch Resolution Complete"
Write-Host "========================================="
Write-Host "Files modified: $resolved"
Write-Host ""

if ($resolved -gt 0) {
    Write-Host "Modified files:"
    $modified | ForEach-Object { Write-Host "  $_" }
}
