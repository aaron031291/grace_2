@echo off
echo ========================================
echo   Grace Console - Build Verification
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Node.js...
node --version
echo.

echo Checking npm...
npm --version
echo.

echo Installing dependencies...
call npm install
echo.

echo Running type check...
call npm run type-check
if errorlevel 1 (
    echo.
    echo [WARNING] Type check had errors, but build may still work
    echo.
) else (
    echo.
    echo [SUCCESS] Type check passed!
    echo.
)

echo Testing build...
call npm run build
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo [SUCCESS] Build completed successfully!
    echo.
    echo Build output is in: dist/
    echo.
)

echo.
echo ========================================
echo   Verification Complete!
echo ========================================
echo.
echo To start development server:
echo   npm run dev
echo.
echo To preview production build:
echo   npm run preview
echo.

pause
