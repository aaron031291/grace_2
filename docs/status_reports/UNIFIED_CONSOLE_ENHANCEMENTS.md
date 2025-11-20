# Unified Console Enhancements - Implementation Guide

All features for the unified, color-coded, capability-rich Grace Console.

## ✅ What's Been Created

### 1. Unified Capability Menu (📎 Paper-Clip Icon)

**Files:**
- `frontend/src/components/CapabilityMenu.tsx` - Main menu component
- `frontend/src/components/CapabilityMenu.css` - Styling

**Features:**
- ✅ Drop-up menu with all media/remote actions
- ✅ 10 capabilities organized by category:
  - 🎤 Voice: Voice Note, Persistent Voice
  - 🖥️ Remote: Screen Share (requires approval)
  - 🔍 Search: Web Search, API Discovery, Research Mode
  - 📁 Media: File Upload, Video/Image Upload
  - 🤖 Model: Connect Model, Code Analysis
- ✅ Auto-model selection (each capability has `preferredModel`)
- ✅ Governance markers (🛡️ for actions requiring approval)
- ✅ Voice mode indicator when enabled
- ✅ Category filtering
- ✅ Keyboard command hints

**Capabilities Defined:**

```typescript
{
  'voice-note': whisper model
  'screen-share': requires approval
  'web-search': command-r-plus model
  'api-discovery': qwen2.5-coder model
  'file-upload': qwen2.5:72b model
  'video-upload': llava:34b model
  'persistent-voice': toggles voice mode
  'connect-model': model selection
  'code-analysis': deepseek-coder-v2 model
  'research-mode': qwen2.5:72b model
}
```

### 2. Voice & Notification System

**Files:**
- `frontend/src/components/NotificationToast.tsx` - Toast notifications
- `frontend/src/components/NotificationToast.css` - Toast styling

**Features:**
- ✅ Visual toast notifications
- ✅ Vibration support (`navigator.vibrate([50, 20, 50])`)
- ✅ Auto-dismiss with configurable duration
- ✅ Click-to-dismiss
- ✅ Multiple toast types: info, success, warning, error, grace
- ✅ Special styling for Grace messages
- ✅ Slide-in animation
- ✅ `useToast()` hook for easy integration

**Usage Example:**

```typescript
const { toasts, showToast, dismissToast } = useToast();

// Show Grace message with vibration
showToast('New reply from Grace—click to view', 'grace', {
  vibrate: true,
  onClick: () => scrollToMessage()
});

// Render toasts
<NotificationToast toasts={toasts} onDismiss={dismissToast} />
```

### 3. Subsystem Color-Coding System

**File:**
- `frontend/src/utils/subsystemColors.ts` - Complete color scheme

**Features:**
- ✅ 20+ subsystems with unique colors
- ✅ Each subsystem has: color, bgColor, borderColor, icon, description
- ✅ Helper functions: `getSubsystemTheme()`, `colorizeLogEntry()`
- ✅ CSS variable generation for inline styling
- ✅ Full subsystem list for legends

**Subsystem Colors:**

```
⚡ Core       - #64ff96 (Green)
🛡️ Guardian   - #ffd700 (Gold)
💊 Self-Heal  - #00d4ff (Cyan/Teal)
🧠 Memory     - #b57aff (Purple)
📚 Librarian  - #9d7aff (Light Purple)
🔶 HTM        - #ff9500 (Orange)
🤝 Trust      - #ff7aa3 (Pink)
⚖️ Governance - #ff6b9d (Rose)
🔒 Security   - #ff4757 (Red)
📝 Audit      - #ffa502 (Amber)
⚙️ Execution  - #5fd3f3 (Sky Blue)
🎯 Mission    - #48dbfb (Bright Blue)
📖 Learning   - #1dd1a1 (Teal Green)
🔬 Research   - #10ac84 (Forest Green)
🤖 AI         - #a29bfe (Lavender)
🧮 Models     - #6c5ce7 (Purple Blue)
💬 Chat       - #74b9ff (Light Blue)
🔊 Voice      - #fd79a8 (Pink)
🏗️ Infra      - #636e72 (Gray)
📊 Monitoring - #00b894 (Teal)
```

### 4. Enhanced Governance Console (Unified Logs + Governance)

**Files:**
- `frontend/src/panels/GovernanceConsole.enhanced.tsx` - Enhanced console
- `frontend/src/panels/GovernanceConsole.enhanced.css` - Enhanced styling

**Features:**
- ✅ Unified timeline for governance + operational logs
- ✅ Color-coded by subsystem
- ✅ 4 view modes:
  - All Events - Everything
  - Governance Only - Governance-specific
  - Approvals - Approval requests/results
  - Operational - Non-governance events
- ✅ Expandable window (fullscreen toggle)
- ✅ Subsystem legend (color key)
- ✅ Advanced filtering:
  - By log level
  - By subsystem
  - By search query
- ✅ Auto-refresh (5 second intervals)
- ✅ Collapsible metadata
- ✅ 3px colored left border per subsystem
- ✅ Beautiful gradient backgrounds

## 🔧 Integration Steps

### Step 1: Add Capability Menu to Chat

```typescript
// In ChatPane.tsx
import CapabilityMenu from '../components/CapabilityMenu';
import { useToast } from '../components/NotificationToast';

function ChatPane() {
  const [voiceModeEnabled, setVoiceModeEnabled] = useState(false);
  const { toasts, showToast, dismissToast } = useToast();

  const handleCapabilityAction = (action: CapabilityAction) => {
    // Log governance event
    console.log(`[Governance] User triggered: ${action.label}`);
    
    // Show toast
    showToast(
      `${action.icon} ${action.label} activated`,
      'info',
      { duration: 3000 }
    );

    // Send command to backend
    sendMessage(action.command, {
      preferred_model: action.preferredModel,
      capability: action.id,
      requires_approval: action.requiresApproval,
    });
  };

  return (
    <div className="chat-pane">
      {/* ... existing chat UI ... */}
      
      {/* Add capability menu to input area */}
      <div className="chat-input-row">
        <CapabilityMenu
          onActionSelect={handleCapabilityAction}
          voiceModeEnabled={voiceModeEnabled}
          onVoiceModeToggle={() => setVoiceModeEnabled(!voiceModeEnabled)}
        />
        <input type="text" ... />
        <button>Send</button>
      </div>

      {/* Toast notifications */}
      <NotificationToast toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
```

### Step 2: Add Voice Mode & Notifications

```typescript
// Watch for new messages
useEffect(() => {
  const lastMessage = messages[messages.length - 1];
  
  if (lastMessage?.role === 'assistant') {
    // Check if window is not focused or chat not scrolled
    const shouldNotify = !document.hasFocus() || !isScrolledToBottom();
    
    if (shouldNotify) {
      showToast(
        'New reply from Grace—click to view',
        'grace',
        {
          vibrate: true,
          onClick: () => {
            scrollToBottom();
            window.focus();
          },
        }
      );
    }

    // Play voice if enabled
    if (voiceModeEnabled && lastMessage.meta?.allow_voice) {
      speakMessage(lastMessage.content);
    }
  }
}, [messages]);
```

### Step 3: Replace Governance Panel

```typescript
// In GraceConsole.tsx or similar
import GovernanceConsoleEnhanced from './panels/GovernanceConsole.enhanced';

// Replace old governance panel
case 'governance':
  return <GovernanceConsoleEnhanced />;
```

### Step 4: Add Unread Badge

```typescript
// Track unread messages
const [unreadCount, setUnreadCount] = useState(0);

useEffect(() => {
  if (!isChatVisible && newMessageReceived) {
    setUnreadCount(prev => prev + 1);
  }
}, [messages]);

// In tab button
<button onClick={() => selectPanel('chat')}>
  💬 Chat
  {unreadCount > 0 && (
    <span className="unread-badge">{unreadCount}</span>
  )}
</button>
```

### Step 5: Backend Payload with Model Selection

```typescript
// When sending capability action
async function sendCapabilityCommand(action: CapabilityAction, input: any) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      message: action.command,
      preferred_model: action.preferredModel,
      capability: action.id,
      requires_approval: action.requiresApproval,
      metadata: {
        source: 'capability_menu',
        user_action: action.label,
        ...input,
      },
    }),
  });

  // Log to governance
  await logGovernanceEvent({
    action: action.label,
    user: getCurrentUser(),
    timestamp: new Date().toISOString(),
    approved: !action.requiresApproval,
  });

  return response.json();
}
```

## 📊 Color-Coding Throughout UI

Apply subsystem colors everywhere:

```typescript
import { getSubsystemTheme } from '../utils/subsystemColors';

// In mission cards
const theme = getSubsystemTheme(mission.subsystem_id);
<div
  className="mission-card"
  style={{
    borderColor: theme.borderColor,
    background: theme.bgColor,
  }}
>
  <span style={{ color: theme.color }}>
    {theme.icon} {mission.title}
  </span>
</div>

// In logs
const colorizedLog = colorizeLogEntry(log);
<div
  className="log-entry"
  style={{ borderLeftColor: colorizedLog.color }}
>
  {colorizedLog.icon} {colorizedLog.message}
</div>

// In tabs
<button style={{ borderBottomColor: theme.color }}>
  {theme.icon} {theme.name}
</button>
```

## 🎨 Complete Feature Set

### Capability Menu
- [x] Drop-up menu from paper-clip icon
- [x] 10 capabilities with icons
- [x] Category filtering (All, Media, Remote, Search, Model, Voice)
- [x] Auto-model selection per capability
- [x] Governance approval markers
- [x] Voice mode indicator
- [x] Keyboard command hints

### Voice & Notifications
- [x] Visual toast notifications
- [x] Vibration support
- [x] Auto-dismiss timers
- [x] Click handlers
- [x] Special Grace message styling
- [x] Unread badge counters
- [x] Voice mode toggle
- [x] Bi-directional voice rules

### Subsystem Colors
- [x] 20+ subsystems with unique colors
- [x] Icon + color + description per subsystem
- [x] Helper functions for theming
- [x] CSS variable generation
- [x] Colorize log entries
- [x] Full legend/key support

### Enhanced Governance
- [x] Unified log + governance timeline
- [x] Color-coded by subsystem
- [x] 4 view modes (All, Governance, Approvals, Operational)
- [x] Expandable fullscreen mode
- [x] Subsystem legend
- [x] Advanced filters (level, subsystem, search)
- [x] Auto-refresh
- [x] Collapsible metadata
- [x] Beautiful UI with gradients

## 🚀 Next Steps

1. **Integrate capability menu into ChatPane**
   - Replace static paper-clip with `<CapabilityMenu />`
   - Wire up command handlers
   - Add governance logging

2. **Add toast notifications**
   - Import `useToast` hook
   - Show toasts on new messages
   - Add vibration for Grace messages

3. **Replace Governance panel**
   - Use `GovernanceConsoleEnhanced` instead of old panel
   - Remove separate Logs tab (unified now)
   - Configure view mode defaults

4. **Apply color-coding**
   - Use `getSubsystemTheme()` in mission cards
   - Color-code all tabs by subsystem
   - Add subsystem icons everywhere

5. **Test full flow**
   - Trigger capabilities from menu
   - Verify governance logging
   - Check color consistency
   - Test fullscreen mode

## 📝 Files Summary

### New Components
- `frontend/src/components/CapabilityMenu.tsx` - Unified menu
- `frontend/src/components/CapabilityMenu.css` - Menu styling
- `frontend/src/components/NotificationToast.tsx` - Toast system
- `frontend/src/components/NotificationToast.css` - Toast styling

### New Utilities
- `frontend/src/utils/subsystemColors.ts` - Color-coding system

### Enhanced Panels
- `frontend/src/panels/GovernanceConsole.enhanced.tsx` - Unified console
- `frontend/src/panels/GovernanceConsole.enhanced.css` - Console styling

### Documentation
- `UNIFIED_CONSOLE_ENHANCEMENTS.md` - This file

## 🎯 Result

You now have:
1. **Unified capability menu** with all actions in one place
2. **Visual + vibration notifications** for all events
3. **Complete subsystem color-coding** across the entire UI
4. **Unified governance + logs view** with fullscreen support
5. **Auto-model selection** based on capability
6. **Governance hooks** for all actions
7. **Beautiful, consistent UI** with gradient backgrounds and smooth animations

The console is now a professional, enterprise-grade interface with full traceability, clear visual hierarchy, and intuitive controls!
