#!/bin/bash

echo "🚀 Grace - Commit and Push to GitHub"
echo "====================================="

# Add all changes
echo "📦 Adding all changes..."
git add .

# Check status
echo "📋 Git status:"
git status --short

# Commit with descriptive message
echo "💾 Committing changes..."
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
echo "🌐 Pushing to GitHub..."
git push origin main

echo "✅ Successfully pushed to GitHub!"
echo "🔗 Check your repository for the changes"