# Quick Start - System Overview Panel

## What You Get

A **tile grid dashboard** as the default landing page with:
- 6 interactive tiles showing system health
- Detail drawers for deep inspection
- Quick controls for common actions
- Auto-refresh every 15 seconds

## Start the Frontend

```bash
cd frontend
npm run dev
```

Open: http://localhost:5173

## First Look

You'll see **6 tiles**:

```
┌─────────────────┬─────────────────┬─────────────────┐
│  🏥 Health      │  🧠 Learning    │  🎯 Missions    │
│  Trust: 95%     │  Active         │  12 total       │
│  Health: 98%    │  450 artifacts  │  3 in progress  │
└─────────────────┴─────────────────┴─────────────────┘
┌─────────────────┬─────────────────┬─────────────────┐
│  🔧 Healing     │  📸 Snapshots   │  🔒 Remote      │
│  24 incidents   │  8 available    │  Inactive       │
│  95% success    │  Latest: 12/20  │  0 sessions     │
└─────────────────┴─────────────────┴─────────────────┘
```

## Quick Actions

**Top-right controls:**
- Click **"⏸️ Pause Learning"** → Pauses Google/Bing collectors
- Click **"🔒 Remote Off"** → Starts remote shell access

## Explore Tiles

**Click any tile** to open its detail drawer:

### 🏥 Health & Trust
- Trust score bar graph
- Guardian score bar graph
- System health bar graph
- Uptime percentage

### 🧠 Learning Status
- Toggle Google collector on/off
- Toggle Bing collector on/off
- Total artifacts count
- Pending ingestion count

### 🎯 Mission Registry
- List of all missions
- Status badges (open, in_progress, resolved)
- Creation and resolution dates

### 🔧 Self-Healing
- Total incidents count
- Active incidents count
- Resolved today count
- Success rate percentage
- Recent incident timeline

### 📸 Snapshots
- List of all snapshots
- Timestamp and label
- Size in MB
- Verification status

### 🔒 Remote Access
- Connection status indicator
- Start/stop remote access button
- Session ID
- Active sessions count
- Firefox agent status
- Last heartbeat timestamp

## Close Drawers

- Click **X** in top-right corner
- Click **outside the drawer**

## Navigate

**3 views available:**
- 🎯 **Overview** (default) - Tile grid
- 📊 **Dashboard** - Legacy detailed view
- 💬 **Chat** - AI conversation

## Data Flow

```
Load Page
    ↓
SystemOverview Component
    ↓
Fetch Data (parallel)
    ├─ GET /api/metrics/summary       → Health
    ├─ GET /api/learning/status       → Learning
    ├─ GET /api/missions/list         → Missions
    ├─ GET /api/incidents             → Incidents
    ├─ GET /api/incidents/stats       → Stats
    ├─ GET /api/snapshots/list        → Snapshots
    └─ GET /api/remote/status         → Remote
    ↓
Render 6 Tiles
    ↓
Auto-refresh every 15s
```

## Common Tasks

### Pause Learning
1. Click "⏸️ Pause Learning" in header
2. Status changes to orange "▶️ Resume Learning"
3. All tiles refresh

### Start Remote Access
1. Click "🔒 Remote Off" in header
2. Backend starts remote session
3. Tile updates to "🔓 Remote Active"

### View Mission Details
1. Click "🎯 Missions" tile
2. Drawer opens with mission list
3. See status, dates, subsystem info

### Check Healing Success Rate
1. Click "🔧 Self-Healing" tile
2. See success rate percentage
3. View recent incident timeline

### Browse Snapshots
1. Click "📸 Snapshots" tile
2. See all available snapshots
3. Check verification status

### Toggle Individual Collector
1. Click "🧠 Learning Status" tile
2. Drawer opens with collector controls
3. Toggle Google or Bing individually

## Troubleshooting

### Tile shows "0" or no data
- Backend endpoint may not exist yet
- Check console for API errors
- Verify backend is running on port 8000

### "Failed to load" error
- Backend endpoint returned 404/500
- Check network tab in browser DevTools
- Verify backend is accessible

### Controls don't work
- Check if loading spinner appears
- Look for error banner at top
- Check console for API errors

### Auto-refresh not working
- Component unmounted
- Check if interval is cleared
- Refresh page to restart

## Backend Requirements

Ensure these endpoints exist:

```bash
# Required endpoints (12 total)
GET  /api/metrics/summary         # Health metrics
GET  /api/learning/status          # Learning status
POST /api/learning/pause           # Pause learning
POST /api/learning/resume          # Resume learning
POST /api/learning/toggle/{type}   # Toggle collector
GET  /api/missions/list            # Missions list
GET  /api/incidents                # Incidents list
GET  /api/incidents/stats          # Healing stats
GET  /api/snapshots/list           # Snapshots list
GET  /api/remote/status            # Remote status
POST /api/remote/start             # Start remote
POST /api/remote/stop/{sessionId}  # Stop remote
```

## Development

### Modify Tiles
Edit `frontend/src/components/SystemOverview.tsx`
```tsx
// Around line 300 - Tile Grid section
<div className="overview-grid">
  {/* Add new tile here */}
</div>
```

### Modify Drawers
Edit detail components at bottom of `SystemOverview.tsx`
```tsx
// Around line 500+ - Detail Components
const HealthDetails: React.FC<...> = ({ health }) => (
  {/* Modify drawer content */}
);
```

### Modify Styles
Edit `frontend/src/components/SystemOverview.css`
```css
/* Tile styles */
.overview-tile { ... }

/* Drawer styles */
.detail-drawer { ... }
```

## What's Next?

### Recommended Workflow
1. ✅ Start backend: `python server.py`
2. ✅ Start frontend: `npm run dev`
3. ✅ Open http://localhost:5173
4. ✅ See System Overview tiles
5. ✅ Click tiles to explore
6. ✅ Use quick controls to test

### Test Checklist
- [ ] All tiles show data
- [ ] Click each tile opens drawer
- [ ] Quick controls work
- [ ] Auto-refresh updates data
- [ ] No console errors
- [ ] Responsive on mobile

---

**You're ready!** 🚀

The System Overview panel provides a comprehensive, interactive dashboard for monitoring and controlling all major Grace subsystems.
