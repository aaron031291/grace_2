#!/bin/bash
# Pre-commit hook to ensure build stays green

set -e

echo "🔍 Running pre-commit checks..."

# Change to frontend directory
cd "$(dirname "$0")/.."

# Check for legacy files in src root
echo "📂 Checking for legacy files in src root..."
LEGACY_FILES=$(find src -maxdepth 1 -name "Grace*.tsx" -o -name "App.backup.tsx" -o -name "App.minimal.tsx" 2>/dev/null || true)

if [ -n "$LEGACY_FILES" ]; then
  echo "❌ Legacy files found in src root:"
  echo "$LEGACY_FILES"
  echo ""
  echo "These should be in src/legacy/ folder."
  exit 1
fi

echo "✓ No legacy files in src root"

# Type check
echo "🔎 Running TypeScript type check..."
if ! npx tsc -b --noEmit; then
  echo "❌ TypeScript errors found"
  exit 1
fi

echo "✓ Type check passed"

# Build check
echo "🔨 Running build..."
if ! npm run build > /dev/null 2>&1; then
  echo "❌ Build failed"
  npm run build
  exit 1
fi

echo "✓ Build passed"

echo ""
echo "✅ All pre-commit checks passed!"
