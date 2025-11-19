# Grace Frontend Developer Guide

Quick reference for developers working on or extending Grace's frontend.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Install Playwright browsers (for testing)
npx playwright install

# Start development server
npm run dev

# Build for production
npm run build

# Run smoke tests
npm run test:smoke
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/              # API clients
│   │   ├── chat.ts       # Chat API
│   │   ├── voice.ts      # Voice API
│   │   ├── remote.ts     # Remote access API
│   │   ├── tasks.ts      # Background tasks API
│   │   └── config.ts     # API configuration
│   ├── components/       # React components
│   │   ├── ChatPanel.tsx              # Main chat interface
│   │   ├── TelemetryStrip.tsx         # System metrics bar
│   │   ├── BackgroundTasksDrawer.tsx  # Tasks sidebar
│   │   ├── HealthMeter.tsx            # Health visualization
│   │   └── RemoteCockpit.tsx          # Remote controls
│   ├── hooks/            # React hooks
│   │   └── useNotifications.ts        # WebSocket notifications
│   ├── AppChat.tsx       # Main app component
│   ├── config.ts         # Frontend configuration
│   └── main.tsx          # Entry point
├── tests/                # Playwright tests
│   └── chat.spec.ts      # Smoke tests
├── playwright.config.ts  # Test configuration
└── API_CONTRACT.md       # API documentation
```

## 🔌 Key Components

### ChatPanel

The main chat interface. Handles:
- Message input/output
- Voice toggle (browser + backend API)
- File attachments
- Inline approval cards
- Auto log attachments on errors

**Usage:**
```tsx
import { ChatPanel } from './components/ChatPanel';

<ChatPanel />
```

### TelemetryStrip

Compact status bar showing system health.

**Features:**
- Guardian health status
- Trust score
- Learning jobs count
- Active missions
- Remote heartbeat
- Pending approvals
- WebSocket status

**Usage:**
```tsx
import { TelemetryStrip } from './components/TelemetryStrip';

<TelemetryStrip />
```

### BackgroundTasksDrawer

Sliding drawer for background task management.

**Props:**
```tsx
interface BackgroundTasksDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}
```

## 🔧 API Integration

All API calls use the centralized `API_BASE_URL` from `config.ts`:

```typescript
import { API_BASE_URL } from './config';

// API calls use proxy in dev, direct URL in production
const response = await fetch(`${API_BASE_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello' })
});
```

### API Clients

Use the provided API client classes:

```typescript
import { ChatAPI } from './api/chat';
import { VoiceAPI } from './api/voice';
import { RemoteAPI } from './api/remote';
import { TasksAPI } from './api/tasks';

// Send chat message
const response = await ChatAPI.sendMessage({
  message: 'What is my trust score?',
  session_id: sessionId,
  user_id: 'user'
});

// Start voice session
const voiceSession = await VoiceAPI.startVoice({
  user_id: 'user',
  language: 'en-US'
});

// Get background tasks
const tasks = await TasksAPI.getTasks();
```

## 📡 Notifications

Subscribe to real-time notifications via WebSocket:

```typescript
import { useNotifications } from './hooks/useNotifications';

function MyComponent() {
  const { notifications, connected } = useNotifications('user');
  
  useEffect(() => {
    notifications.forEach(notif => {
      console.log(`[${notif.badge}] ${notif.message}`);
    });
  }, [notifications]);
  
  return <div>Connected: {connected ? '✅' : '❌'}</div>;
}
```

## 🎭 Voice Integration

Voice has two layers:
1. **Browser Speech Recognition** - Captures audio locally
2. **Backend Session** - Maintains persistent "always listening" mode

```typescript
// Start backend voice session
const response = await VoiceAPI.startVoice();
const sessionId = response.session.session_id;

// Start browser recognition
const recognition = new webkitSpeechRecognition();
recognition.continuous = true;
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  // Send to chat...
};
recognition.start();

// Stop when done
await VoiceAPI.stopVoice(sessionId);
recognition.stop();
```

## ⚖️ Governance & Approvals

Approvals appear inline in chat when Grace needs permission:

```typescript
// Handle approval from UI
const handleApproval = async (traceId: string, approved: boolean) => {
  const endpoint = approved 
    ? '/api/governance/approve' 
    : '/api/governance/reject';
    
  await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      trace_id: traceId,
      approved,
      user_id: 'user'
    })
  });
};
```

**Governance Tiers:**
- `supervised` - Tier 2, moderate oversight
- `approval_required` - Tier 3, requires explicit approval

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run specific test
npm run test:smoke

# Debug mode
npx playwright test --debug
```

### Writing Tests

```typescript
import { test, expect } from '@playwright/test';

test('should send message', async ({ page }) => {
  await page.goto('/');
  
  await page.getByPlaceholder('Ask Grace anything...').fill('test');
  await page.getByText('📤 Send').click();
  
  await expect(page.getByText('👤 You')).toBeVisible();
});
```

### Mocking API Responses

```typescript
test('should handle response', async ({ page }) => {
  await page.route('**/api/chat', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        reply: 'Test response',
        trace_id: 'test-123',
        session_id: 'sess-456',
        // ... rest of response
      })
    });
  });
  
  await page.goto('/');
  // ... test interaction
});
```

## 🎨 Styling

CSS modules are used for component-specific styles:

```tsx
// Component
import './MyComponent.css';

// CSS
.my-component {
  background: #1a1a1a;
  color: #fff;
}
```

**Design System:**
- Background: `#0a0a0a`, `#1a1a1a`, `#2a2a2a`
- Text: `#fff`, `#ccc`, `#888`
- Primary: `#0066cc`
- Success: `#4caf50`
- Warning: `#ff9800`
- Error: `#f44336`

## 🔍 Debugging

### Enable Verbose Logging

```typescript
// config.ts
if (import.meta.env.DEV) {
  console.log('[CONFIG]', config);
}
```

### Check WebSocket Connection

```typescript
const { notifications, connected } = useNotifications('user');
console.log('WS Connected:', connected);
console.log('Notifications:', notifications);
```

### Inspect API Calls

Open DevTools → Network tab to see all API requests/responses.

## 🚢 Deployment

### Environment Variables

Create `.env.local`:

```bash
# API URL (leave empty for dev proxy)
VITE_API_BASE_URL=

# Or set for production
VITE_API_BASE_URL=https://api.yourdomain.com
```

### Build

```bash
npm run build
```

Output in `dist/` directory.

### Production Checklist

- [ ] `npm run build` passes
- [ ] `npm run test` passes
- [ ] API endpoints configured
- [ ] WebSocket URL set
- [ ] Error boundaries in place

## 📚 Additional Resources

- [API Contract](./API_CONTRACT.md) - Complete API reference
- [Smoke Tests](./tests/chat.spec.ts) - Test examples
- [Vite Docs](https://vitejs.dev/) - Build tool
- [Playwright Docs](https://playwright.dev/) - Testing framework

## 🤝 Contributing

When adding new features:

1. **Add API client** in `src/api/`
2. **Create component** in `src/components/`
3. **Write tests** in `tests/`
4. **Document API** in `API_CONTRACT.md`
5. **Update this guide** if needed

### Code Style

- Use TypeScript
- Functional components + hooks
- Type all props and state
- Handle errors gracefully
- Add comments for complex logic

### Commit Messages

```
feat: add voice session management
fix: resolve approval card rendering
docs: update API contract
test: add smoke tests for chat
```

## 🐛 Common Issues

### CORS Errors

**Solution:** Use Vite's dev proxy (already configured):

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

### WebSocket Won't Connect

**Check:**
1. Backend is running on port 8000
2. WebSocket endpoint: `ws://localhost:8000/api/notifications/ws/user`
3. No firewall blocking

### Tests Failing

**Common fixes:**
```bash
# Update browsers
npx playwright install

# Clear cache
rm -rf node_modules/.vite
npm run dev
```

## 💡 Tips

- Use React DevTools for debugging components
- Use Network tab to inspect API calls
- Use Playwright UI mode for visual test debugging
- Keep API clients thin - logic in components
- Use TypeScript for better DX

---

**Questions?** Check [API_CONTRACT.md](./API_CONTRACT.md) or the smoke tests for examples.
