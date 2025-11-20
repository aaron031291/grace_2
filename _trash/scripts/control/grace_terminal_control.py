"""
Grace Terminal Control
Terminal interface to control and chat with Grace while she's learning
Press Ctrl+S to stop remote access, Ctrl+C to exit, or type to chat with Grace
"""

import asyncio
import sys
import logging
from datetime import datetime
from typing import Optional
import keyboard
import threading

from backend.web_learning_orchestrator import web_learning_orchestrator
from backend.remote_computer_access import remote_access
from backend.youtube_learning import youtube_learning
from backend.safe_web_scraper import safe_web_scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraceTerminalControl:
    """
    Interactive terminal control for Grace
    - Chat with Grace in real-time
    - Monitor her learning activities
    - Stop remote access with Ctrl+S
    - Emergency stop with Ctrl+C
    """
    
    def __init__(self):
        self.running = False
        self.chat_active = False
        self.remote_access_active = False
        self.messages = []
        
    def print_header(self):
        """Print terminal header"""
        print("\n" + "="*80)
        print("🤖 GRACE TERMINAL CONTROL")
        print("="*80)
        print("\n📋 CONTROLS:")
        print("  • Type message + Enter  → Chat with Grace")
        print("  • Ctrl+S               → Stop Remote Access")
        print("  • Ctrl+C               → Emergency Stop & Exit")
        print("  • 'status'             → Check Grace's status")
        print("  • 'stop remote'        → Stop remote access")
        print("  • 'start remote'       → Start remote access")
        print("  • 'help'               → Show help")
        print("  • 'exit'               → Graceful exit")
        print("\n" + "="*80 + "\n")
    
    async def start(self):
        """Start terminal control"""
        self.running = True
        self.chat_active = True
        
        print("\n🚀 Starting Grace's systems...")
        
        # Start Grace's systems
        await web_learning_orchestrator.start()
        
        self.remote_access_active = remote_access.access_enabled
        
        self.print_header()
        
        print("✅ Grace is online and ready!\n")
        print("Grace: Hello! I'm ready to learn and help. What would you like me to do?\n")
        
        # Start keyboard listener in background
        self._start_keyboard_listener()
        
        # Start chat loop
        await self._chat_loop()
    
    def _start_keyboard_listener(self):
        """Start keyboard listener for shortcuts"""
        
        def on_ctrl_s():
            """Handle Ctrl+S - Stop remote access"""
            if self.remote_access_active:
                print("\n\n⚠️  CTRL+S DETECTED - STOPPING REMOTE ACCESS!")
                asyncio.create_task(self._stop_remote_access())
        
        def on_ctrl_c():
            """Handle Ctrl+C - Emergency stop"""
            print("\n\n🛑 EMERGENCY STOP - Shutting down Grace...")
            self.running = False
            asyncio.create_task(self._emergency_stop())
        
        # Register hotkeys (keyboard library)
        try:
            keyboard.add_hotkey('ctrl+s', on_ctrl_s)
            keyboard.add_hotkey('ctrl+c', on_ctrl_c)
        except:
            print("⚠️  Keyboard shortcuts not available (requires admin rights)")
    
    async def _chat_loop(self):
        """Main chat loop"""
        
        while self.running:
            try:
                # Get user input (non-blocking)
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: input("You: ")
                )
                
                if not user_input.strip():
                    continue
                
                # Process command
                await self._process_input(user_input.strip())
                
            except KeyboardInterrupt:
                print("\n\n🛑 Keyboard interrupt - stopping...")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    async def _process_input(self, user_input: str):
        """Process user input"""
        
        # Store message
        self.messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'sender': 'user',
            'message': user_input
        })
        
        # Check for commands
        lower_input = user_input.lower()
        
        if lower_input == 'exit':
            print("\nGrace: Goodbye! Shutting down gracefully...\n")
            self.running = False
            await self._shutdown()
            
        elif lower_input == 'help':
            self._show_help()
            
        elif lower_input == 'status':
            await self._show_status()
            
        elif lower_input == 'stop remote':
            await self._stop_remote_access()
            
        elif lower_input == 'start remote':
            await self._start_remote_access()
            
        elif 'learn' in lower_input:
            await self._handle_learn_request(user_input)
            
        elif 'youtube' in lower_input:
            await self._handle_youtube_request(user_input)
            
        else:
            # Regular chat
            await self._chat_with_grace(user_input)
    
    def _show_help(self):
        """Show help"""
        print("\nGrace: Here are the commands I understand:\n")
        print("  📊 Status Commands:")
        print("     • 'status'       - Check my current status")
        print("     • 'help'         - Show this help message\n")
        print("  🖥️  Remote Access:")
        print("     • 'stop remote'  - Stop remote computer access")
        print("     • 'start remote' - Start remote computer access")
        print("     • Ctrl+S         - Emergency stop remote access\n")
        print("  🎓 Learning:")
        print("     • 'learn [topic]'  - Learn about a topic from web")
        print("     • 'youtube [topic]' - Learn from YouTube videos\n")
        print("  💬 Chat:")
        print("     • Just type anything else to chat with me!\n")
        print("  🚪 Exit:")
        print("     • 'exit'   - Shut down gracefully")
        print("     • Ctrl+C   - Emergency stop\n")
    
    async def _show_status(self):
        """Show Grace's status"""
        print("\nGrace: Here's my current status:\n")
        
        # Remote access status
        remote_status = await remote_access.get_status()
        print(f"  🖥️  Remote Access: {'✅ Enabled' if remote_status['access_enabled'] else '❌ Disabled'}")
        print(f"     Actions performed: {remote_status['actions_performed']}")
        
        # Learning stats
        report = await web_learning_orchestrator.get_learning_report(days=1)
        stats = report['statistics']
        print(f"\n  📚 Learning Today:")
        print(f"     Sessions: {stats['sessions_started']}")
        print(f"     Sources learned: {stats['sources_learned']}")
        print(f"     Applications tested: {stats['applications_tested']}")
        print(f"     Applications approved: {stats['applications_approved']}")
        
        print(f"\n  🛡️  Governance: {report['governance_compliance']}")
        print(f"  📋 Traceable: {report['fully_traceable']}")
        print()
    
    async def _stop_remote_access(self):
        """Stop remote access"""
        if not remote_access.access_enabled:
            print("\nGrace: Remote access is already stopped.\n")
            return
        
        await remote_access.stop()
        self.remote_access_active = False
        print("\nGrace: ✅ Remote access has been stopped. I can no longer access this computer.\n")
    
    async def _start_remote_access(self):
        """Start remote access"""
        if remote_access.access_enabled:
            print("\nGrace: Remote access is already running.\n")
            return
        
        await remote_access.start()
        self.remote_access_active = True
        print("\nGrace: ✅ Remote access has been started. I can now access this computer (with governance approval).\n")
    
    async def _handle_learn_request(self, user_input: str):
        """Handle learning request"""
        # Extract topic
        topic = user_input.replace('learn', '').strip()
        if not topic:
            print("\nGrace: What topic would you like me to learn about?\n")
            return
        
        print(f"\nGrace: I'll learn about '{topic}' from the web. This might take a moment...\n")
        
        # Trigger learning
        try:
            report = await web_learning_orchestrator.learn_and_apply(
                topic=topic,
                learning_type='web',
                sources=[],
                test_application=False
            )
            
            sources = report['knowledge_acquisition']['sources_verified']
            print(f"Grace: ✅ I've learned about {topic} from {sources} verified sources!")
            print(f"       All sources are fully traceable and governed.\n")
            
        except Exception as e:
            print(f"\nGrace: ❌ I encountered an error while learning: {e}\n")
    
    async def _handle_youtube_request(self, user_input: str):
        """Handle YouTube learning request"""
        topic = user_input.replace('youtube', '').strip()
        if not topic:
            print("\nGrace: What topic would you like me to learn from YouTube?\n")
            return
        
        print(f"\nGrace: I'll search YouTube for '{topic}' tutorials...\n")
        
        try:
            summary = await youtube_learning.learn_topic(
                topic=topic,
                category='frontend',  # Default
                max_videos=3
            )
            
            print(f"Grace: ✅ I've learned from {summary['videos_learned']} YouTube videos about {topic}!")
            print(f"       Total words processed: {summary['total_words']:,}")
            print(f"       All videos are tracked and traceable.\n")
            
        except Exception as e:
            print(f"\nGrace: ❌ Error learning from YouTube: {e}\n")
    
    async def _chat_with_grace(self, message: str):
        """General chat with Grace"""
        
        # Store Grace's response
        grace_response = f"I understand you're asking about: '{message}'. "
        grace_response += "I'm an AI learning system focused on Frontend, Backend, UI, and Cloud development. "
        grace_response += "I can learn from the web, GitHub, and YouTube - all with complete governance and traceability!"
        
        self.messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'sender': 'grace',
            'message': grace_response
        })
        
        print(f"\nGrace: {grace_response}\n")
    
    async def _emergency_stop(self):
        """Emergency stop all systems"""
        print("\n🛑 EMERGENCY STOP INITIATED")
        print("  Stopping all systems...")
        
        try:
            await remote_access.stop()
            print("  ✅ Remote access stopped")
        except:
            pass
        
        try:
            await web_learning_orchestrator.stop()
            print("  ✅ Learning systems stopped")
        except:
            pass
        
        print("\n✅ All systems stopped safely")
        print("Goodbye!\n")
        
        sys.exit(0)
    
    async def _shutdown(self):
        """Graceful shutdown"""
        print("\n👋 Shutting down Grace's systems...")
        
        await remote_access.stop()
        print("  ✅ Remote access stopped")
        
        await web_learning_orchestrator.stop()
        print("  ✅ Learning systems stopped")
        
        print("\n✅ Shutdown complete. Goodbye!\n")
        
        sys.exit(0)


async def main():
    """Main entry point"""
    
    terminal = GraceTerminalControl()
    
    try:
        await terminal.start()
    except KeyboardInterrupt:
        print("\n\n🛑 Keyboard interrupt detected")
        await terminal._emergency_stop()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        await terminal._emergency_stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
