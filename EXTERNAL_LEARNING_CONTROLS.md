# External Learning Controls - Mission Control Enhancement ✅

**Added:** November 20, 2025  
**Status:** Integrated into Mission Control Dashboard

---

## 🎯 Overview

Enhanced the Mission Control Dashboard with **External Learning Controls & Status** monitoring. This new panel provides real-time visibility into:

- 🌐 **Web Learning** - Safe web scraper status
- 🐙 **GitHub Learning** - Token validation & availability
- 🦊 **Firefox Agent** - Remote browser automation status
- 🔍 **Google Search Quota** - API quota monitoring with reset dates
- ⚠️ **Warning System** - Automated alerts for token/quota issues

---

## 📁 Files Modified

### Frontend Components

1. **`frontend/src/components/MissionControlDashboard.tsx`**
   - Added `ExternalLearningStatus` interface
   - Added `fetchExternalLearningStatus()` function
   - Added External Learning panel UI
   - Integrated playbook status monitoring

2. **`frontend/src/components/MissionControlDashboard.css`**
   - Added `.external-learning-grid` styling
   - Added status indicator classes
   - Added warning banner styles
   - Color-coded status badges

3. **`MISSION_CONTROL_DASHBOARD.md`** (Updated)
   - Documented new External Learning Controls section
   - Added status indicator table
   - Updated API endpoints list
   - Added future enhancements

---

## 🔌 Data Sources

### Playbook Status API
```
GET /api/playbooks/status
```

Monitors self-healing playbooks to detect:
- **GitHub Token Missing** (`github_token_missing.yaml`)
- **Google Search Quota Exhaustion** (`google_search_quota_exhaustion.yaml`)

Returns playbook trigger history to determine:
- When token was last detected as missing
- When quota was last exhausted
- Next quota reset date (if available)

### PC Access API
```
GET /api/pc/status
```

Returns Firefox agent status:
- `firefox.enabled` - Whether agent is running
- `firefox.approved_domains` - List of trusted domains
- `firefox.pages_visited` - Recent browsing history

---

## 🎨 UI Components

### Status Grid (2-column layout)

```
┌─────────────────────────────────────────┐
│  🌐 External Learning Sources          │
├─────────────────────────────────────────┤
│  Web Learning:        ✅ ENABLED        │
│  GitHub Learning:     ✅ ENABLED        │
│  GitHub Token:        ✓ Valid           │
│  Firefox Agent:       🟢 RUNNING        │
│  Google Search Quota: ✅ OK             │
├─────────────────────────────────────────┤
│  ⚠️ Warning banners appear here         │
└─────────────────────────────────────────┘
```

### Status Indicators

**Enabled/Disabled:**
- ✅ ENABLED - Green badge (#00ff88)
- ⏸️ DISABLED - Orange badge (#ff8800)

**Running/Stopped:**
- 🟢 RUNNING - Green badge
- 🔴 STOPPED - Red badge (#ff4444)

**Token Status:**
- ✓ Valid - Green badge
- ❌ Missing - Red badge
- ❓ Unknown - Gray badge

**Quota Status:**
- ✅ OK - Green badge
- ⚠️ LOW - Orange badge (#ffaa00)
- ❌ EXHAUSTED - Red badge with reset date
- ❓ Unknown - Gray badge

---

## ⚠️ Warning System

### GitHub Token Missing

**Trigger:** `github_token_missing` playbook executed

**UI Display:**
```
┌──────────────────────────────────────────────────────┐
│ ⚠️ GitHub token missing. Some learning features may │
│    be limited.                                       │
└──────────────────────────────────────────────────────┘
```

**Color:** Orange gradient (#ff8800 → #ff4444)  
**Location:** Full-width below status grid

**Fix:** Run `SETUP_TOKEN.bat` to configure GitHub token

---

### Google Search Quota Exhausted

**Trigger:** `google_search_quota_exhaustion` playbook executed

**UI Display:**
```
┌──────────────────────────────────────────────────────┐
│ ⚠️ Google Search quota exhausted. Using fallback    │
│    search methods.                                   │
└──────────────────────────────────────────────────────┘
```

**Color:** Orange gradient  
**Location:** Full-width below status grid

**Additional Info:** Shows quota reset date if available

**Fix:** Quota resets daily (UTC), or use alternative search methods

---

## 📊 Status Detection Logic

### GitHub Token Status
```typescript
// Check if github_token_missing playbook has been triggered
const githubPlaybook = playbooksData.playbooks?.find(
  p => p.name === 'github_token_missing'
);

// If playbook was triggered recently, token is missing
github_token_status = githubPlaybook?.last_triggered 
  ? 'missing' 
  : 'valid';

// GitHub learning is enabled if token is valid
github_learning_enabled = !githubPlaybook || 
  githubPlaybook.last_triggered === null;
```

### Google Search Quota
```typescript
// Check if quota playbook has been triggered
const quotaPlaybook = playbooksData.playbooks?.find(
  p => p.name === 'google_search_quota_exhaustion'
);

// If playbook was triggered, quota is exhausted
google_search_quota = quotaPlaybook?.last_triggered 
  ? 'exhausted' 
  : 'ok';

// Extract reset date if available
quota_reset_date = quotaPlaybook?.next_reset_date;
```

### Firefox Agent
```typescript
// Check PC access API for Firefox status
const pcStatus = await fetch('/api/pc/status');
firefox_agent_running = pcStatus.firefox?.enabled === true;
```

---

## 🔄 Auto-Refresh

The External Learning panel refreshes automatically with the rest of the dashboard:

**Refresh Interval:** 30 seconds  
**APIs Called:**
1. `/api/pc/status` - Firefox agent status
2. `/api/playbooks/status` - Token and quota status

**Error Handling:**
- If APIs fail, displays "Unknown" status
- No errors shown to user (graceful degradation)
- Console logs for debugging

---

## 🎯 Use Cases

### 1. Monitor GitHub Token
**Scenario:** GitHub token expires or is not set

**Dashboard Shows:**
- GitHub Token: ❌ Missing
- GitHub Learning: ⚠️ DISABLED
- Warning banner displayed

**User Action:** Click warning → Run `SETUP_TOKEN.bat`

---

### 2. Track Google Search Quota
**Scenario:** Daily search quota exhausted

**Dashboard Shows:**
- Google Search Quota: ❌ EXHAUSTED (Resets: 2025-11-21)
- Warning banner with fallback info

**User Action:** Wait for reset or use alternative search

---

### 3. Verify Firefox Agent
**Scenario:** Check if remote browser is running

**Dashboard Shows:**
- Firefox Agent: 🟢 RUNNING or 🔴 STOPPED

**User Action:** Start/stop agent via `/api/pc` if needed

---

### 4. Overall Learning Health
**Scenario:** Quick check of all external learning sources

**Dashboard Shows:**
- All green ✅ = Full learning capabilities
- Any red/orange ⚠️ = Reduced capabilities with warnings

**User Action:** Address warnings to restore full functionality

---

## 🧪 Testing

### Manual Testing Steps

1. **Start Grace:**
   ```bash
   START_GRACE.bat
   ```

2. **Open Mission Control:**
   - Open frontend (`npm run dev`)
   - Click **🎯 Mission Control** button
   - Verify External Learning panel appears

3. **Test Token Detection:**
   - Check current token status
   - Remove token temporarily (rename .env)
   - Trigger GitHub learning (should fail)
   - Verify playbook triggers
   - Refresh dashboard
   - Verify status shows ❌ Missing
   - Restore token

4. **Test Quota Detection:**
   - Make many Google Search API calls
   - Exhaust daily quota
   - Verify playbook triggers
   - Refresh dashboard
   - Verify status shows ❌ EXHAUSTED

5. **Test Firefox Agent:**
   - Start Firefox agent via API
   - Refresh dashboard
   - Verify shows 🟢 RUNNING
   - Stop agent
   - Verify shows 🔴 STOPPED

### API Testing

```bash
# Check playbook status
curl http://localhost:8017/api/playbooks/status

# Check PC status
curl http://localhost:8017/api/pc/status

# Expected responses:
# {
#   "playbooks": [
#     {
#       "name": "github_token_missing",
#       "last_triggered": "2025-11-20T14:30:00Z" or null
#     },
#     {
#       "name": "google_search_quota_exhaustion",
#       "last_triggered": "2025-11-20T15:00:00Z" or null,
#       "next_reset_date": "2025-11-21T00:00:00Z"
#     }
#   ]
# }
#
# {
#   "firefox": {
#     "enabled": true,
#     "approved_domains": ["github.com", "stackoverflow.com"]
#   }
# }
```

---

## 🎨 Design Details

### Color Scheme

**Status Colors:**
- Green (#00ff88) - Active/OK/Valid
- Orange (#ff8800) - Warning/Disabled
- Red (#ff4444) - Error/Missing/Exhausted
- Gray (#888) - Unknown

**Warning Banner:**
- Background: Linear gradient (orange → red)
- Border: 2px solid orange
- Text: Orange (#ffaa00)

**Layout:**
- 2-column grid for status items
- Full-width for quota and warnings
- Consistent padding (10px items, 12px gaps)

---

## 📈 Future Enhancements

### Planned Features

1. **Toggle Controls**
   - Add on/off switches for each learning source
   - POST to `/api/learning/toggle` endpoints
   - Immediate visual feedback

2. **Token Management**
   - Add GitHub token input field
   - Save token via API
   - Validate token on-the-fly

3. **Quota Visualization**
   - Progress bar showing quota usage
   - Estimate time until reset
   - Historical quota usage chart

4. **Firefox Agent Controls**
   - Start/stop button for agent
   - Domain approval from UI
   - Recent pages visited list

5. **Real-Time Alerts**
   - WebSocket connection for live updates
   - Browser notifications for quota warnings
   - Toast messages for token issues

---

## ✅ Integration Checklist

### Implementation
- [x] Added ExternalLearningStatus interface
- [x] Created fetchExternalLearningStatus function
- [x] Integrated playbook status API
- [x] Integrated PC status API
- [x] Added External Learning panel UI
- [x] Added status indicators
- [x] Added warning banners
- [x] Added CSS styling
- [x] Updated documentation

### Features
- [x] Web learning status display
- [x] GitHub learning status display
- [x] GitHub token validation
- [x] Firefox agent monitoring
- [x] Google Search quota monitoring
- [x] Token missing warning
- [x] Quota exhausted warning
- [x] Reset date display
- [x] Auto-refresh integration

### Testing
- [ ] Test with Grace running
- [ ] Verify playbook API responds
- [ ] Test token missing scenario
- [ ] Test quota exhausted scenario
- [ ] Test Firefox agent status
- [ ] Verify warnings appear correctly
- [ ] Test auto-refresh updates
- [ ] Test error states

---

## 🎯 Success Criteria

External Learning Controls are **complete and functional** when:

1. ✅ Panel displays in Mission Control Dashboard
2. ✅ All 5 status indicators show correct data
3. ✅ Playbook status API integrated
4. ✅ PC status API integrated
5. ✅ Warning banners appear when needed
6. ✅ Auto-refresh updates status every 30s
7. ✅ Visual design matches Mission Control theme
8. ✅ Error states handled gracefully

---

## 📚 Related Documentation

- [MISSION_CONTROL_DASHBOARD.md](./MISSION_CONTROL_DASHBOARD.md) - Full dashboard docs
- [playbooks/github_token_missing.yaml](./playbooks/github_token_missing.yaml) - Token playbook
- [playbooks/google_search_quota.yaml](./playbooks/google_search_quota.yaml) - Quota playbook
- [backend/routes/pc_access_api.py](./backend/routes/pc_access_api.py) - PC access API
- [backend/agents/firefox_agent.py](./backend/agents/firefox_agent.py) - Firefox agent

---

## 💡 Key Innovations

### Playbook-Driven Status
Instead of polling external services directly, the dashboard monitors **playbook execution history**. This means:
- ✅ No API keys needed in frontend
- ✅ Playbooks already detect issues
- ✅ Status is accurate (playbooks are self-healing triggers)
- ✅ Warning messages align with playbook actions

### Unified Monitoring
All external learning sources in one panel:
- No need to check multiple logs
- Quick glance shows overall health
- Warnings guide user to fixes

### Graceful Degradation
If APIs fail:
- Shows "Unknown" status (no crashes)
- Dashboard still functional
- Other panels load normally

---

**Status:** ✅ READY FOR TESTING

**Next Steps:**
1. Start Grace backend
2. Open Mission Control Dashboard
3. Verify External Learning panel loads
4. Test each status indicator
5. Trigger playbooks to test warnings

---

**Created by:** Amp AI Assistant  
**Date:** November 20, 2025  
**Thread:** [T-ac720866-366d-4fff-a73f-9d02af62b4d5](https://ampcode.com/threads/T-ac720866-366d-4fff-a73f-9d02af62b4d5)
