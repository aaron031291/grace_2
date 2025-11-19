# Grace Frontend Tests

Smoke tests to prevent regressions in the chat UI.

## Setup

```bash
# Install Playwright
npm install

# Install browsers
npx playwright install chromium
```

## Running Tests

```bash
# Run all tests (headless)
npm test

# Run with UI for debugging
npm run test:ui

# Run smoke tests only
npm run test:smoke

# Run in debug mode
npx playwright test --debug

# Run specific test
npx playwright test tests/chat.spec.ts
```

## Test Coverage

### ✅ UI Rendering
- Chat interface loads
- Telemetry strip displays
- Sidebar controls present
- Voice/attachment buttons visible

### ✅ Chat Interaction
- Can send messages
- Messages display in chat
- Receives responses from Grace
- Loading states work

### ✅ Approvals
- Approval cards render with correct data
- Shows tier badges (SUPERVISED, APPROVAL REQUIRED)
- Approve/Reject buttons work
- Calls governance API endpoints

### ✅ Background Tasks
- Tasks drawer opens/closes
- Displays task list
- Shows task status

### ✅ Error Handling
- Displays error messages
- Auto-attaches log excerpts

## Writing New Tests

```typescript
import { test, expect } from '@playwright/test';

test('my new feature', async ({ page }) => {
  await page.goto('/');
  
  // Your test logic
  await expect(page.getByText('Expected Text')).toBeVisible();
});
```

## Mocking APIs

```typescript
test('with mocked API', async ({ page }) => {
  await page.route('**/api/chat', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        reply: 'Mocked response',
        // ... rest of response
      })
    });
  });
  
  await page.goto('/');
  // ... test interaction
});
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npm test
```

## Debugging

### Visual Debug Mode

```bash
npm run test:ui
```

This opens Playwright's UI where you can:
- See each test step
- Inspect the DOM
- View network calls
- Time travel through the test

### Screenshots on Failure

Screenshots are automatically captured on test failure and saved to `test-results/`.

### Trace Viewer

```bash
npx playwright show-trace trace.zip
```

## Best Practices

1. **Keep tests fast** - Mock API calls when possible
2. **Test user flows** - Not implementation details
3. **Use accessible selectors** - Text, roles, labels
4. **Clean up** - Tests should be independent
5. **Add new tests** - When fixing bugs or adding features

## Common Patterns

### Wait for Element

```typescript
await expect(page.getByText('Grace')).toBeVisible({ timeout: 5000 });
```

### Fill Form

```typescript
await page.getByPlaceholder('Ask Grace...').fill('test message');
await page.getByText('Send').click();
```

### Check API Call

```typescript
let apiCalled = false;

await page.route('**/api/chat', async (route) => {
  apiCalled = true;
  await route.fulfill({ ... });
});

// ... trigger action

expect(apiCalled).toBe(true);
```

## Troubleshooting

### Tests Won't Start

```bash
# Reinstall browsers
npx playwright install chromium --force
```

### Port Already in Use

Kill existing dev server:
```bash
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5173 | xargs kill
```

### Timeout Errors

Increase timeout in test:
```typescript
test('slow test', async ({ page }) => {
  test.setTimeout(60000); // 60 seconds
  // ...
});
```

---

**Need help?** Check [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)
