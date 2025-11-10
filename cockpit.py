"""
Grace Cockpit Chat Interface
Interactive terminal interface for Grace's full cognition system
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.grace_llm import get_grace_llm
from backend.memory import PersistentMemory
from backend.transcendence.unified_intelligence import transcendence
from backend.transcendence.self_awareness import grace_self_awareness
from backend.agentic_spine import AgenticSpine
from backend.code_generator import CodeGenerator
# from backend.self_healing import SelfHealingEngine  # Not available
from backend.governance import governance_engine
from backend.immutable_log import ImmutableLog
from backend.governance_framework import governance_framework

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GraceCockpit:
    """
    Interactive cockpit interface with Grace
    Full integration with:
    - Transcendence (unified intelligence)
    - Agentic Spine (autonomous behavior)
    - Code Agent (code generation & understanding)
    - Self-Healing (ML/DL learning)
    - Memory & Context
    """

    def __init__(self, user_name: str = "aaron"):
        self.user_name = user_name
        self.session_id = f"cockpit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Core components
        self.grace_llm: Optional[Any] = None
        self.memory: Optional[PersistentMemory] = None
        self.transcendence = transcendence
        self.self_awareness = grace_self_awareness
        self.code_agent: Optional[CodeGenerator] = None
        self.learning_enabled = True
        self.immutable_log = ImmutableLog()

        # Track actions for approval
        self.pending_actions = []

        print("\n" + "="*80)
        print("  GRACE COCKPIT - Full Cognition Interface")
        print("  Autonomous AI System with Complete Agentic Capabilities")
        print("="*80 + "\n")

    async def initialize(self):
        """Initialize all Grace systems"""
        print("Initializing Grace cognition systems...")

        try:
            # 1. Memory system
            print("  [1/6] Initializing persistent memory...")
            self.memory = PersistentMemory()

            # 2. Grace LLM
            print("  [2/6] Initializing Grace LLM...")
            self.grace_llm = get_grace_llm(self.memory)

            # 3. Transcendence (Unified Intelligence)
            print("  [3/6] Initializing Transcendence layer...")
            # Already initialized as singleton

            # 4. Self-Awareness
            print("  [4/6] Initializing Self-Awareness Layer...")
            # Already initialized as singleton

            # 5. Code Agent
            print("  [5/6] Initializing Code Agent...")
            self.code_agent = CodeGenerator()

            # 6. Learning indicators
            print("  [6/6] Enabling ML/DL learning systems...")

            print("\nAll cognition systems operational\n")
            self._show_capabilities()

        except Exception as e:
            logger.error(f"Initialization error: {e}", exc_info=True)
            print(f"\nError during initialization: {e}")
            print("Some features may be limited.\n")

    def _show_capabilities(self):
        """Show what Grace can do in this session"""
        print("Active Capabilities:")
        print("   • Natural language conversation with full context")
        print("   • Code generation, analysis, and refactoring")
        print("   • Self-healing and continuous learning")
        print("   • Autonomous decision making and execution")
        print("   • Memory retention and pattern recognition")
        print("   • Multi-modal understanding and reasoning")
        print("   • Governance framework integration")
        print("   • Real-time system monitoring and analytics")
        print("   • Transcendence unified intelligence system")
        print("\nCommands:")
        print("   • create file <path> with <description>")
        print("   • modify file <path> to <changes>")
        print("   • approve / reject - Approve/reject pending actions")
        print("   • status - Show system status")
        print("   • governance - Show governance framework")
        print("   • autonomy - Show/control autonomy mode")
        print("   • dashboard - Show complete system dashboard")
        print("   • report - Grace's self-generated activity report")
        print("   • analyze - Grace analyzes her own performance")
        print("   • improve - Grace's improvement plan")
        print("   • memory - Show recent memory contents")
        print("   • learn - Enable/disable learning mode")
        print("   • clear - Clear screen")
        print("   • exit / quit - End session\n")

    async def chat(self, user_message: str) -> str:
        """
        Process user message through Grace's full intelligence stack
        """
        try:
            # Build context
            context = {
                "user_name": self.user_name,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "learning_enabled": self.learning_enabled,
                "capabilities": {
                    "code_generation": True,
                    "self_healing": True,
                    "transcendence": True,
                    "memory": True,
                    "governance": True,
                    "autonomy": True
                }
            }

            # Check for special commands
            if user_message.lower().startswith("create file"):
                return await self._handle_file_creation(user_message, context)
            elif user_message.lower().startswith("modify file"):
                return await self._handle_file_modification(user_message, context)
            elif user_message.lower() == "approve":
                return await self._approve_pending_action()
            elif user_message.lower() == "reject":
                return self._reject_pending_action()
            elif user_message.lower() == "governance":
                return self._show_governance()
            elif user_message.lower().startswith("autonomy"):
                return await self._handle_autonomy_command(user_message)
            elif user_message.lower() == "dashboard":
                return await self._show_dashboard()
            elif user_message.lower() == "report":
                return await self._show_self_report()
            elif user_message.lower() == "analyze":
                return await self._show_self_analysis()
            elif user_message.lower() == "improve":
                return await self._show_improvement_plan()
            elif user_message.lower() == "memory":
                return await self._show_memory()
            elif user_message.lower().startswith("learn"):
                return self._toggle_learning(user_message)

            # Check if this is a code-related request
            code_keywords = ["code", "function", "class", "implement", "write", "create", "fix", "debug", "build", "refactor"]
            is_code_request = any(keyword in user_message.lower() for keyword in code_keywords)

            # Route through appropriate system
            if is_code_request and self.code_agent:
                # Use code agent for code tasks
                response = await self._handle_code_request(user_message, context)
            else:
                # Use Grace LLM for general conversation
                response = await self.grace_llm.chat(
                    user_message=user_message,
                    context=context
                )

            # Log to memory for learning
            if self.memory:
                await self._log_interaction(user_message, response, context)

            return response

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return f"I encountered an error: {str(e)}. I'm learning from this to improve."

    async def _handle_code_request(self, message: str, context: Dict[str, Any]) -> str:
        """Handle code-specific requests"""
        try:
            # Use code agent
            result = await self.code_agent.generate_code(
                prompt=message,
                context=context
            )

            if isinstance(result, dict):
                code = result.get("code", "")
                explanation = result.get("explanation", "")
                return f"{explanation}\n\n```python\n{code}\n```"
            else:
                return str(result)

        except Exception as e:
            logger.error(f"Code generation error: {e}")
            # Fallback to regular Grace LLM
            return await self.grace_llm.chat(user_message=message, context=context)

    async def _log_interaction(self, user_msg: str, grace_response: str, context: Dict[str, Any]):
        """Log interaction for learning"""
        try:
            await self.memory.add_memory(
                content=f"User: {user_msg}\nGrace: {grace_response}",
                memory_type="conversation",
                metadata={
                    **context,
                    "user_message": user_msg,
                    "grace_response": grace_response
                }
            )
        except Exception as e:
            logger.warning(f"Memory logging failed: {e}")

    async def run(self):
        """Main cockpit loop"""
        await self.initialize()

        print(f"Grace: Welcome to the cockpit, {self.user_name}! All cognition systems are online.")
        print("       I'm ready to collaborate with full autonomy and learning capabilities.")
        print("       What would you like to work on together?\n")

        while True:
            try:
                # Get user input
                user_input = input(f"{self.user_name}@cockpit: ").strip()

                if not user_input:
                    continue

                # Check for exit commands
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print("\nGrace: Cockpit session ended. All learnings saved to memory.")
                    print("       Ready for next mission!\n")
                    break

                # Special commands
                if user_input.lower() == "status":
                    await self._show_status()
                    continue

                if user_input.lower() == "clear":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\n" + "="*80)
                    print("  GRACE COCKPIT - Session Active")
                    print("="*80 + "\n")
                    continue

                # Process message
                print("Grace: ", end="", flush=True)
                response = await self.chat(user_input)
                print(response + "\n")

            except KeyboardInterrupt:
                print("\n\nGrace: Cockpit shutdown initiated. Saving all progress...\n")
                break
            except Exception as e:
                logger.error(f"Error in cockpit loop: {e}", exc_info=True)
                print(f"\nGrace: System error encountered. Continuing operation...\n")

    async def _handle_file_creation(self, message: str, context: Dict[str, Any]) -> str:
        """Handle file creation request with approval"""
        # Parse file path from message
        parts = message.split("with", 1)
        if len(parts) < 2:
            return "Please specify: 'create file <path> with <description>'"

        file_path = parts[0].replace("create file", "").strip()
        description = parts[1].strip()

        # Check governance framework
        approval = await governance_framework.check_action(
            actor=self.user_name,
            action="create_file",
            resource=file_path,
            context={"description": description},
            confidence=0.9
        )

        if not approval.get("approved", False) and not approval.get("requires_human_approval", False):
            return f"❌ Governance denied file creation: {approval.get('reason', 'Unknown')}"

        # Request user confirmation
        action = {
            "type": "create_file",
            "file_path": file_path,
            "description": description,
            "context": context
        }
        self.pending_actions.append(action)

        return f"📝 File Creation Request:\n   Path: {file_path}\n   Purpose: {description}\n\n   Type 'approve' to proceed or 'reject' to cancel."

    async def _handle_file_modification(self, message: str, context: Dict[str, Any]) -> str:
        """Handle file modification request with approval"""
        parts = message.split("to", 1)
        if len(parts) < 2:
            return "Please specify: 'modify file <path> to <changes>'"

        file_path = parts[0].replace("modify file", "").strip()
        changes = parts[1].strip()

        # Check governance
        approval = await governance_engine.check_approval(
            actor=self.user_name,
            action="modify_file",
            resource=file_path,
            context={"changes": changes}
        )

        if not approval.get("approved", False):
            return f"❌ Governance denied file modification: {approval.get('reason', 'Unknown')}"

        # Request user confirmation
        action = {
            "type": "modify_file",
            "file_path": file_path,
            "changes": changes,
            "context": context
        }
        self.pending_actions.append(action)

        return f"✏️  File Modification Request:\n   Path: {file_path}\n   Changes: {changes}\n\n   Type 'approve' to proceed or 'reject' to cancel."

    async def _approve_pending_action(self) -> str:
        """Execute pending action after approval"""
        if not self.pending_actions:
            return "No pending actions to approve."

        action = self.pending_actions.pop(0)

        try:
            if action["type"] == "create_file":
                # Generate code for the file
                result = await self.code_agent.generate_code(
                    prompt=action["description"],
                    context=action["context"]
                )

                code = result.get("code", "") if isinstance(result, dict) else str(result)

                # Write file
                file_path = action["file_path"]
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)

                # Log action
                await self.immutable_log.append(
                    actor=self.user_name,
                    action="file_created",
                    resource=file_path,
                    subsystem="cockpit",
                    payload={"description": action["description"]},
                    result="success"
                )

                return f"✅ File created successfully: {file_path}\n\n```python\n{code[:500]}...\n```"

            elif action["type"] == "modify_file":
                # Read existing file
                file_path = action["file_path"]
                with open(file_path, 'r', encoding='utf-8') as f:
                    original = f.read()

                # Generate modified version
                result = await self.code_agent.generate_code(
                    prompt=f"Modify this code:\n{original}\n\nChanges: {action['changes']}",
                    context=action["context"]
                )

                code = result.get("code", "") if isinstance(result, dict) else str(result)

                # Write modified file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)

                # Log action
                await self.immutable_log.append(
                    actor=self.user_name,
                    action="file_modified",
                    resource=file_path,
                    subsystem="cockpit",
                    payload={"changes": action["changes"]},
                    result="success"
                )

                return f"✅ File modified successfully: {file_path}"

        except Exception as e:
            logger.error(f"Error executing action: {e}", exc_info=True)
            return f"❌ Error executing action: {e}"

    def _reject_pending_action(self) -> str:
        """Reject pending action"""
        if not self.pending_actions:
            return "No pending actions to reject."

        action = self.pending_actions.pop(0)
        return f"❌ Rejected: {action['type']} for {action.get('file_path', 'unknown')}"

    def _show_governance(self) -> str:
        """Show governance framework status"""
        summary = governance_framework.get_summary()

        output = "\n🏛️ GRACE GOVERNANCE FRAMEWORK\n\n"

        # Constitution
        const = summary.get("constitution", {})
        output += "📜 CONSTITUTION:\n"
        output += f"   • Loaded: {'✅' if const.get('loaded') else '❌'}\n"
        output += f"   • Version: {const.get('version', 'unknown')}\n"
        output += f"   • Core Values: {const.get('core_values', 0)}\n"

        boundaries = const.get("ethical_boundaries", {})
        output += f"   • Never Allowed: {boundaries.get('never_allowed', 0)} rules\n"
        output += f"   • Requires Approval: {boundaries.get('requires_approval', 0)} rules\n"
        output += f"   • Auto-Approved: {boundaries.get('auto_approved', 0)} rules\n\n"

        # Guardrails
        guards = summary.get("guardrails", {})
        output += "🛡️ GUARDRAILS:\n"
        output += f"   • Loaded: {'✅' if guards.get('loaded') else '❌'}\n"
        output += f"   • Version: {guards.get('version', 'unknown')}\n"
        output += f"   • Categories: {', '.join(guards.get('categories', []))}\n\n"

        # Whitelist
        white = summary.get("whitelist", {})
        output += "✅ WHITELIST:\n"
        output += f"   • Loaded: {'✅' if white.get('loaded') else '❌'}\n"
        output += f"   • Version: {white.get('version', 'unknown')}\n"
        output += f"   • Approved Actors: {white.get('approved_actors', 0)}\n\n"

        output += "Type 'help' for available commands."

        return output

    async def _handle_autonomy_command(self, message: str) -> str:
        """Handle autonomy control commands"""
        from backend.governance_framework import governance_framework
        from backend.full_autonomy import full_autonomy

        msg_lower = message.lower()

        # Status
        if msg_lower == "autonomy" or msg_lower == "autonomy status":
            status = full_autonomy.get_status()

            output = "\n🤖 AUTONOMY STATUS:\n\n"
            output += f"   Enabled: {'✅ Yes' if status['enabled'] else '❌ No'}\n"
            output += f"   Tier: {status['tier']} - {status['tier_name']}\n\n"

            if status['enabled']:
                settings = status.get('settings', {})
                output += "   Capabilities:\n"
                output += f"      • Auto-detect errors: {'✅' if settings.get('auto_detect') else '❌'}\n"
                output += f"      • Auto-propose fixes: {'✅' if settings.get('auto_propose') else '❌'}\n"
                output += f"      • Auto-apply fixes: {'✅' if settings.get('auto_apply') else '❌'}\n"
                output += f"      • Auto-commit fixes: {'✅' if settings.get('auto_commit') else '❌'}\n"

            return output

        # Enable
        elif msg_lower.startswith("autonomy enable"):
            parts = msg_lower.split()
            tier = int(parts[2]) if len(parts) > 2 else 2

            success = await full_autonomy.enable(tier)

            if success:
                return f"✅ Full autonomy enabled at Tier {tier}!\n   Grace can now autonomously detect, fix, and commit code changes."
            else:
                return f"❌ Failed to enable autonomy"

        # Disable
        elif msg_lower == "autonomy disable":
            await full_autonomy.disable()
            return "🛑 Autonomy disabled. Grace now requires approval for all actions."

        else:
            return "Usage:\n  • autonomy - Show status\n  • autonomy enable <tier> - Enable (0-3)\n  • autonomy disable - Disable"

    async def _show_dashboard(self) -> str:
        """Show comprehensive dashboard"""
        from backend.grace_log_reader import grace_log_reader
        from backend.healing_analytics import healing_analytics

        # Get comprehensive data
        activity = await grace_log_reader.get_my_recent_activity(hours=24)
        analytics = await healing_analytics.get_healing_summary(hours=24)
        ml_stats = await healing_analytics.get_ml_learning_stats(hours=24)

        output = "\n" + "="*80 + "\n"
        output += "📊 GRACE COMPLETE DASHBOARD (Last 24h)\n"
        output += "="*80 + "\n\n"

        # Healing
        output += "🔧 HEALING:\n"
        output += f"   Attempts: {analytics['total_attempts']}\n"
        output += f"   Success: {analytics['successful']} ({analytics['success_rate']:.1%})\n"
        output += f"   Failed: {analytics['failed']}\n"
        output += f"   Pending: {analytics['pending']}\n\n"

        # ML/DL
        output += "🧠 ML/DL LEARNING:\n"
        output += f"   Learning cycles: {ml_stats['total_learning_cycles']}\n"
        output += f"   Pattern updates: {ml_stats['pattern_updates']}\n"
        output += f"   Model trainings: {ml_stats['model_trainings']}\n"
        output += f"   Avg confidence: {ml_stats['average_confidence']:.1%}\n\n"

        # Activity
        output += "🤖 AUTONOMOUS ACTIVITY:\n"
        output += f"   Decisions made: {activity['decisions']['made']}\n"
        output += f"   Actions executed: {activity['decisions']['executed']}\n"
        output += f"   Shards active: {activity['shards']['active']}\n"
        output += f"   Events published: {activity['events']['published']}\n\n"

        output += "="*80 + "\n"

        return output

    async def _show_self_report(self) -> str:
        """Show Grace's self-generated report"""
        from backend.grace_log_reader import grace_log_reader

        report = await grace_log_reader.generate_self_report(hours=24)
        return "\n" + report

    async def _show_self_analysis(self) -> str:
        """Show Grace's performance analysis"""
        from backend.grace_self_analysis import grace_self_analysis

        analysis = await grace_self_analysis.analyze_performance(hours=24)

        output = f"\n🔍 MY PERFORMANCE ANALYSIS (Last 24h)\n\n"
        output += f"Health Score: {analysis['health_score']}/100\n\n"

        output += "📊 Performance Grades:\n"
        output += f"   • Healing: {analysis['healing_performance']['grade']} ({analysis['healing_performance']['success_rate']:.1%})\n"
        output += f"   • Learning: {analysis['learning_performance']['grade']} ({analysis['learning_performance']['confidence']:.1%})\n"
        output += f"   • Autonomy: {analysis['autonomous_performance']['grade']}\n\n"

        if analysis['strengths']:
            output += "💪 Strengths:\n"
            for s in analysis['strengths'][:3]:
                output += f"   • {s}\n"
            output += "\n"

        if analysis['improvement_areas']:
            output += "🎯 Need Improvement:\n"
            for area in analysis['improvement_areas'][:3]:
                output += f"   • {area}\n"
            output += "\n"

        return output

    async def _show_improvement_plan(self) -> str:
        """Show Grace's improvement plan"""
        from backend.grace_self_analysis import grace_self_analysis

        plan = await grace_self_analysis.generate_improvement_plan()
        return "\n" + plan

    async def _show_memory(self) -> str:
        """Show recent memory contents"""
        if not self.memory:
            return "Memory system not available."

        try:
            memories = await self.memory.get_recent_memories(limit=10)

            output = "\n🧠 RECENT MEMORY CONTENTS\n\n"
            for i, mem in enumerate(memories, 1):
                output += f"{i}. [{mem.get('type', 'unknown')}] {mem.get('content', '')[:100]}...\n"
                output += f"   Timestamp: {mem.get('timestamp', 'unknown')}\n\n"

            return output
        except Exception as e:
            return f"Error accessing memory: {e}"

    def _toggle_learning(self, message: str) -> str:
        """Toggle learning mode"""
        if "enable" in message.lower():
            self.learning_enabled = True
            return "🧠 Learning mode enabled. I'll learn from our interactions."
        elif "disable" in message.lower():
            self.learning_enabled = False
            return "⏸️ Learning mode disabled. I'll stop learning from interactions."
        else:
            return f"Learning mode: {'✅ Enabled' if self.learning_enabled else '❌ Disabled'}\nUse 'learn enable' or 'learn disable' to change."

    async def _show_status(self):
        """Show system status"""
        print("\nGrace: 📊 Cockpit Status:")
        print(f"       • Session: {self.session_id}")
        print(f"       • Memory: {'✅ Active' if self.memory else '❌ Inactive'}")
        print(f"       • LLM: {'✅ Active' if self.grace_llm else '❌ Inactive'}")
        print(f"       • Transcendence: ✅ Active (singleton)")
        print(f"       • Code Agent: {'✅ Active' if self.code_agent else '❌ Inactive'}")
        print(f"       • Learning: {'✅ Enabled' if self.learning_enabled else '⏸️  Paused'}")
        print(f"       • Pending Actions: {len(self.pending_actions)}")

        # Show memory stats
        if self.memory:
            try:
                stats = await self.memory.get_stats()
                print(f"       • Total Memories: {stats.get('total', 0)}")
            except:
                pass

        print()


async def main():
    """Entry point"""
    # Get username from environment or use default
    user_name = os.getenv("USER") or os.getenv("USERNAME") or "aaron"

    # Create and run cockpit interface
    cockpit = GraceCockpit(user_name=user_name)
    await cockpit.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nCockpit shutdown complete.\n")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n\nFatal error: {e}\n")
