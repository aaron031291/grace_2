"""
Smoke test for chat UI
Ensures chat loads, accepts input, and responds
"""

import pytest
from playwright.async_api import async_playwright, Page
import asyncio


@pytest.mark.asyncio
async def test_chat_page_loads():
    """Test that chat page loads and renders input"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to frontend
            await page.goto("http://localhost:5173", timeout=10000)
            
            # Wait for chat input to be visible
            await page.wait_for_selector("textarea.chat-input", timeout=5000)
            
            # Verify chat panel exists
            chat_panel = await page.query_selector(".chat-panel")
            assert chat_panel is not None, "Chat panel not found"
            
            # Verify send button exists
            send_btn = await page.query_selector(".chat-send-btn")
            assert send_btn is not None, "Send button not found"
            
            print("✅ Chat UI loaded successfully")
        
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_chat_send_message():
    """Test sending a message to Grace"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to frontend
            await page.goto("http://localhost:5173", timeout=10000)
            
            # Wait for chat input
            await page.wait_for_selector("textarea.chat-input", timeout=5000)
            
            # Type a message
            await page.fill("textarea.chat-input", "Hello Grace!")
            
            # Click send button
            await page.click(".chat-send-btn")
            
            # Wait for response message to appear
            await page.wait_for_selector(".message-assistant", timeout=10000)
            
            # Verify message was sent (user message should appear)
            user_messages = await page.query_selector_all(".message-user")
            assert len(user_messages) > 0, "User message not displayed"
            
            # Verify Grace responded
            assistant_messages = await page.query_selector_all(".message-assistant")
            assert len(assistant_messages) > 0, "Grace did not respond"
            
            print("✅ Chat message sent and response received")
        
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_health_meter_loads():
    """Test that health meter displays metrics"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to frontend
            await page.goto("http://localhost:5173", timeout=10000)
            
            # Wait for health meter
            await page.wait_for_selector(".health-meter", timeout=5000)
            
            # Verify metric cards exist
            metric_cards = await page.query_selector_all(".metric-card")
            assert len(metric_cards) >= 2, "Health metrics not displayed"
            
            print("✅ Health meter loaded successfully")
        
        finally:
            await browser.close()


if __name__ == "__main__":
    # Run tests directly
    asyncio.run(test_chat_page_loads())
    asyncio.run(test_chat_send_message())
    asyncio.run(test_health_meter_loads())
    print("\n🎉 All smoke tests passed!")
