# Automated conflict resolution for Base import pattern
# Replaces: from .models import Base -> from .base_models import Base

$files = Get-ChildItem -Path "backend" -Recurse -Include *.py -File | 
    Select-String -Pattern "^<<<<<<< HEAD" -CaseSensitive | 
    Select-Object -ExpandProperty Path -Unique

$resolved = 0
$skipped = 0

foreach ($file in $files) {
    $content = Get-Content $file -Raw
    
    # Pattern: conflict with only Base import difference
    $pattern = '<<<<<<< HEAD\s+from \.models import Base\s+=======\s+from \.base_models import Base\s+>>>>>>> origin/main'
    
    if ($content -match $pattern) {
        $newContent = $content -replace $pattern, 'from .base_models import Base'
        Set-Content -Path $file -Value $newContent -NoNewline
        Write-Host "Resolved: $file"
        $resolved++
    } else {
        $skipped++
    }
}

Write-Host "`nResolved: $resolved files"
Write-Host "Skipped (complex conflicts): $skipped files"
