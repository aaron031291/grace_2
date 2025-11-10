# Grace GPT Interface Guide

## Overview

The new GPT-style interface (`GraceGPT`) provides a modern, user-friendly chat experience while preserving Grace's full autonomous capabilities. It combines familiar chat UX with real-time monitoring, explainability, and human-in-the-loop controls.

## Features

### 1. **Conversation Layout**
- **Chat Bubbles**: Clean message bubbles with avatars, timestamps, and domain tags
- **Markdown Rendering**: Full support for formatted text, code blocks, and links
- **Typing Indicators**: Visual feedback when Grace is processing
- **Message Types**:
  - User messages (right-aligned, purple)
  - Assistant messages (left-aligned, Grace avatar)
  - System messages (cyan border)
  - Subagent notifications (green border)

### 2. **Command Palette**
- Press `/` in empty input to open slash-command autocomplete
- Available commands:
  - `/self_heal` - Trigger self-healing analysis
  - `/meta` - Run meta-loop cycle
  - `/playbook` - Execute domain playbook
  - `/scan` - Security vulnerability scan
  - `/learn` - Knowledge discovery cycle
  - `/status` - System health status

### 3. **Context Sidebar** (Left Panel)
- **Domain Selector**: Switch between domains (all, chat, self_heal, meta_loop, knowledge, security, transcendence, resource, core)
- **Controls**:
  - Review mode toggle - Approve actions before execution
  - Activity feed toggle - Show/hide live telemetry
- **Subagents Monitor**: Real-time view of active subagents with progress bars
- **Theme Toggle**: Switch between dark and light modes
- **Quick Logout**: One-click session termination

### 4. **Live Telemetry Activity Rail** (Right Panel)
- Color-coded severity levels:
  - **Info** (cyan): Normal operations
  - **Warning** (yellow): Requires attention
  - **Critical** (red): Urgent issues
- Event types:
  - 🧠 Meta-loop cycles
  - 🔧 Self-heal actions
  - 📊 Resource adjustments
  - 📋 Playbook executions
  - ⚠️ Alerts
- Automatically scrolls to show latest events
- Timestamp for each activity

### 5. **Explainability Hooks**
- **Explain Button**: Click on any assistant message with metadata
- Shows:
  - Root causes
  - Confidence levels
  - Safeguards applied
  - Decision rationale
- Logged back into transcript for audit trail

### 6. **Human Override & Approval**
- **Review Mode**: When enabled, Grace requests approval for sensitive playbooks
- **Approval Modal**: Shows action details with approve/decline buttons
- **Response Options**: Quick-reply buttons for Grace's questions
- **Manual Intervention**: Interrupt or guide autonomous actions

### 7. **Visual Polish**
- **Dark/Light Themes**: Customizable appearance
- **Smooth Transitions**: Animated message entry, sidebar slides, modal fades
- **Keyboard Shortcuts**:
  - `Enter` - Send message
  - `Shift+Enter` - New line
  - `/` - Open command palette
- **Persistent History**: All messages saved per session
- **Responsive Design**: Adapts to mobile/tablet screens

## WebSocket Connections

The interface maintains two WebSocket connections:

1. **Proactive Messaging** (`ws://localhost:8000/api/proactive/ws`)
   - Receives Grace's autonomous notifications
   - Handles questions requiring user response
   - Streams ideas and consensus requests

2. **Subagent Monitoring** (`ws://localhost:8000/api/subagents/ws`)
   - Real-time subagent status updates
   - Spawn/completion events
   - Progress tracking

## Usage Examples

### Basic Chat
```
User: Analyze system health
Grace: Running diagnostics across all domains...
[Activity Rail shows: 🔧 Self-heal analysis started]
Grace: ✅ All systems nominal. Self-heal score: 98%
```

### Using Slash Commands
```
User: /self_heal analyze memory leaks
[Command palette opens with autocomplete]
Grace: Initiating self-heal playbook for memory analysis...
[Subagent spawned: memory_analyzer - 45% complete]
```

### Review Mode
```
[Review Mode Enabled]
Grace: I'd like to restart the ML service to apply optimizations.
[Approval Modal appears]
Action: Restart ML Service
Impact: 30s downtime
[Approve] [Decline]
```

### Explainability
```
Grace: Increased cache TTL from 5m to 15m
[Explain button visible]
User: [clicks Explain]
Modal shows:
- Cause: 87% cache hit rate observed
- Confidence: 0.92
- Safeguards: Rollback on error spike
```

## Architecture

```
┌─────────────┐    WebSocket     ┌──────────────┐
│  GraceGPT   │ ◄──────────────► │   Backend    │
│  Component  │                  │  FastAPI     │
└─────────────┘                  └──────────────┘
      │                                 │
      ├─ Sidebar                        ├─ Proactive WS
      ├─ Chat                            ├─ Subagent WS
      └─ Activity Rail                   └─ Event Bus
```

## State Management

- **Messages**: Array of timestamped chat turns
- **Activity**: Ring buffer (max 50 events)
- **Subagents**: Live map updated via WS
- **Domain**: User-selected or auto-switched
- **Theme**: Persisted to localStorage
- **Review Mode**: Local toggle, sent to backend

## Customization

### Adding New Slash Commands

Edit `SLASH_COMMANDS` in `GraceGPT.tsx`:
```typescript
{ cmd: '/my_command', desc: 'Command description', domain: 'my_domain' }
```

### Custom Activity Types

Add to `ActivityEvent` type and update icon mapping:
```typescript
type: 'my_event'
// In activity icon rendering:
act.type === 'my_event' ? '🎯' : '...'
```

### Theme Colors

Modify CSS variables in `GraceGPT.css`:
```css
.grace-gpt {
  --accent-purple: #7b2cbf;
  --accent-cyan: #00d4ff;
  /* ... */
}
```

## Migration from Old UI

The legacy chat interface (`App.tsx` default chat) is preserved. Users can switch via the `⚡ GPT Chat` nav button. Both share the same backend and authentication.

## Next Steps (Future Enhancements)

1. **Advanced Telemetry**: Causal graph visualization, resource heatmaps
2. **Search History**: Full-text search across past conversations
3. **Voice Input**: Audio messages with speech-to-text
4. **Multi-Session**: Tab management for parallel conversations
5. **Export**: Download chat transcripts as Markdown/JSON
6. **Collaboration**: Share sessions with other operators

## Troubleshooting

- **WebSocket disconnects**: Check backend is running on port 8000
- **No slash commands**: Press `/` in empty input field
- **Missing activity**: Toggle activity rail visibility in sidebar
- **Theme not persisting**: Check localStorage permissions
- **Subagents not showing**: Ensure subagent WS connection is active (check browser console)

## Support

For issues or feature requests, see the main Grace documentation or consult the development team.
