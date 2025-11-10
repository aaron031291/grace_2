# Enhanced batch conflict resolution for common patterns
# Pattern 1: BOM character conflicts (HEAD clean vs origin/main with BOM)
# Pattern 2: Base import conflicts (already handled by batch_resolve_conflicts.ps1)

$backendFiles = Get-ChildItem -Path "backend" -Recurse -Include *.py -File
$resolved = 0
$modified = @()

foreach ($file in $backendFiles) {
    $content = Get-Content $file.FullName -Raw
    $original = $content
    
    # Pattern 1: BOM in origin/main - keep HEAD's clean version
    # Matches lines with BOM character (ï»¿) in merge conflicts
    $content = $content -replace '<<<<<<< HEAD\r?\n([^\r\n]+)\r?\n=======\r?\nï»¿\1\r?\n>>>>>>> origin/main', '$1'
    
    # Pattern 2: Checkmark vs [OK] style - keep HEAD's checkmark
    $content = $content -replace '<<<<<<< HEAD\r?\n(\s+print\(f"✓[^"]+"\))\r?\n=======\r?\n\s+print\(f"\[OK\][^"]+"\)\r?\n>>>>>>> origin/main', '$1'
    $content = $content -replace '<<<<<<< HEAD\r?\n(\s+print\(f"✗[^"]+"\))\r?\n=======\r?\n\s+print\(f"\[FAIL\][^"]+"\)\r?\n>>>>>>> origin/main', '$1'
    $content = $content -replace '<<<<<<< HEAD\r?\n(\s+print\(f"⚠️[^"]+"\))\r?\n=======\r?\n\s+print\(f"\[WARN\][^"]+"\)\r?\n>>>>>>> origin/main', '$1'
    
    if ($content -ne $original) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        $resolved++
        $modified += $file.FullName
        Write-Host "Resolved: $($file.FullName)"
    }
}

Write-Host "`n========================================="
Write-Host "Enhanced Batch Resolution Complete"
Write-Host "========================================="
Write-Host "Files modified: $resolved"

if ($resolved -gt 0) {
    Write-Host "`nModified files:"
    $modified | ForEach-Object { Write-Host "  $_" }
}
