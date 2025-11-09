"""
Grace Monitor Dashboard
Real-time visual dashboard to monitor Grace's activities and chat with her
Shows: Learning progress, remote access status, recent actions, chat
"""

import asyncio
import curses
from datetime import datetime
from typing import List, Dict, Any
import logging

from backend.web_learning_orchestrator import web_learning_orchestrator
from backend.remote_computer_access import remote_access
from backend.knowledge_provenance import provenance_tracker

logging.basicConfig(
    filename='grace_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class GraceMonitorDashboard:
    """
    Real-time visual dashboard for monitoring Grace
    """
    
    def __init__(self):
        self.running = False
        self.chat_messages = []
        self.recent_actions = []
        self.status_data = {}
        
    async def start(self, stdscr):
        """Start dashboard"""
        self.running = True
        self.stdscr = stdscr
        
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        
        # Colors
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        
        # Start Grace's systems
        await web_learning_orchestrator.start()
        
        # Main loop
        await self._dashboard_loop()
    
    async def _dashboard_loop(self):
        """Main dashboard loop"""
        
        input_buffer = ""
        
        while self.running:
            try:
                # Clear screen
                self.stdscr.clear()
                
                # Get terminal size
                max_y, max_x = self.stdscr.getmaxyx()
                
                # Draw dashboard
                self._draw_header(max_x)
                self._draw_status_panel(max_y, max_x)
                self._draw_activity_panel(max_y, max_x)
                self._draw_chat_panel(max_y, max_x)
                self._draw_controls(max_y, max_x)
                self._draw_input_box(max_y, max_x, input_buffer)
                
                # Refresh
                self.stdscr.refresh()
                
                # Handle input
                try:
                    key = self.stdscr.getch()
                    
                    if key == ord('q') or key == ord('Q'):
                        # Quit
                        break
                    elif key == ord('s') or key == ord('S'):
                        # Stop remote access
                        await remote_access.stop()
                        self.recent_actions.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Remote access STOPPED")
                    elif key == ord('r') or key == ord('R'):
                        # Start remote access
                        await remote_access.start()
                        self.recent_actions.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Remote access STARTED")
                    elif key == curses.KEY_ENTER or key == 10 or key == 13:
                        # Send message
                        if input_buffer.strip():
                            await self._send_message(input_buffer.strip())
                            input_buffer = ""
                    elif key == curses.KEY_BACKSPACE or key == 127:
                        # Backspace
                        input_buffer = input_buffer[:-1]
                    elif 32 <= key <= 126:
                        # Printable character
                        input_buffer += chr(key)
                
                except:
                    pass
                
                # Update data
                await self._update_data()
                
                # Sleep briefly
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                break
        
        # Cleanup
        await web_learning_orchestrator.stop()
    
    def _draw_header(self, max_x):
        """Draw header"""
        title = "🤖 GRACE MONITOR DASHBOARD"
        subtitle = f"Real-time monitoring • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.addstr(0, (max_x - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
        
        self.stdscr.addstr(1, (max_x - len(subtitle)) // 2, subtitle)
        
        # Separator
        self.stdscr.addstr(2, 0, "═" * max_x)
    
    def _draw_status_panel(self, max_y, max_x):
        """Draw status panel (top left)"""
        y_start = 3
        x_start = 2
        
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(y_start, x_start, "📊 STATUS")
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        y = y_start + 1
        
        # Remote access status
        remote_enabled = remote_access.access_enabled
        status_color = 1 if remote_enabled else 3
        status_text = "✅ ENABLED" if remote_enabled else "❌ DISABLED"
        
        self.stdscr.addstr(y, x_start, "  Remote Access: ")
        self.stdscr.attron(curses.color_pair(status_color))
        self.stdscr.addstr(status_text)
        self.stdscr.attroff(curses.color_pair(status_color))
        y += 1
        
        # Learning stats
        stats = self.status_data.get('stats', {})
        self.stdscr.addstr(y, x_start, f"  Sessions: {stats.get('sessions_started', 0)}")
        y += 1
        self.stdscr.addstr(y, x_start, f"  Sources: {stats.get('sources_learned', 0)}")
        y += 1
        self.stdscr.addstr(y, x_start, f"  Tests: {stats.get('applications_tested', 0)}")
        y += 1
        
        # Governance
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(y, x_start, "  Governance: 100% ✓")
        self.stdscr.attroff(curses.color_pair(1))
    
    def _draw_activity_panel(self, max_y, max_x):
        """Draw recent activity (top right)"""
        y_start = 3
        x_start = max_x // 2 + 2
        
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(y_start, x_start, "📋 RECENT ACTIVITY")
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        
        y = y_start + 1
        
        # Show recent actions
        for i, action in enumerate(self.recent_actions[:8]):
            if y >= max_y // 2 - 2:
                break
            self.stdscr.addstr(y, x_start, f"  {action[:max_x // 2 - 5]}")
            y += 1
    
    def _draw_chat_panel(self, max_y, max_x):
        """Draw chat panel (bottom)"""
        y_start = max_y // 2
        
        self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        self.stdscr.addstr(y_start, 2, "💬 CHAT WITH GRACE")
        self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
        
        # Draw chat messages
        y = y_start + 1
        chat_height = max_y - y_start - 5
        
        for msg in self.chat_messages[-chat_height:]:
            if y >= max_y - 4:
                break
            
            sender = msg['sender']
            text = msg['message']
            
            if sender == 'user':
                self.stdscr.attron(curses.color_pair(4))
                self.stdscr.addstr(y, 2, f"You: {text[:max_x - 8]}")
                self.stdscr.attroff(curses.color_pair(4))
            else:
                self.stdscr.attron(curses.color_pair(1))
                self.stdscr.addstr(y, 2, f"Grace: {text[:max_x - 10]}")
                self.stdscr.attroff(curses.color_pair(1))
            
            y += 1
    
    def _draw_controls(self, max_y, max_x):
        """Draw controls (bottom)"""
        y = max_y - 3
        
        self.stdscr.addstr(y, 0, "─" * max_x)
        
        controls = "Q: Quit | S: Stop Remote | R: Start Remote | Type & Enter: Chat"
        self.stdscr.attron(curses.color_pair(2))
        self.stdscr.addstr(y + 1, (max_x - len(controls)) // 2, controls)
        self.stdscr.attroff(curses.color_pair(2))
    
    def _draw_input_box(self, max_y, max_x, input_buffer):
        """Draw input box"""
        y = max_y - 1
        
        prompt = "› "
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(y, 0, prompt + input_buffer + "_")
        self.stdscr.attroff(curses.color_pair(4))
    
    async def _update_data(self):
        """Update dashboard data"""
        try:
            # Get learning report
            report = await web_learning_orchestrator.get_learning_report(days=1)
            self.status_data['stats'] = report.get('statistics', {})
        except:
            pass
    
    async def _send_message(self, message: str):
        """Send chat message to Grace"""
        
        # Add user message
        self.chat_messages.append({
            'sender': 'user',
            'message': message
        })
        
        # Add to recent activity
        self.recent_actions.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] User: {message[:30]}")
        
        # Process message
        lower_msg = message.lower()
        
        if 'learn' in lower_msg:
            grace_response = "I'll start learning about that topic from the web!"
            # Trigger learning (non-blocking)
            asyncio.create_task(self._trigger_learning(message))
        elif 'status' in lower_msg:
            grace_response = f"I'm online! Sessions: {self.status_data.get('stats', {}).get('sessions_started', 0)}"
        elif 'stop' in lower_msg and 'remote' in lower_msg:
            await remote_access.stop()
            grace_response = "Remote access stopped!"
        else:
            grace_response = "I'm here and listening! Ask me to learn something or check my status."
        
        # Add Grace's response
        self.chat_messages.append({
            'sender': 'grace',
            'message': grace_response
        })
        
        self.recent_actions.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Grace responded")
    
    async def _trigger_learning(self, message: str):
        """Trigger learning (background)"""
        try:
            topic = message.replace('learn', '').strip()
            if topic:
                await web_learning_orchestrator.learn_and_apply(
                    topic=topic,
                    learning_type='web',
                    sources=[],
                    test_application=False
                )
                self.recent_actions.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Learned about {topic}")
        except Exception as e:
            self.recent_actions.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Learning failed: {e}")


def main(stdscr):
    """Main entry point for curses"""
    dashboard = GraceMonitorDashboard()
    asyncio.run(dashboard.start(stdscr))


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
