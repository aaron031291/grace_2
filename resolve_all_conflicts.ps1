# Comprehensive conflict resolver for Grace repo
# Resolves common merge conflict patterns automatically

param(
    [string]$Path = ".",
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Continue"
$filesProcessed = 0
$conflictsResolved = 0
$errors = @()

Write-Host "=== Grace Conflict Resolver ===" -ForegroundColor Cyan
Write-Host "Path: $Path" -ForegroundColor Gray
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })
Write-Host ""

# Find all files with conflict markers
$conflictFiles = git diff --check --cached 2>&1 | 
    Where-Object { $_ -match "leftover conflict marker" } |
    ForEach-Object { 
        if ($_ -match "^([^:]+):") { $matches[1] }
    } | Select-Object -Unique

if (-not $conflictFiles) {
    # Fallback: search all text files
    Write-Host "Git check found no conflicts, scanning files directly..." -ForegroundColor Yellow
    $conflictFiles = Get-ChildItem -Path $Path -Recurse -Include *.py,*.md,*.txt,*.yaml,*.yml,*.json,*.js,*.ts,*.tsx,*.jsx,*.sh,*.ps1,*.bat -File |
        Where-Object { 
            $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
            $content -match '<<<<<<<|=======|>>>>>>>'
        } | Select-Object -ExpandProperty FullName
}

Write-Host "Found $($conflictFiles.Count) files with conflicts" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $conflictFiles) {
    $fullPath = Join-Path (Get-Location) $file
    if (-not (Test-Path $fullPath)) { continue }
    
    Write-Host "Processing: $file" -ForegroundColor White
    
    try {
        $content = Get-Content $fullPath -Raw -Encoding UTF8
        $originalContent = $content
        $fileConflicts = 0
        
        # Pattern 1: Arrow style conflicts (any arrow to ->)
        # Simplified: just remove conflict markers and keep arrow variants as-is, normalizing to ->
        $content = $content -replace '(?s)<<<<<<<\s+HEAD\s*\n([^\n]+)\n=======\s*\n([^\n]+)\n>>>>>>>\s+origin/main', {
            param($match)
            $head = $match.Groups[1].Value
            $main = $match.Groups[2].Value
            # If lines differ only in arrow style, normalize to ->
            if ($head -replace '[→]', '->' -eq $main -replace '[→]', '->') {
                return $head -replace '[→]', '->'
            }
            # If identical, keep one
            if ($head -eq $main) { return $head }
            # Otherwise keep HEAD for now (conservative)
            return $head
        }
        if ($content -ne $originalContent) { 
            $fileConflicts++ 
            $originalContent = $content
        }
        
        # Pattern 2: Print statement conflicts (✓ vs [OK])
        $content = $content -replace '(?s)<<<<<<<\s+HEAD\s*\n(\s*)print\(f"✓([^"]+)"\)\n=======\s*\n(\s*)print\(f"\[OK\]([^"]+)"\)\n>>>>>>>\s+origin/main', '$1print(f"[OK]$2")'
        if ($content -ne $originalContent) { 
            $fileConflicts++ 
            $originalContent = $content
        }
        
        # Pattern 3: TODO comment conflicts
        $content = $content -replace '(?s)<<<<<<<\s+HEAD\s*\n(\s*)#\s*TODO:([^\n]+)\n=======\s*\n(\s*)#\s*TODO\(FUTURE\):([^\n]+)\n>>>>>>>\s+origin/main', '$1# TODO:$2'
        if ($content -ne $originalContent) { 
            $fileConflicts++ 
            $originalContent = $content
        }
        
        # Pattern 4: Simple identical line conflicts (keep one copy)
        $content = $content -replace '(?s)<<<<<<<\s+HEAD\s*\n([^\n]+)\n=======\s*\n\1\n>>>>>>>\s+origin/main', '$1'
        if ($content -ne $originalContent) { 
            $fileConflicts++ 
            $originalContent = $content
        }
        
        # Pattern 5: Empty vs non-empty (keep non-empty)
        $content = $content -replace '(?s)<<<<<<<\s+HEAD\s*\n\s*\n=======\s*\n([^\n<]+)\n>>>>>>>\s+origin/main', '$1'
        if ($content -ne $originalContent) { 
            $fileConflicts++ 
            $originalContent = $content
        }
        
        $content = $content -replace '(?s)<<<<<<<\s+HEAD\s*\n([^\n<]+)\n=======\s*\n\s*\n>>>>>>>\s+origin/main', '$1'
        if ($content -ne $originalContent) { 
            $fileConflicts++ 
            $originalContent = $content
        }
        
        # Pattern 6: Generic conflict resolution (prefer HEAD side for now)
        # This is conservative - only resolves if both sides are very short
        $content = $content -replace '(?s)<<<<<<<\s+HEAD\s*\n([^\n]{1,80})\n=======\s*\n([^\n]{1,80})\n>>>>>>>\s+origin/main', '$1'
        if ($content -ne $originalContent) { 
            $fileConflicts++ 
            $originalContent = $content
        }
        
        if ($fileConflicts -gt 0) {
            $filesProcessed++
            $conflictsResolved += $fileConflicts
            Write-Host "  → Resolved $fileConflicts conflict(s)" -ForegroundColor Green
            
            if (-not $DryRun) {
                Set-Content -Path $fullPath -Value $content -Encoding UTF8 -NoNewline
            }
        } else {
            Write-Host "  → No auto-resolvable conflicts" -ForegroundColor Yellow
        }
        
    } catch {
        $errors += "Error processing $file : $_"
        Write-Host "  → ERROR: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Files processed: $filesProcessed" -ForegroundColor White
Write-Host "Conflicts resolved: $conflictsResolved" -ForegroundColor Green

if ($errors.Count -gt 0) {
    Write-Host "Errors: $($errors.Count)" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
}

if ($DryRun) {
    Write-Host ""
    Write-Host "DRY RUN - No files were modified" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to apply changes" -ForegroundColor Yellow
}

Write-Host ""
