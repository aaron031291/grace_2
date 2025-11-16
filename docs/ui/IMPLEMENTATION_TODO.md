# Unified Console - Implementation TODO

## 🎯 Backend Tasks (Required First)

### API Endpoints
- [ ] Create `/api/approvals/grant-all` - Single approval endpoint
- [ ] Create `/api/logs/recent` - Recent logs endpoint
- [ ] Create `/api/logs/stream` (WebSocket) - Real-time log streaming
- [ ] Create `/api/missions/active` - Active missions list
- [ ] Create `/api/missions/{id}` - Mission details
- [ ] Create `/ws/missions` (WebSocket) - Mission updates
- [ ] Create `/api/domains/{id}/dashboard` - Domain dashboard data
- [ ] Create `/api/reports/daily-brief` - Daily summary
- [ ] Create `/api/reports/trends` - Trend data

### Backend Services
- [ ] Wire Domain Event Bus to WebSocket for logs
- [ ] Ensure Mission Control API is accessible
- [ ] Set up Telemetry WebSocket streams
- [ ] Configure single approval manager

---

## 🖥️ Frontend Tasks

### Phase 1: Core Layout (Week 1)
- [ ] Set up React/Svelte project in `frontend/console/`
- [ ] Create `ConsoleLayout` component (3-pane split)
- [ ] Implement `LogsPane` component
  - [ ] Color-coded log rendering
  - [ ] Domain filter dropdown
  - [ ] Log level filter
  - [ ] Auto-scroll toggle
  - [ ] Search/grep functionality
- [ ] Implement `ChatPane` component
  - [ ] Text input/output
  - [ ] Markdown rendering
  - [ ] Code syntax highlighting
  - [ ] Send button + Enter key
- [ ] Implement `TaskManagerPane` component
  - [ ] Mission cards
  - [ ] Status indicators
  - [ ] Click to open details
- [ ] Set up WebSocket hooks
  - [ ] `useWebSocket('/ws/logs')`
  - [ ] `useWebSocket('/ws/missions')`

### Phase 2: Dynamic Workspaces (Week 2)
- [ ] Create `WorkspaceContainer` component
- [ ] Implement workspace types:
  - [ ] `DomainDashboard` - Domain health/metrics
  - [ ] `MissionDetail` - Mission deep-dive
  - [ ] `CodeView` - File viewer with syntax highlighting
  - [ ] `DataExplorer` - Query results, database browser
  - [ ] `ChartView` - Time-series charts
- [ ] Add tab bar for workspace switching
- [ ] Implement spawn/close/minimize logic
- [ ] Add workspace persistence (localStorage)
- [ ] Wire chat commands to workspace spawning
  - [ ] Parse "open dashboard X" → spawn workspace
  - [ ] Parse "show mission Y" → spawn workspace

### Phase 3: File Explorer (Week 3)
- [ ] Build `FileExplorer` component
  - [ ] Category tree navigation
  - [ ] File list with metadata cards
  - [ ] Drag & drop upload zone
  - [ ] Search bar with RAG integration
  - [ ] Filter controls
- [ ] Implement file actions
  - [ ] Preview modal
  - [ ] Notes editor
  - [ ] Re-ingest trigger
  - [ ] Delete with confirmation
- [ ] Build upload flows
  - [ ] Single file upload
  - [ ] Bulk upload
  - [ ] Text paste & ingest
  - [ ] Voice recording
- [ ] Add governance integration
  - [ ] Access control checks
  - [ ] Audit logging
  - [ ] Credential vault for remote files

### Phase 4: Additional Panels (Week 4)
- [ ] Build `MissionDashboard` component
  - [ ] Card/table view
  - [ ] Active/Proactive/Follow-up tabs
  - [ ] Drill-down to details
- [ ] Build `AlertsPanel` component
  - [ ] Alert cards
  - [ ] Acknowledge button
  - [ ] "Ask Grace" quick action
  - [ ] Filter by channel
- [ ] Build `DailyBrief` component
  - [ ] Auto-generated summary
  - [ ] Trend charts (mission counts, MTTR, success rate)
  - [ ] Export to PDF/JSON
- [ ] Build `CommandPalette` component
  - [ ] Fuzzy search
  - [ ] Keyboard navigation
  - [ ] Recent commands
  - [ ] Quick actions list

### Phase 4: Polish (Week 4)
- [ ] Add keyboard shortcuts
  - [ ] Cmd/Ctrl+K: Command Palette
  - [ ] Cmd/Ctrl+L: Focus Logs
  - [ ] Cmd/Ctrl+J: Focus Chat
  - [ ] Cmd/Ctrl+M: Focus Missions
  - [ ] Cmd/Ctrl+W: Close current workspace
- [ ] Implement themes (dark/light)
- [ ] Add loading states
- [ ] Add error boundaries
- [ ] Optimize re-renders
- [ ] Add mobile responsiveness
- [ ] User preferences panel
- [ ] Add onboarding tour

---

## 🧪 Testing Tasks

### Unit Tests
- [ ] Test LogsPane filtering
- [ ] Test ChatPane message rendering
- [ ] Test TaskManager mission cards
- [ ] Test WorkspaceContainer spawn/close
- [ ] Test CommandPalette search

### Integration Tests
- [ ] Test WebSocket connection handling
- [ ] Test workspace spawning from chat
- [ ] Test approval flow end-to-end
- [ ] Test mission status updates

### E2E Tests
- [ ] Test full user flow: login → approve → chat → mission
- [ ] Test workspace spawning and navigation
- [ ] Test real-time log streaming
- [ ] Test command palette actions

---

## 📦 Dependencies to Install

### Frontend
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwindcss": "^3.3.0",
    "monaco-editor": "^0.44.0",
    "recharts": "^2.9.0",
    "socket.io-client": "^4.5.0",
    "@tanstack/react-query": "^5.0.0",
    "cmdk": "^0.2.0",
    "zustand": "^4.4.0"
  }
}
```

### Backend
```python
# Already have most dependencies
# May need:
pip install python-socketio
pip install aiofiles
```

---

## 🎯 MVP (Minimum Viable Product)

**Week 1 Goal**: Working console with basic functionality

**Must Have**:
1. ✅ 3-pane layout (Logs, Chat, Tasks)
2. ✅ Logs pane showing real-time logs
3. ✅ Chat pane accepting/displaying messages
4. ✅ Task Manager showing active missions
5. ✅ Command Palette with "Approve All" action
6. ✅ Single approval endpoint working

**Nice to Have** (can add later):
- Dynamic workspaces
- Daily brief
- Alerts panel
- Advanced filtering

---

## 🚀 Quick Start for Implementation

### Backend First
```bash
# 1. Create approval endpoint
touch backend/routes/approval_api.py
# Implement /api/approvals/grant-all

# 2. Add to main.py
# app.include_router(approval_router)

# 3. Test
curl -X POST http://localhost:8017/api/approvals/grant-all
```

### Frontend Next
```bash
# 1. Create frontend console app
cd frontend
npx create-react-app console
cd console
npm install tailwindcss monaco-editor recharts socket.io-client

# 2. Build components
mkdir src/components/Console
touch src/components/Console/LogsPane.tsx
touch src/components/Console/ChatPane.tsx
touch src/components/Console/TaskManagerPane.tsx

# 3. Run dev server
npm start
```

---

## 📊 Progress Tracking

**Track progress in**: `docs/ui/CONSOLE_PROGRESS.md`

**Update after each task completed**

---

**Next Step**: Create the `/api/approvals/grant-all` backend endpoint, then start frontend development.
