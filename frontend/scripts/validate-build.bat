@echo off
REM Windows version of build validation

echo Validating frontend build...
echo.

cd /d "%~dp0\.."

echo [1/4] Checking for legacy files in src root...
dir src\Grace*.tsx >nul 2>&1
if %errorlevel% equ 0 (
  echo [ERROR] Legacy Grace*.tsx files found in src root
  echo These should be in src\legacy\ folder
  exit /b 1
)
echo [OK] No legacy files in src root
echo.

echo [2/4] Running TypeScript check...
call npx tsc -b
if %errorlevel% neq 0 (
  echo [ERROR] TypeScript errors found
  exit /b 1
)
echo [OK] TypeScript check passed
echo.

echo [3/4] Building production bundle...
call npm run build
if %errorlevel% neq 0 (
  echo [ERROR] Build failed
  exit /b 1
)
echo [OK] Build successful
echo.

echo [4/4] Validating build output...
if not exist "dist\index.html" (
  echo [ERROR] dist\index.html not found
  exit /b 1
)
echo [OK] Build output validated
echo.

echo ========================================
echo [SUCCESS] All validation checks passed!
echo ========================================
