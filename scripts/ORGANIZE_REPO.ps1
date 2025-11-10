# ============================================================================
# ORGANIZE GRACE REPOSITORY - CREATE FOLDERS & MOVE FILES
# Creates proper folder structure and organizes all files
# ============================================================================

Write-Host "🧹 Organizing Grace Repository..." -ForegroundColor Cyan
Write-Host ""

Set-Location C:\Users\aaron\grace_2

# ============================================================================
# CREATE FOLDER STRUCTURE
# ============================================================================

Write-Host "📁 Creating folder structure..." -ForegroundColor Yellow

$folders = @(
    # Documentation folders
    "docs/kernels",
    "docs/systems",
    "docs/systems/cognition",
    "docs/systems/parliament",
    "docs/systems/meta-loop",
    "docs/systems/speech",
    "docs/systems/transcendence",
    "docs/systems/verification",
    "docs/systems/self-healing",
    "docs/implementation",
    "docs/deployment",
    "docs/metrics",
    
    # Scripts folders
    "scripts/boot",
    "scripts/utilities",
    "scripts/testing",
    
    # Config folders
    "config/playbooks",
    "config/policies"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  ✓ Created: $folder" -ForegroundColor Green
    } else {
        Write-Host "  → Exists: $folder" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "✅ Folder structure complete!" -ForegroundColor Green
Write-Host ""

# ============================================================================
# ORGANIZE KERNEL DOCS
# ============================================================================

Write-Host "📦 Organizing kernel documentation..." -ForegroundColor Yellow

$kernelDocs = @(
    "KERNEL_ARCHITECTURE_COMPLETE.md",
    "KERNEL_API_AUDIT_COMPLETE.md",
    "KERNEL_IMPLEMENTATION_COMPLETE.md",
    "README_KERNELS.md"
)

foreach ($file in $kernelDocs) {
    $source = "docs/$file"
    $dest = "docs/kernels/$file"
    
    if (Test-Path $source) {
        Move-Item $source $dest -Force
        Write-Host "  ✓ Moved: $file → docs/kernels/" -ForegroundColor Green
    }
}

# ============================================================================
# ORGANIZE SYSTEM DOCS
# ============================================================================

Write-Host "📦 Organizing system documentation..." -ForegroundColor Yellow

# Cognition docs
$cognitionDocs = @(
    "COGNITION_*.md"
)
Get-ChildItem "docs/COGNITION_*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "docs/systems/cognition/" -Force
    Write-Host "  ✓ Moved: $($_.Name) → docs/systems/cognition/" -ForegroundColor Green
}

# Parliament docs
Get-ChildItem "docs/PARLIAMENT_*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "docs/systems/parliament/" -Force
    Write-Host "  ✓ Moved: $($_.Name) → docs/systems/parliament/" -ForegroundColor Green
}

# Meta-loop docs
Get-ChildItem "docs/META_LOOP*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "docs/systems/meta-loop/" -Force
    Write-Host "  ✓ Moved: $($_.Name) → docs/systems/meta-loop/" -ForegroundColor Green
}

# Speech docs
Get-ChildItem "docs/SPEECH_*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "docs/systems/speech/" -Force
    Write-Host "  ✓ Moved: $($_.Name) → docs/systems/speech/" -ForegroundColor Green
}

# Transcendence docs
Get-ChildItem "docs/TRANSCENDENCE_*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "docs/systems/transcendence/" -Force
    Write-Host "  ✓ Moved: $($_.Name) → docs/systems/transcendence/" -ForegroundColor Green
}

# Verification docs
Get-ChildItem "docs/VERIFICATION_*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "docs/systems/verification/" -Force
    Write-Host "  ✓ Moved: $($_.Name) → docs/systems/verification/" -ForegroundColor Green
}

# Self-healing docs
Get-ChildItem "docs/SELF_HEALING*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "docs/systems/self-healing/" -Force
    Write-Host "  ✓ Moved: $($_.Name) → docs/systems/self-healing/" -ForegroundColor Green
}

# Agentic docs
Get-ChildItem "docs/AGENTIC_*.md" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "docs/systems/" -Force
    Write-Host "  ✓ Moved: $($_.Name) → docs/systems/" -ForegroundColor Green
}

# ============================================================================
# ORGANIZE IMPLEMENTATION DOCS
# ============================================================================

Write-Host "📦 Organizing implementation docs..." -ForegroundColor Yellow

$implDocs = @(
    "*_IMPLEMENTATION*.md",
    "*_COMPLETE.md",
    "*_DELIVERED.md",
    "*_SUMMARY.md"
)

foreach ($pattern in $implDocs) {
    Get-ChildItem "docs/$pattern" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "docs/implementation/" -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Moved: $($_.Name) → docs/implementation/" -ForegroundColor Green
    }
}

# ============================================================================
# ORGANIZE DEPLOYMENT DOCS
# ============================================================================

Write-Host "📦 Organizing deployment docs..." -ForegroundColor Yellow

$deployDocs = @(
    "DEPLOYMENT_*.md",
    "PRODUCTION_*.md",
    "BOOT_*.md"
)

foreach ($pattern in $deployDocs) {
    Get-ChildItem "docs/$pattern" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "docs/deployment/" -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Moved: $($_.Name) → docs/deployment/" -ForegroundColor Green
    }
}

# ============================================================================
# ORGANIZE METRICS DOCS
# ============================================================================

Write-Host "📦 Organizing metrics docs..." -ForegroundColor Yellow

$metricsDocs = @(
    "METRICS_*.md"
)

foreach ($pattern in $metricsDocs) {
    Get-ChildItem "docs/$pattern" -ErrorAction SilentlyContinue | ForEach-Object {
        Move-Item $_.FullName "docs/metrics/" -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Moved: $($_.Name) → docs/metrics/" -ForegroundColor Green
    }
}

# ============================================================================
# DONE
# ============================================================================

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "✅ REPOSITORY ORGANIZED!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""

Write-Host "📊 RESULTS:" -ForegroundColor Cyan
Write-Host "  ✓ Created organized folder structure" -ForegroundColor Green
Write-Host "  ✓ Moved system docs to docs/systems/" -ForegroundColor Green
Write-Host "  ✓ Moved kernel docs to docs/kernels/" -ForegroundColor Green
Write-Host "  ✓ Moved implementation docs to docs/implementation/" -ForegroundColor Green
Write-Host "  ✓ Moved deployment docs to docs/deployment/" -ForegroundColor Green
Write-Host "  ✓ Moved metrics docs to docs/metrics/" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Boot Grace with:" -ForegroundColor Cyan
Write-Host "  .\GRACE.ps1" -ForegroundColor White
Write-Host ""
