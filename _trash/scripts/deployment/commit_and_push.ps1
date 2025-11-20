Write-Host "🚀 Grace - Commit and Push to GitHub" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Add all changes
Write-Host "📦 Adding all changes..." -ForegroundColor Yellow
git add .

# Check status
Write-Host "📋 Git status:" -ForegroundColor Cyan
git status --short

# Commit with descriptive message
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m "feat: Add universal service launcher with 8000→5173 trigger

- Enhanced backend/grace.py with service launch capabilities
- Added backend server on port 8000 with health endpoints
- Added frontend proxy server on port 5173 with built-in UI
- Implemented sequential startup: backend first, then frontend
- Added port cleanup and service validation
- Included minimal chat interface connecting to backend
- Added CORS support for cross-origin requests

Features:
- ✅ Backend API server (8000)
- ✅ Frontend proxy server (5173) 
- ✅ Health check endpoints
- ✅ Built-in chat interface
- ✅ Service validation
- ✅ Port conflict resolution

Usage: python backend/grace.py"

# Push to GitHub
Write-Host "🌐 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "🔗 Check your repository for the changes" -ForegroundColor Cyan