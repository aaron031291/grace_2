@echo off
echo Stopping all Node processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo Clearing Vite cache...
cd frontend
if exist node_modules\.vite rmdir /s /q node_modules\.vite
if exist dist rmdir /s /q dist

echo.
echo Starting Vite with verbose logging...
echo.
set DEBUG=vite:*
npm run dev -- --force --clearScreen false
