# Start Grace Frontend

Backend is running on port 8000 ✅

## Start Frontend

Open a NEW terminal/PowerShell window:

```powershell
cd c:\Users\aaron\grace_2\frontend
npm run dev
```

**Expected output:**
```
  VITE v7.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## Access Grace UI

Open browser to: **http://localhost:5173**

## What's Available in Frontend

The frontend can now access:
- ✅ Chat API
- ✅ Clarity Framework status
- ✅ Component manifest
- ✅ Event history
- ✅ System health

## New Components Created

- `frontend/src/services/clarityApi.ts` - API client for clarity endpoints
- `frontend/src/components/ClarityDashboard.tsx` - Dashboard component

## Quick Test

Once frontend starts, you can:
1. View the Clarity Dashboard (if integrated into routing)
2. Call clarity APIs from browser console:
   ```javascript
   fetch('http://localhost:8000/api/clarity/status')
     .then(r => r.json())
     .then(console.log)
   ```

## Both Running

When both are running:
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5173

Press `Ctrl+C` in each window to stop.
