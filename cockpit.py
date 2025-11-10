#!/usr/bin/env python3
"""
Grace Cockpit Chat Interface

Interactive WebSocket-based chat interface for Grace's full cognition system.
Provides real-time communication, system monitoring, and command execution.

Features:
- WebSocket chat with Grace's cognition authority
- Real-time system status and metrics
- Command parsing and structured execution
- Approval workflow for high-risk actions
- Dashboard views for system monitoring
- Full integration with Grace's agentic systems
"""

import asyncio
import json
import websockets
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.cognition_intent import cognition_authority
from backend.websocket_handler import websocket_manager
from backend.cognition_metrics import get_metrics_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraceCockpit:
    """
    WebSocket-based cockpit interface for Grace's cognition system
    """

    def __init__(self, backend_url: str = "ws://localhost:8000/ws/cognition"):
        self.backend_url = backend_url
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.session_id = f"cockpit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_name = "cockpit_user"
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

    async def connect(self):
        """Connect to Grace backend WebSocket"""
        try:
            async with websockets.connect(self.backend_url) as websocket:
                self.websocket = websocket
                logger.info(f"Connected to Grace backend at {self.backend_url}")

                # Send initial connection message
                await self.send_message({
                    "type": "cockpit_connect",
                    "session_id": self.session_id,
                    "user_name": self.user_name,
                    "timestamp": datetime.now().isoformat()
                })

                # Start message handling loop
                await self.message_loop()

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            print(f"❌ Failed to connect to Grace backend: {e}")
            print("Make sure the backend is running with WebSocket support")

    async def send_message(self, message: Dict[str, Any]):
        """Send message to backend"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))

    async def message_loop(self):
        """Handle incoming messages from backend"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed")
        except Exception as e:
            logger.error(f"Message loop error: {e}")

    async def handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = data.get("type", "unknown")

        if message_type == "chat_response":
            await self.display_chat_response(data)

        elif message_type == "status_update":
            await self.display_status_update(data)

        elif message_type == "approval_required":
            await self.handle_approval_request(data)

        elif message_type == "system_event":
            await self.display_system_event(data)

        elif message_type == "error":
            await self.display_error(data)

        else:
            logger.info(f"Unhandled message type: {message_type}")

    async def display_chat_response(self, data: Dict[str, Any]):
        """Display chat response from Grace"""
        message = data.get("message", "")
        timestamp = data.get("timestamp", "")

        print(f"\n🤖 Grace [{timestamp}]:")
        print(f"   {message}")
        print()

    async def display_status_update(self, data: Dict[str, Any]):
        """Display system status update"""
        status = data.get("status", {})

        print(f"\n📊 System Status Update:")
        print(f"   Health: {status.get('overall_health', 0):.1f}%")
        print(f"   Trust: {status.get('overall_trust', 0):.1f}%")
        print(f"   Confidence: {status.get('overall_confidence', 0):.1f}%")
        print(f"   SaaS Ready: {'✅' if status.get('saas_ready') else '❌'}")
        print()

    async def handle_approval_request(self, data: Dict[str, Any]):
        """Handle approval request for high-risk action"""
        approval_id = data.get("approval_id")
        action = data.get("action", {})
        reason = data.get("reason", "High-risk action requires approval")

        self.pending_approvals[approval_id] = action

        print(f"\n⚠️  APPROVAL REQUIRED:")
        print(f"   Action: {action.get('type', 'unknown')}")
        print(f"   Target: {action.get('target', 'unknown')}")
        print(f"   Reason: {reason}")
        print(f"   ID: {approval_id}")
        print()
        print("Type 'approve <id>' or 'reject <id>' to respond")
        print()

    async def display_system_event(self, data: Dict[str, Any]):
        """Display system event"""
        event_type = data.get("event_type", "unknown")
        message = data.get("message", "")

        print(f"\n🔔 System Event [{event_type}]:")
        print(f"   {message}")
        print()

    async def display_error(self, data: Dict[str, Any]):
        """Display error message"""
        error = data.get("error", "Unknown error")

        print(f"\n❌ Error:")
        print(f"   {error}")
        print()

    async def send_chat_message(self, message: str):
        """Send chat message to Grace"""
        await self.send_message({
            "type": "chat",
            "message": message,
            "session_id": self.session_id,
            "user_name": self.user_name,
            "timestamp": datetime.now().isoformat()
        })

    async def request_status(self):
        """Request current system status"""
        await self.send_message({
            "type": "status_request",
            "timestamp": datetime.now().isoformat()
        })

    async def subscribe_to_updates(self, subscriptions: list = None):
        """Subscribe to real-time updates"""
        if subscriptions is None:
            subscriptions = ["status", "events", "metrics"]

        await self.send_message({
            "type": "subscribe",
            "subscriptions": subscriptions,
            "timestamp": datetime.now().isoformat()
        })

    async def run_interactive(self):
        """Run interactive cockpit session"""
        print("\n" + "="*70)
        print("  GRACE COCKPIT - Interactive AI Control Center")
        print("  Full Cognition System Access via WebSocket")
        print("="*70)
        print()
        print("Commands:")
        print("  • Type any message to chat with Grace")
        print("  • 'status' - Get current system status")
        print("  • 'dashboard' - Show full system dashboard")
        print("  • 'subscribe' - Subscribe to real-time updates")
        print("  • 'approve <id>' - Approve pending action")
        print("  • 'reject <id>' - Reject pending action")
        print("  • 'help' - Show this help")
        print("  • 'exit' - Exit cockpit")
        print()

        # Connect to backend
        connect_task = asyncio.create_task(self.connect())

        # Start input loop
        while True:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, f"{self.user_name}: ")

                if not user_input.strip():
                    continue

                command = user_input.strip().lower()

                if command == "exit":
                    break

                elif command == "help":
                    self.show_help()

                elif command == "status":
                    await self.request_status()

                elif command == "dashboard":
                    await self.show_dashboard()

                elif command == "subscribe":
                    await self.subscribe_to_updates()

                elif command.startswith("approve "):
                    approval_id = command.split(" ", 1)[1]
                    await self.approve_action(approval_id)

                elif command.startswith("reject "):
                    approval_id = command.split(" ", 1)[1]
                    await self.reject_action(approval_id)

                else:
                    # Send as chat message
                    await self.send_chat_message(user_input)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Input error: {e}")

        # Cleanup
        connect_task.cancel()
        try:
            await connect_task
        except asyncio.CancelledError:
            pass

        print("\n👋 Cockpit session ended")

    def show_help(self):
        """Show help information"""
        print("\n" + "="*50)
        print("GRACE COCKPIT HELP")
        print("="*50)
        print()
        print("CHAT COMMANDS:")
        print("  • Any text - Chat with Grace's cognition system")
        print("  • 'create file <path> with <description>' - Create files")
        print("  • 'modify file <path> to <changes>' - Modify files")
        print("  • 'show status' - Get system status")
        print("  • 'run diagnostics' - Run system diagnostics")
        print()
        print("SYSTEM COMMANDS:")
        print("  • status - Get current system status")
        print("  • dashboard - Show full system dashboard")
        print("  • subscribe - Subscribe to real-time updates")
        print("  • approve <id> - Approve pending action")
        print("  • reject <id> - Reject pending action")
        print()
        print("SPECIAL COMMANDS:")
        print("  • help - Show this help")
        print("  • exit - Exit cockpit")
        print()

    async def show_dashboard(self):
        """Show comprehensive system dashboard"""
        print("\n" + "="*70)
        print("GRACE SYSTEM DASHBOARD")
        print("="*70)

        try:
            # Get metrics from cognition engine
            engine = get_metrics_engine()
            status = engine.get_status()

            print("\n📊 OVERALL METRICS:")
            print(f"   Health: {status.get('overall_health', 0):.1f}%")
            print(f"   Trust: {status.get('overall_trust', 0):.1f}%")
            print(f"   Confidence: {status.get('overall_confidence', 0):.1f}%")
            print(f"   SaaS Ready: {'✅' if status.get('saas_ready') else '❌'}")

            domains = status.get('domains', {})
            print("\n🏛️  DOMAIN STATUS:")
            for domain, metrics in domains.items():
                health = metrics.get('health', 0)
                trust = metrics.get('trust', 0)
                confidence = metrics.get('confidence', 0)
                status_icon = "🟢" if health > 80 else "🟡" if health > 60 else "🔴"
                print(f"   {status_icon} {domain.upper()}: H{health:.0f}% T{trust:.0f}% C{confidence:.0f}%")

            print("\n⏰ SESSION INFO:")
            print(f"   Session ID: {self.session_id}")
            print(f"   Connected: {datetime.now().isoformat()}")
            print(f"   Pending Approvals: {len(self.pending_approvals)}")

        except Exception as e:
            print(f"❌ Error getting dashboard data: {e}")

        print("="*70)
        print()

    async def approve_action(self, approval_id: str):
        """Approve a pending action"""
        if approval_id not in self.pending_approvals:
            print(f"❌ No pending approval with ID: {approval_id}")
            return

        action = self.pending_approvals[approval_id]

        await self.send_message({
            "type": "approval_response",
            "approval_id": approval_id,
            "approved": True,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })

        del self.pending_approvals[approval_id]
        print(f"✅ Approved action: {approval_id}")

    async def reject_action(self, approval_id: str):
        """Reject a pending action"""
        if approval_id not in self.pending_approvals:
            print(f"❌ No pending approval with ID: {approval_id}")
            return

        action = self.pending_approvals[approval_id]

        await self.send_message({
            "type": "approval_response",
            "approval_id": approval_id,
            "approved": False,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })

        del self.pending_approvals[approval_id]
        print(f"❌ Rejected action: {approval_id}")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Grace Cockpit - Interactive AI Control Center")
    parser.add_argument("--backend", default="ws://localhost:8000/ws/cognition",
                       help="Backend WebSocket URL")
    parser.add_argument("--user", default="cockpit_user",
                       help="Username for session")

    args = parser.parse_args()

    cockpit = GraceCockpit(backend_url=args.backend)
    cockpit.user_name = args.user

    try:
        await cockpit.run_interactive()
    except KeyboardInterrupt:
        print("\n\n👋 Cockpit shutdown")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n💥 Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
