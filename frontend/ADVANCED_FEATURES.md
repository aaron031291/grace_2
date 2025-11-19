# Advanced Chat Features

Historical transcripts, automated reminders, and multi-user routing are now fully integrated.

## 🔍 Historical Transcripts

Search past conversations with full context, actions, and logs.

### Features

- **Full-text search** across all conversation sessions
- **Context windows** - see messages before/after matches
- **Session browser** - view all chat sessions chronologically
- **Action history** - see what Grace did during conversations
- **One-click restore** - jump back into any past conversation

### Usage

**Open History Search:**
```typescript
// Click "🔍 History" button in sidebar
// Or programmatically:
<HistorySearch 
  isOpen={true} 
  onClose={() => setOpen(false)}
  onSelectSession={(sessionId) => loadSession(sessionId)}
/>
```

**Search Examples:**
- "What did Grace fix last Tuesday?"
- "deployment errors"
- "trust score changes"
- "approval required"

### API

```typescript
import { HistoryAPI } from './api/history';

// List all sessions
const sessions = await HistoryAPI.listSessions();

// Get specific session history
const messages = await HistoryAPI.getSessionHistory('sess_abc123', 50);

// Search across all conversations
const results = await HistoryAPI.searchHistory('deployment failed');

// Results include:
results.forEach(result => {
  console.log('Match:', result.message.content);
  console.log('Context:', result.context); // Surrounding messages
  console.log('Relevance:', result.relevance_score);
});
```

## ⏰ Automated Reminders

Create reminders and scheduled tasks via natural language chat commands.

### Features

- **Natural language parsing** - "remind me to X tomorrow"
- **Multiple time formats** - tomorrow, today, in 2 hours
- **Notification delivery** - via WebSocket notification stream
- **Task integration** - creates actual background tasks

### Usage

**Create Reminder (Chat Command):**
```
remind me to review the CRM deploy tomorrow
remind me to check logs in 2 hours
remind me to follow up with the team today
```

**How it Works:**
1. ChatPanel detects "remind me to..." pattern
2. Parses task and time (tomorrow, today, in X hours/days)
3. Calls `/api/reminders/create` endpoint
4. Grace sends notification at scheduled time via WebSocket

**Supported Time Formats:**
- `tomorrow` - Next day at 9 AM
- `today` - Today at 5 PM
- `in 2 hours` - 2 hours from now
- `in 3 days` - 3 days from now
- `in 30 minutes` - 30 minutes from now

### API

```typescript
import { RemindersAPI } from './api/reminders';

// Create reminder manually
const reminder = await RemindersAPI.createReminder({
  user_id: 'user',
  message: 'Review CRM deployment',
  scheduled_time: new Date('2024-01-16T09:00:00').toISOString(),
  metadata: { priority: 'high' }
});

// List reminders
const reminders = await RemindersAPI.listReminders('user', 'pending');

// Cancel reminder
await RemindersAPI.cancelReminder('reminder_abc123');

// Parse natural language
const parsed = RemindersAPI.parseReminderCommand(
  'remind me to check logs tomorrow'
);
// Returns: { message: 'check logs', scheduled_time: '...', ... }
```

### Notification Format

When a reminder fires, you receive:

```json
{
  "message": "⏰ Reminder: Review CRM deployment",
  "timestamp": "2024-01-16T09:00:00Z",
  "badge": "⏰",
  "level": "info",
  "source": "reminders",
  "data": {
    "reminder_id": "reminder_abc123",
    "original_message": "Review CRM deployment"
  }
}
```

## 👥 Multi-User Routing

User presence tracking and @mentions for team collaboration.

### Features

- **Presence tracking** - see who's online
- **@mentions** - notify specific users
- **Heartbeat system** - automatic presence updates
- **Targeted approvals** - route to right person
- **Activity awareness** - see what others are viewing

### Usage

**User Presence Bar:**

Automatically shown when multiple users are active. Shows:
- Online/away status (🟢/🟠)
- User names
- Current activity

**@Mentions in Chat:**
```
Hey @john can you review this deployment?
@sarah I need approval for the database migration
```

When you mention someone:
1. ChatPanel detects `@username` pattern
2. Sends notification to that user via backend
3. User receives real-time WebSocket notification
4. Notification includes message context and session link

### API

```typescript
import { PresenceAPI } from './api/presence';

// Join session (automatic on app load)
await PresenceAPI.joinSession('user123', 'John Doe');

// Send heartbeat (every 30s)
await PresenceAPI.sendHeartbeat('user123');

// Get active users
const users = await PresenceAPI.getActiveUsers();
users.forEach(user => {
  console.log(`${user.user_name}: ${user.status}`);
});

// Parse mentions from text
const mentions = PresenceAPI.parseMentions('Hey @john and @sarah');
// Returns: ['john', 'sarah']

// Send mention notification
await PresenceAPI.notifyMention('john', 'Can you review?', 'sess_123');
```

### Presence System

**Backend Tracking:**
- Heartbeats every 30 seconds
- Stale sessions removed after 2 minutes
- View tracking (what file/table user is seeing)
- Edit locks (exclusive editing)

**Frontend Integration:**
```typescript
// Automatic in AppChat
<UserPresenceBar currentUser="user" />

// Shows:
// 👥 Active: 🟢 John (you) | 🟢 Sarah | 🟠 Mike (away)
```

## 🔗 Integration Example

All three features working together:

```typescript
function EnhancedChat() {
  const [historyOpen, setHistoryOpen] = useState(false);
  
  return (
    <div>
      {/* Main chat with reminders and mentions */}
      <ChatPanel />
      
      {/* User presence (shows when others online) */}
      <UserPresenceBar currentUser="user" />
      
      {/* History search modal */}
      <HistorySearch 
        isOpen={historyOpen}
        onClose={() => setHistoryOpen(false)}
      />
      
      {/* Sidebar button */}
      <button onClick={() => setHistoryOpen(true)}>
        🔍 Search History
      </button>
    </div>
  );
}
```

## 💬 Chat Examples

### History Search
```
User: What did Grace fix last Tuesday?
[Opens history search automatically or click 🔍 History button]
Results: 
  - "Fixed CRM deployment error" (95% match)
  - "Resolved database migration" (87% match)
```

### Reminders
```
User: remind me to review the deploy tomorrow
Grace: ✅ Reminder created: "review the deploy" scheduled for 1/16/2024 9:00 AM

[Tomorrow at 9 AM via notification stream]
⏰ Reminder: review the deploy
```

### Mentions
```
User: Hey @sarah can you approve this database migration?
Grace: Message sent, @sarah has been notified

[Sarah receives notification]
💬 @john mentioned you: "can you approve this database migration?"
```

## 🎯 Use Cases

### For Solo Users
- **History:** Find when you discussed specific topics
- **Reminders:** Schedule follow-ups and reviews
- **Presence:** Track your own session continuity

### For Teams
- **History:** Share context from past conversations
- **Reminders:** Coordinate scheduled reviews
- **Presence:** Know who's available for approvals
- **Mentions:** Route questions to right person

## 🔧 Configuration

### Enable Multi-User Mode

In your `.env.local`:
```bash
VITE_MULTI_USER=true
VITE_USER_ID=john    # Your user ID
```

### Backend Requirements

Ensure these endpoints are available:
- `/api/chat/history/:session_id`
- `/api/chat/sessions`
- `/api/reminders/create`
- `/api/presence/join`
- `/api/presence/heartbeat/:user_id`
- `/api/presence/active`

## 📊 Analytics

Track usage:
```typescript
// History searches per user
// Most searched terms
// Reminder completion rate
// Mention frequency
```

## 🚀 Future Enhancements

- [ ] **Smart search** - semantic search vs. keyword
- [ ] **Recurring reminders** - daily/weekly schedules
- [ ] **Presence insights** - availability patterns
- [ ] **Mention threading** - conversation branching
- [ ] **History export** - download as markdown/PDF
- [ ] **Cross-session search** - find patterns across sessions

## 📝 Testing

Smoke tests included in [tests/chat.spec.ts](./tests/chat.spec.ts):

```bash
npm run test:smoke
```

Tests verify:
- History search opens/closes
- Reminders parse correctly
- Mentions detected
- Presence bar renders

## 🎉 Benefits

**Productivity:**
- No more "What was that thing Grace did last week?"
- Automated follow-ups reduce mental load
- Team coordination without context switching

**Governance:**
- Full audit trail via searchable history
- Scheduled compliance reminders
- Approval routing to correct stakeholders

**Collaboration:**
- Real-time presence awareness
- Direct @mentions for urgent matters
- Shared conversation history

---

**Ready to use!** All features are integrated and production-ready.
