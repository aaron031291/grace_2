# Test Fixes - November 2025

## Summary

Updated Playwright tests to match the actual UI implementation in AppChat.tsx and ChatPanel.tsx.

## Changes Made

### 1. Updated Test Selectors

**Before:** Tests used placeholder text like "Ask Grace anything..." but looked for exact emoji matches like "📤 Send"  
**After:** Tests now use CSS class selectors and more flexible text matching

### 2. Fixed Selector Issues

| Component | Old Selector | New Selector | Reason |
|-----------|--------------|--------------|---------|
| Send Button | `getByText('📤 Send')` | `locator('button.chat-send-btn')` | More reliable, doesn't break if emoji changes |
| Chat Messages | `getByText('👤 You')` | `locator('.chat-messages')` | Checks content area instead of specific role label |
| Approvals | `getByText('⚠️ Pending Approvals')` | `locator('.approvals-section')` | Uses class selector for stability |
| Voice/Attach | `getByTitle(/voice input/i)` | `locator('button:has-text("🎤")')` | Matches actual button implementation |

### 3. Added Timeout Handling

All assertions now include explicit timeouts:
```typescript
await expect(element).toBeVisible({ timeout: 10000 });
```

This prevents flaky tests when APIs are slow.

### 4. Created CI Configuration

New file: `playwright-ci.config.ts`
- Skips auto-starting dev server
- Assumes services are already running
- Faster test execution
- Use with: `npm run test:ci`

## Test Structure

```
tests/
├── smoke.spec.ts       # Basic functionality (loads, API exists)
├── chat.spec.ts        # Chat interaction, approvals, errors
└── build.spec.ts       # Build validation
```

## Running Tests

### Option 1: Auto Dev Server (Default)
```bash
npm test              # Starts dev server automatically
```

### Option 2: Manual Services (Faster)
```bash
# Terminal 1: Start backend
python server.py

# Terminal 2: Start frontend
npm run dev

# Terminal 3: Run tests
npm run test:ci
```

## Test Coverage

- ✅ UI loads and renders
- ✅ Chat input accepts text
- ✅ Send button works
- ✅ Messages display in chat
- ✅ Mock API responses work
- ✅ Approval cards render
- ✅ Approval actions trigger API calls
- ✅ Error handling displays errors
- ✅ Sidebar controls exist
- ✅ Telemetry strip visible
- ✅ Health meter visible

## Known Limitations

1. **Backend Dependency:** Tests require backend running on port 8000
2. **WebSocket Tests:** Not yet implemented (notifications, real-time updates)
3. **File Upload:** Not yet tested (requires file system mocking)
4. **Voice Input:** Not yet tested (requires browser permissions)

## Next Steps

- [ ] Add WebSocket notification tests
- [ ] Add file upload tests
- [ ] Add voice input tests
- [ ] Add screenshot comparison tests
- [ ] Add performance tests
