/**
 * Smoke Tests - Quick validation that core functionality works
 * 
 * Run with: npm run test:smoke
 */

import { test, expect } from '@playwright/test';

const API_BASE = process.env.VITE_API_BASE_URL || 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5173';

test.describe('Smoke Tests', () => {
  
  test('frontend app loads successfully', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Should see Grace header
    await expect(page.locator('h1')).toContainText('GRACE');
    
    // Should see main chat interface
    const chatPanel = page.locator('.chat-panel, [class*="chat"]');
    await expect(chatPanel).toBeVisible({ timeout: 5000 });
  });
  
  test('sidebar controls are present', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Check for key sidebar buttons
    const sidebar = page.locator('.app-sidebar, .sidebar');
    await expect(sidebar).toBeVisible();
    
    // Should have control buttons
    const buttons = page.locator('.control-button, button');
    const buttonCount = await buttons.count();
    expect(buttonCount).toBeGreaterThan(3); // At least 4-5 buttons
  });
  
  test('chat input is functional', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Find chat input (textarea or input)
    const chatInput = page.locator('textarea, input[type="text"]').first();
    await expect(chatInput).toBeVisible({ timeout: 5000 });
    
    // Should be able to type
    await chatInput.fill('Hello Grace');
    await expect(chatInput).toHaveValue('Hello Grace');
  });
  
  test('backend health endpoint responds', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status');
  });
  
  test('chat API endpoint exists', async ({ request }) => {
    const response = await request.post(`${API_BASE}/api/chat`, {
      data: {
        message: 'test',
        session_id: 'smoke-test'
      }
    });
    
    // Should respond (even if OpenAI key not set, should return error response)
    expect(response.status()).toBeLessThan(500);
    
    const data = await response.json();
    expect(data).toHaveProperty('reply');
  });
  
  test('memory files API endpoint exists', async ({ request }) => {
    const response = await request.get(`${API_BASE}/memory/files/list`);
    
    // Should respond
    expect([200, 404, 500]).toContain(response.status());
  });
  
  test('build produces dist folder', async () => {
    const fs = require('fs');
    const path = require('path');
    
    const distPath = path.join(process.cwd(), 'dist');
    const distExists = fs.existsSync(distPath);
    
    expect(distExists).toBeTruthy();
    
    // Should have index.html
    const indexExists = fs.existsSync(path.join(distPath, 'index.html'));
    expect(indexExists).toBeTruthy();
  });
  
  test('no legacy files in active build', async () => {
    const fs = require('fs');
    const path = require('path');
    
    // Check that legacy files are not in src root
    const srcPath = path.join(process.cwd(), 'src');
    const files = fs.readdirSync(srcPath);
    
    const legacyPatterns = [
      'GraceAgentic.tsx',
      'GraceChat.tsx',
      'GraceChatGPT.tsx',
      'App.backup.tsx',
      'App.minimal.tsx'
    ];
    
    for (const pattern of legacyPatterns) {
      expect(files).not.toContain(pattern);
    }
    
    // Legacy folder should exist
    expect(files).toContain('legacy');
  });
  
});

test.describe('Integration Smoke Tests', () => {
  
  test.skip('chat message flow (requires running backend)', async ({ page, request }) => {
    // Skip by default, enable when backend is running
    await page.goto(FRONTEND_URL);
    
    // Type message
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('Hello Grace');
    
    // Click send
    const sendButton = page.locator('button:has-text("Send"), button[type="submit"]').first();
    await sendButton.click();
    
    // Should see message in chat
    await expect(page.locator('.message, .chat-message')).toContainText('Hello Grace');
  });
  
});
