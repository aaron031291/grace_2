/**
 * Grace Chat Smoke Tests
 * 
 * Prevents regressions by testing core chat functionality:
 * - Page loads
 * - Can send messages
 * - Receives responses
 * - Approvals render
 * - Notifications work
 */

import { test, expect } from '@playwright/test';

test.describe('Grace Chat UI', () => {
  test('should load the chat interface', async ({ page }) => {
    await page.goto('/');
    
    // Check for main elements - GRACE header exists in sidebar
    await expect(page.locator('h1')).toContainText('GRACE');
    await expect(page.getByPlaceholder('Ask Grace anything...')).toBeVisible({ timeout: 10000 });
    
    // Send button appears when there's text or initially
    const sendButton = page.locator('button.chat-send-btn');
    await expect(sendButton).toBeVisible({ timeout: 10000 });
  });

  test('should display telemetry strip', async ({ page }) => {
    await page.goto('/');
    
    // Check telemetry strip is present (in ChatPanel)
    const telemetryStrip = page.locator('.telemetry-strip');
    await expect(telemetryStrip).toBeVisible({ timeout: 10000 });
    
    // HealthMeter shows Trust Score instead of just "Trust" or "Guardian"
    const healthMeter = page.locator('.health-meter');
    await expect(healthMeter).toBeVisible({ timeout: 10000 });
  });

  test('should have voice and attachment controls', async ({ page }) => {
    await page.goto('/');
    
    // Voice toggle button in ChatPanel
    const voiceButton = page.locator('button[title*="voice" i], button:has-text("🎤")');
    await expect(voiceButton.first()).toBeVisible({ timeout: 10000 });
    
    // Attachment button in ChatPanel
    const attachButton = page.locator('button[title*="attach" i], button:has-text("📎")');
    await expect(attachButton.first()).toBeVisible({ timeout: 10000 });
  });

  test('should have sidebar controls', async ({ page }) => {
    await page.goto('/');
    
    // Check sidebar buttons exist - using actual text from AppChat.tsx
    await expect(page.getByText('Remote Access', { exact: false })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Screen Share', { exact: false })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Upload Docs')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Tasks')).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Chat Interaction', () => {
  test('should send a message and display it', async ({ page }) => {
    await page.goto('/');
    
    const input = page.getByPlaceholder('Ask Grace anything...');
    await expect(input).toBeVisible({ timeout: 10000 });
    
    // Type a test message
    await input.fill('ping');
    
    // Find send button using class selector
    const sendBtn = page.locator('button.chat-send-btn');
    await expect(sendBtn).toBeVisible();
    await expect(sendBtn).toBeEnabled();
    
    // Click send
    await sendBtn.click();
    
    // Message should appear in chat history
    await expect(page.locator('.chat-messages')).toContainText('ping', { timeout: 5000 });
  });

  test('should receive a response from Grace', async ({ page }) => {
    // Mock the API response
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: 'pong',
          trace_id: 'test-trace-123',
          session_id: 'test-session-456',
          actions: [],
          citations: [],
          confidence: 0.95,
          requires_approval: false,
          pending_approvals: [],
          timestamp: new Date().toISOString(),
        }),
      });
    });

    await page.goto('/');
    
    const input = page.getByPlaceholder('Ask Grace anything...');
    await input.fill('ping');
    
    const sendBtn = page.locator('button.chat-send-btn');
    await sendBtn.click();
    
    // Wait for Grace's response in chat messages
    await expect(page.locator('.chat-messages')).toContainText('pong', { timeout: 5000 });
  });
});

test.describe('Approvals', () => {
  test('should render pending approval cards', async ({ page }) => {
    // Mock chat response with pending approvals
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: 'I need approval to proceed',
          trace_id: 'approval-trace-789',
          session_id: 'test-session',
          actions: [],
          citations: [],
          confidence: 0.9,
          requires_approval: true,
          pending_approvals: [
            {
              trace_id: 'approval-trace-789',
              action_type: 'execute_command',
              agent: 'shell_agent',
              governance_tier: 'approval_required',
              params: { command: 'ls -la' },
              reason: 'Shell command requires user approval',
              timestamp: new Date().toISOString(),
            },
          ],
          timestamp: new Date().toISOString(),
        }),
      });
    });

    await page.goto('/');
    
    const input = page.getByPlaceholder('Ask Grace anything...');
    await input.fill('run command');
    
    const sendBtn = page.locator('button.chat-send-btn');
    await sendBtn.click();
    
    // Wait for approval section to appear
    await expect(page.locator('.approvals-section')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Pending Approvals')).toBeVisible();
    await expect(page.getByText('execute_command')).toBeVisible();
    
    // Check approval buttons exist
    await expect(page.locator('button').filter({ hasText: 'Approve' })).toBeVisible();
    await expect(page.locator('button').filter({ hasText: 'Reject' })).toBeVisible();
  });

  test('should handle approval action', async ({ page }) => {
    // Mock the approval response
    let approvalCalled = false;
    
    await page.route('**/api/governance/approve', async (route) => {
      approvalCalled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          action: 'approved',
          trace_id: 'approval-trace-789',
          approved_by: 'user',
          timestamp: new Date().toISOString(),
          details: { action_type: 'execute_command' },
        }),
      });
    });

    // Mock chat with approval
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          reply: 'Needs approval',
          trace_id: 'test',
          session_id: 'test',
          actions: [],
          citations: [],
          confidence: 0.9,
          requires_approval: true,
          pending_approvals: [
            {
              trace_id: 'approval-trace-789',
              action_type: 'execute_command',
              agent: 'shell_agent',
              governance_tier: 'approval_required',
              params: {},
              reason: 'Test approval',
              timestamp: new Date().toISOString(),
            },
          ],
          timestamp: new Date().toISOString(),
        }),
      });
    });

    await page.goto('/');
    
    const input = page.getByPlaceholder('Ask Grace anything...');
    await input.fill('test');
    
    const sendBtn = page.locator('button.chat-send-btn');
    await sendBtn.click();
    
    // Wait for approval section
    await page.locator('.approvals-section').waitFor({ timeout: 10000 });
    
    // Click approve button
    const approveBtn = page.locator('button').filter({ hasText: 'Approve' });
    await approveBtn.click();
    
    // Wait a bit for the API call
    await page.waitForTimeout(500);
    
    // Verify the approval API was called
    expect(approvalCalled).toBe(true);
  });
});

test.describe('Background Tasks Drawer', () => {
  test('should open tasks drawer', async ({ page }) => {
    await page.goto('/');
    
    // Click tasks button
    await page.getByText('📋 Tasks').click();
    
    // Drawer should open
    await expect(page.getByText('📋 Background Tasks')).toBeVisible();
    
    // Should have close button
    await expect(page.locator('.drawer-close')).toBeVisible();
  });

  test('should close tasks drawer', async ({ page }) => {
    await page.goto('/');
    
    await page.getByText('📋 Tasks').click();
    await expect(page.getByText('📋 Background Tasks')).toBeVisible();
    
    // Click close button
    await page.locator('.drawer-close').click();
    
    // Drawer should disappear
    await expect(page.getByText('📋 Background Tasks')).not.toBeVisible();
  });
});

test.describe('Error Handling', () => {
  test('should display error messages', async ({ page }) => {
    // Mock API error
    await page.route('**/api/chat', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Internal server error',
        }),
      });
    });

    await page.goto('/');
    
    const input = page.getByPlaceholder('Ask Grace anything...');
    await input.fill('test error');
    
    const sendBtn = page.locator('button.chat-send-btn');
    await sendBtn.click();
    
    // Should show error message in chat
    await expect(page.locator('.chat-messages')).toContainText('Error', { timeout: 10000 });
  });
});
