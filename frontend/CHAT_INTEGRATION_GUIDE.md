# Chat Integration Guide

Complete implementation of Grace chat with conversation state, attachments, citations, and workspace integration.

## Architecture

```
┌──────────────┐
│  ChatPane    │  UI Component
│  Component   │  - Message bubbles
└──────┬───────┘  - Input area
       │          - Citation pills
       ▼
┌──────────────┐
│  useChat     │  React Hook
│  Hook        │  - Conversation state
└──────┬───────┘  - Message persistence
       │          - Send/clear actions
       ▼
┌──────────────┐
│  chatApi     │  API Service
│  Service     │  - POST /api/chat
└──────────────┘  - Upload attachments
       │          - Parse responses
       ▼
   Backend API
```

## Features Implemented

### ✅ 1. Conversation State Management
- Messages stored in array: `{ role, content, timestamp, metadata, attachments }`
- Persisted to localStorage automatically
- Optional backend history loading
- Clear conversation functionality

### ✅ 2. Message Sending
- POST to `/api/chat` with message and context
- Automatic attachment upload before sending
- Loading state during API call
- Error handling with error messages

### ✅ 3. Attachment Handling
- File upload via file picker
- Multiple file support
- Upload to `/api/ingest/upload` first
- Include artifact references in message
- Display attached files in message bubbles

### ✅ 4. Citation Rendering
- Extract citations from response metadata
- Color-coded citation pills by type:
  - 🎯 **Mission** - Orange
  - 📈 **KPI** - Cyan
  - 📄 **Document** - Purple
  - 💻 **Code** - Green
  - 🔗 **URL** - Gray
- Clickable to open in workspace

### ✅ 5. Metadata Display
- **Suggestions** - Follow-up question buttons
- **Actions** - Inline action buttons
- **Custom metadata** - Flexible rendering

### ✅ 6. Enhanced UX
- Typing indicator with animated dots
- Auto-scroll to latest message
- Quick action buttons on welcome screen
- Clear conversation button
- Error states and retry options

## API Service (`chatApi.ts`)

### Send Message

```typescript
import { sendMessage } from '../services/chatApi';

const response = await sendMessage({
  message: 'Show me critical missions',
  attachments: [file1, file2],
  context: {
    currentWorkspace: 'dashboard',
    currentMission: 'mission_123'
  }
});

// Response structure:
{
  response: string;
  citations?: Citation[];
  metadata?: {
    missions?: string[];
    kpis?: string[];
    suggestions?: string[];
    actions?: Action[];
  };
  message_id?: string;
}
```

### Upload Attachment

```typescript
import { uploadAttachment } from '../services/chatApi';

const result = await uploadAttachment(file);
// Returns: { reference, filename, artifact_id, url }
```

### Types

```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    citations?: Citation[];
    missions?: string[];
    kpis?: string[];
    suggestions?: string[];
    actions?: Action[];
  };
  attachments?: Attachment[];
}

interface Citation {
  type: 'mission' | 'kpi' | 'document' | 'code' | 'url';
  id: string;
  title: string;
  url?: string;
  excerpt?: string;
}

interface Action {
  type: 'open_workspace' | 'execute_mission' | 'view_logs' | 'custom';
  label: string;
  payload: any;
}
```

## React Hook (`useChat.ts`)

### Basic Usage

```typescript
import { useChat } from '../hooks/useChat';

function ChatComponent() {
  const {
    messages,
    loading,
    error,
    isEmpty,
    sendMessage,
    clearMessages,
  } = useChat({
    persistMessages: true,  // Save to localStorage
    loadHistory: false,     // Load from backend
    onError: (error) => {
      toast.error(error.message);
    }
  });

  return (
    <div>
      {messages.map(msg => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <input onSubmit={(text) => sendMessage(text)} />
    </div>
  );
}
```

### Advanced Features

```typescript
const {
  messages,
  sendMessage,
  regenerateLastMessage,  // Resend last user message
  getCitationsByType,     // Get all citations of a type
  getLastMessage,         // Get most recent message
} = useChat();

// Get all mission citations
const missions = getCitationsByType('mission');

// Regenerate last response
await regenerateLastMessage();

// Get last message
const last = getLastMessage();
```

### Attachments Hook

```typescript
import { useChatAttachments } from '../hooks/useChat';

const {
  attachments,
  uploading,
  uploadError,
  addAttachment,
  removeAttachment,
  clearAttachments,
} = useChatAttachments();

// Add file
addAttachment(file);

// Remove by index
removeAttachment(0);

// Clear all
clearAttachments();
```

## Component (`ChatPane.tsx`)

### Props

```typescript
interface ChatPaneProps {
  onOpenWorkspace?: (type: string, data: any) => void;
}
```

### Workspace Integration

When a citation is clicked:

```typescript
<ChatPane
  onOpenWorkspace={(type, data) => {
    // type: 'mission', 'kpi', 'document', etc.
    // data: Citation object with id, title, etc.
    
    if (type === 'mission') {
      // Open mission detail workspace
      workspaceManager.createWorkspace('mission', data.title, {
        missionId: data.id
      });
    } else if (type === 'kpi') {
      // Open KPI dashboard
      workspaceManager.createWorkspace('dashboard', 'KPI Dashboard', {
        kpiId: data.id
      });
    }
  }}
/>
```

### Message Flow

```
User types message + attaches files
       ↓
Click Send
       ↓
1. Clear input immediately (optimistic UI)
2. Add user message to messages array
3. Upload attachments to /api/ingest/upload
4. Send message + attachment refs to /api/chat
5. Parse response (text + citations + metadata)
6. Add assistant message to messages array
7. Auto-scroll to bottom
```

## Citation Extraction

The service automatically extracts citations from:

### 1. Explicit `citations` field
```json
{
  "response": "...",
  "citations": [
    { "type": "mission", "id": "mission_123", "title": "..." }
  ]
}
```

### 2. Metadata fields
```json
{
  "response": "...",
  "metadata": {
    "missions": ["mission_123", "mission_456"],
    "kpis": ["kpi_revenue", "kpi_conversion"]
  }
}
```

### 3. Text parsing
Grace can include citations in text:
```
"See [mission:mission_123] and [kpi:revenue_growth]"
```

All are automatically extracted and rendered as pills.

## Styling

### Citation Pills

Each type has unique styling:

```css
.citation-mission {
  background: rgba(255, 170, 0, 0.1);
  color: #ffaa00;
  border-color: rgba(255, 170, 0, 0.3);
}

.citation-kpi {
  background: rgba(0, 204, 255, 0.1);
  color: #00ccff;
  border-color: rgba(0, 204, 255, 0.3);
}
```

Hover effects:
- Background darkens
- Border brightens
- Slight lift (`translateY(-1px)`)

### Message Bubbles

- **User messages:** Right-aligned, blue background
- **Assistant messages:** Left-aligned, dark gray background
- **Error messages:** Red border, light red background

### Typing Indicator

Animated dots while Grace is thinking:

```css
@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  30% {
    opacity: 1;
    transform: scale(1);
  }
}
```

## Integration with GraceConsole

Update `GraceConsole.tsx` to pass workspace handler:

```typescript
import ChatPane from './panels/ChatPane';
import WorkspaceManager from './panels/WorkspaceManager';

function GraceConsole() {
  const [workspace, setWorkspace] = useState(null);

  const handleOpenWorkspace = (type, data) => {
    // Create new workspace tab
    setWorkspace({ type, data });
  };

  return (
    <div className="console">
      <ChatPane onOpenWorkspace={handleOpenWorkspace} />
      <WorkspaceManager workspace={workspace} />
    </div>
  );
}
```

## Backend Requirements

The chat endpoint should return:

```json
{
  "response": "Here are the critical missions...",
  "citations": [
    {
      "type": "mission",
      "id": "mission_123",
      "title": "Fix CRM data sync",
      "excerpt": "Detected anomaly in..."
    }
  ],
  "metadata": {
    "suggestions": [
      "Show me mission details",
      "Execute the mission"
    ],
    "actions": [
      {
        "type": "execute_mission",
        "label": "Execute Mission",
        "payload": { "mission_id": "mission_123" }
      }
    ]
  }
}
```

## Message Persistence

Messages are saved to `localStorage` under key `grace_chat_messages`:

```typescript
// Save
localStorage.setItem('grace_chat_messages', JSON.stringify(messages));

// Load
const stored = localStorage.getItem('grace_chat_messages');
const messages = JSON.parse(stored);
```

Clear on logout:
```typescript
localStorage.removeItem('grace_chat_messages');
```

## Error Handling

### Network Errors
```typescript
try {
  await sendMessage(text);
} catch (error) {
  // Error message automatically added to conversation
  // onError callback triggered
}
```

### Display
- Error banner if messages exist
- Full error screen if no messages
- Retry button in both cases

## Accessibility

- Keyboard navigation (`Enter` to send, `Shift+Enter` for new line)
- Focus management
- ARIA labels on buttons
- Screen reader friendly

## Performance

- LocalStorage persistence (instant load)
- Lazy message rendering (virtual scrolling ready)
- Optimistic UI updates (immediate feedback)
- Debounced auto-save

## Testing

### Unit Tests
```typescript
// Test hook
import { renderHook, act } from '@testing-library/react-hooks';
import { useChat } from './useChat';

test('sends message', async () => {
  const { result } = renderHook(() => useChat());
  
  await act(async () => {
    await result.current.sendMessage('Hello');
  });
  
  expect(result.current.messages).toHaveLength(2); // User + Assistant
});
```

### Integration Tests
```typescript
// Test component
import { render, fireEvent, waitFor } from '@testing-library/react';
import ChatPane from './ChatPane';

test('displays message', async () => {
  const { getByPlaceholderText, getByText } = render(<ChatPane />);
  
  const input = getByPlaceholderText('Ask Grace anything...');
  fireEvent.change(input, { target: { value: 'Hello' } });
  fireEvent.submit(input.closest('form'));
  
  await waitFor(() => {
    expect(getByText('Hello')).toBeInTheDocument();
  });
});
```

## Future Enhancements

1. **Voice Input** - Use Web Speech API
2. **Message Editing** - Edit and resend messages
3. **Message Reactions** - Thumbs up/down feedback
4. **Rich Content** - Render markdown, code blocks
5. **Search** - Search conversation history
6. **Export** - Export conversation as PDF/text
7. **Streaming** - Stream responses word-by-word
8. **WebSocket** - Real-time bidirectional communication

## Summary

✅ **Full conversation state** - Persistent across sessions  
✅ **Attachment support** - Upload files, include in messages  
✅ **Citation rendering** - Color-coded, clickable pills  
✅ **Metadata display** - Suggestions, actions, custom data  
✅ **Workspace integration** - Click citations to open workspaces  
✅ **Error handling** - Graceful degradation, retry options  
✅ **Loading states** - Typing indicator, disabled inputs  
✅ **Type-safe** - Full TypeScript support  

The chat is now production-ready with all the features of a modern conversational interface!
