# Frontend Build Validation

## Overview

The frontend build now includes automated smoke tests and validation to ensure builds stay green.

## Quick Commands

```bash
# Standard build
npm run build

# Build with validation
npm run build:check

# Run smoke tests
npm run test:smoke

# Run build validation tests
npm run test:build

# All tests
npm test
```

## What's Validated

### 1. Build Process
- ✅ TypeScript compilation succeeds
- ✅ Vite bundling completes
- ✅ No legacy files in active source
- ✅ Output files generated

### 2. Build Output
- ✅ `dist/` folder exists
- ✅ `dist/index.html` is valid HTML
- ✅ JavaScript bundles present
- ✅ CSS bundles present
- ✅ No TypeScript files in output
- ✅ Bundle size < 5MB

### 3. Runtime Smoke Tests
- ✅ App loads without errors
- ✅ Sidebar controls present
- ✅ Chat input functional
- ✅ Backend API endpoints respond

## Automated Tests

### Build Validation (`tests/build.spec.ts`)
```typescript
test('dist folder exists and contains files')
test('index.html exists and is valid')
test('assets contain JS/CSS bundles')
test('no TypeScript files in dist')
test('bundle size is reasonable')
```

### Smoke Tests (`tests/smoke.spec.ts`)
```typescript
test('frontend app loads successfully')
test('sidebar controls are present')
test('chat input is functional')
test('backend health endpoint responds')
test('chat API endpoint exists')
test('no legacy files in active build')
```

## CI/CD Integration

### GitHub Actions (`.github/workflows/build-check.yml`)
Runs on every push/PR:
1. Install dependencies
2. Type check
3. Lint (non-blocking)
4. Build
5. Validate build output
6. Upload artifacts
7. Check bundle sizes

### Pre-commit Hook (`scripts/pre-commit-check.sh`)
Run before committing:
```bash
chmod +x scripts/pre-commit-check.sh
ln -s ../../frontend/scripts/pre-commit-check.sh .git/hooks/pre-commit
```

Checks:
- No legacy files in src root
- TypeScript compiles
- Build succeeds

### Windows Validation (`scripts/validate-build.bat`)
```cmd
cd frontend
scripts\validate-build.bat
```

## Legacy File Protection

### Current Structure
```
frontend/src/
├── main.tsx              ✅ Active
├── AppChat.tsx           ✅ Active
├── components/           ✅ Active
├── api/                  ✅ Active
└── legacy/               ❌ Excluded
    ├── Grace*.tsx        (34 files)
    └── App.backup.tsx
```

### TypeScript Config (`tsconfig.app.json`)
```json
{
  "include": [
    "src/main.tsx",
    "src/AppChat.tsx",
    "src/components/**/*",
    "src/api/**/*"
  ],
  "exclude": [
    "src/legacy/**/*"
  ]
}
```

## Running Validation

### Local Development
```bash
# Before committing
npm run build:check

# Quick smoke test
npm run test:smoke

# Full test suite
npm test
```

### Continuous Integration
```yaml
# .github/workflows/build-check.yml runs automatically on:
- Push to main/develop
- Pull requests
- Changes in frontend/**
```

### Manual Validation
```bash
# Windows
cd frontend
scripts\validate-build.bat

# Linux/Mac
cd frontend
chmod +x scripts/pre-commit-check.sh
./scripts/pre-commit-check.sh
```

## Troubleshooting

### Build Fails with TypeScript Errors
```bash
# Check what's included in build
npx tsc -b --listFiles

# Verify legacy is excluded
grep -r "GraceAgentic" src/
# Should only find: src/legacy/GraceAgentic.tsx
```

### Legacy Files in Build
```bash
# Move to legacy folder
mv src/Grace*.tsx src/legacy/
mv src/App.backup.tsx src/legacy/

# Rebuild
npm run build
```

### Smoke Tests Fail
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend
cd ../
python server.py

# Start frontend
cd frontend
npm run dev
```

## Adding New Tests

### Build Validation Test
```typescript
// tests/build.spec.ts
test('my new build check', () => {
  const distPath = path.join(process.cwd(), 'dist');
  // Your validation logic
  expect(something).toBeTruthy();
});
```

### Smoke Test
```typescript
// tests/smoke.spec.ts
test('my new feature works', async ({ page }) => {
  await page.goto('http://localhost:5173');
  // Your test logic
  await expect(page.locator('.my-feature')).toBeVisible();
});
```

## Best Practices

1. **Run `npm run build:check` before pushing**
2. **Keep legacy files in `src/legacy/`**
3. **Don't import from legacy folder**
4. **Update tests when adding new features**
5. **Monitor bundle sizes** (keep < 5MB)

## Checklist for New Components

- [ ] Component in `src/components/` or `src/`
- [ ] Not named `Grace*.tsx` or `App.backup.tsx`
- [ ] Added to `tsconfig.app.json` include if needed
- [ ] No imports from `src/legacy/`
- [ ] Build passes: `npm run build`
- [ ] Tests pass: `npm run test:build`

## Success Criteria

✅ **Green Build**: `npm run build` exits with code 0  
✅ **No Errors**: No TypeScript errors  
✅ **No Legacy**: Legacy files only in `src/legacy/`  
✅ **Tests Pass**: All smoke tests green  
✅ **Small Bundles**: JS bundles < 5MB  
✅ **Valid Output**: `dist/index.html` exists and valid  

## Summary

The frontend build is now protected by:
- 🔒 TypeScript exclude rules for legacy code
- 🧪 Automated build validation tests
- 💨 Quick smoke tests for core functionality
- 🤖 CI/CD pipeline for continuous validation
- 🪝 Pre-commit hooks for local validation

**Result: Builds stay green! 🟢**
