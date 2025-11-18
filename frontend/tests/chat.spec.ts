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
    
    // Check for main elements
    await expect(page.getByText('GRACE')).toBeVisible();
    await expect(page.getByPlaceholder('Ask Grace anything...')).toBeVisible();
    await expect(page.getByText('📤 Send')).toBeVisible();
  });

  test('should display telemetry strip', async ({ page }) => {
    await page.goto('/');
    
    // Check telemetry strip is present
    await expect(page.locator('.telemetry-strip')).toBeVisible();
    
    // Should show at least some metrics
    await expect(page.getByText('Guardian')).toBeVisible();
    await expect(page.getByText('Trust')).toBeVisible();
  });

  test('should have voice and attachment controls', async ({ page }) => {
    await page.goto('/');
    
    // Voice toggle button
    await expect(page.getByTitle(/voice input/i)).toBeVisible();
    
    // Attachment button
    await expect(page.getByTitle(/attach files/i)).toBeVisible();
  });

  test('should have sidebar controls', async ({ page }) => {
    await page.goto('/');
    
    // Check sidebar buttons exist
    await expect(page.getByText('Remote Access')).toBeVisible();
    await expect(page.getByText('Screen Share')).toBeVisible();
    await expect(page.getByText('Upload Docs')).toBeVisible();
    await expect(page.getByText('Tasks')).toBeVisible();
  });
});

test.describe('Chat Interaction', () => {
  test('should send a message and display it', async ({ page }) => {
    await page.goto('/');
    
    const input = page.getByPlaceholder('Ask Grace anything...');
    const sendBtn = page.getByText('📤 Send');
    
    // Type a test message
    await input.fill('ping');
    
    // Send should be enabled
    await expect(sendBtn).toBeEnabled();
    
    // Click send
    await sendBtn.click();
    
    // Message should appear in chat
    await expect(page.getByText('👤 You')).toBeVisible();
    await expect(page.getByText('ping')).toBeVisible();
    
    // Send button should show loading state
    await expect(page.getByText('⏳ Sending...')).toBeVisible({ timeout: 1000 });
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
    await page.getByText('📤 Send').click();
    
    // Wait for Grace's response
    await expect(page.getByText('🤖 Grace')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('pong')).toBeVisible();
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
    await page.getByText('📤 Send').click();
    
    // Wait for approval card to appear
    await expect(page.getByText('⚠️ Pending Approvals')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('execute_command')).toBeVisible();
    await expect(page.getByText('APPROVAL REQUIRED')).toBeVisible();
    
    // Check approval buttons exist
    await expect(page.getByText('✅ Approve')).toBeVisible();
    await expect(page.getByText('❌ Reject')).toBeVisible();
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
    await page.getByText('📤 Send').click();
    
    // Click approve button
    await page.getByText('✅ Approve').click();
    
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
    await page.getByText('📤 Send').click();
    
    // Should show error message
    await expect(page.getByText(/Error:/)).toBeVisible({ timeout: 5000 });
  });
});
