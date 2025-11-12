# Remove BOM characters from all Python files in backend

$files = Get-ChildItem -Path "backend" -Recurse -Include *.py -File
$fixed = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Check if file starts with BOM or contains BOM
    if ($content -match '\ufeff') {
        # Remove all BOM characters
        $cleaned = $content -replace '\ufeff', ''
        
        # Write back without BOM
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($file.FullName, $cleaned, $utf8NoBom)
        
        $fixed++
        Write-Host "Fixed: $($file.FullName)"
    }
}

Write-Host "`nRemoved BOM from $fixed files"
