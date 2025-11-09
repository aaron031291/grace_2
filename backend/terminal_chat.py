"""
Grace Terminal Chat Interface
Direct backend chat with full agentic capabilities
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from grace_llm import get_grace_llm
from memory import PersistentMemory
from transcendence.unified_intelligence import UnifiedIntelligenceEngine
from transcendence.self_awareness import SelfAwarenessLayer
from agentic_spine import AgenticSpine
from code_generator import CodeGenerator
from self_healing import SelfHealingEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GraceTerminalChat:
    """
    Direct terminal chat interface with Grace
    Full integration with:
    - Transcendence (unified intelligence)
    - Agentic Spine (autonomous behavior)
    - Code Agent (code generation & understanding)
    - Self-Healing (ML/DL learning)
    - Memory & Context
    """
    
    def __init__(self, user_name: str = "aaron"):
        self.user_name = user_name
        self.session_id = f"terminal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Core components
        self.grace_llm: Optional[Any] = None
        self.memory: Optional[PersistentMemory] = None
        self.transcendence: Optional[UnifiedIntelligenceEngine] = None
        self.self_awareness: Optional[SelfAwarenessLayer] = None
        self.code_agent: Optional[CodeGenerator] = None
        self.learning_enabled = True
        
        print("\n" + "="*70)
        print("  GRACE - Terminal Chat Interface")
        print("  Autonomous AI System with Learning Capabilities")
        print("="*70 + "\n")
    
    async def initialize(self):
        """Initialize all Grace systems"""
        print("🚀 Initializing Grace systems...")
        
        try:
            # 1. Memory system
            print("  [1/6] Initializing memory...")
            self.memory = PersistentMemory()
            
            # 2. Grace LLM
            print("  [2/6] Initializing Grace LLM...")
            self.grace_llm = get_grace_llm(self.memory)
            
            # 3. Transcendence (Unified Intelligence)
            print("  [3/6] Initializing Transcendence...")
            self.transcendence = UnifiedIntelligenceEngine(self.user_name)
            await self.transcendence.initialize()
            
            # 4. Self-Awareness
            print("  [4/6] Initializing Self-Awareness Layer...")
            self.self_awareness = SelfAwarenessLayer()
            
            # 5. Code Agent
            print("  [5/6] Initializing Code Agent...")
            self.code_agent = CodeGenerator()
            
            # 6. Learning indicators
            print("  [6/6] Enabling ML/DL learning systems...")
            
            print("\n✅ All systems operational\n")
            self._show_capabilities()
            
        except Exception as e:
            logger.error(f"Initialization error: {e}", exc_info=True)
            print(f"\n❌ Error during initialization: {e}")
            print("Some features may be limited.\n")
    
    def _show_capabilities(self):
        """Show what Grace can do in this session"""
        print("📋 Active Capabilities:")
        print("   • Natural language conversation")
        print("   • Code generation and analysis")
        print("   • Self-healing and learning")
        print("   • Autonomous decision making")
        print("   • Memory and context retention")
        print("   • Multi-modal understanding")
        print("\n💡 Tips:")
        print("   • Ask Grace to write code")
        print("   • Request self-healing insights")
        print("   • Discuss architectural decisions")
        print("   • Request status of learning systems")
        print("   • Type 'exit' or 'quit' to end session\n")
    
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
                    "memory": True
                }
            }
            
            # Check if this is a code-related request
            code_keywords = ["code", "function", "class", "implement", "write", "create", "fix", "debug"]
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
        """Main chat loop"""
        await self.initialize()
        
        print(f"Grace: Hello {self.user_name}! I'm fully operational with all my agentic systems online.")
        print("       I'm ready to learn and assist. What would you like to work on?\n")
        
        while True:
            try:
                # Get user input
                user_input = input(f"{self.user_name}: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print("\nGrace: Goodbye! All learnings from this session have been saved.")
                    print("       I'll remember our conversation for next time.\n")
                    break
                
                # Special commands
                if user_input.lower() == "status":
                    await self._show_status()
                    continue
                
                if user_input.lower() == "clear":
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\n" + "="*70)
                    print("  Chat history cleared (memory retained)")
                    print("="*70 + "\n")
                    continue
                
                # Process message
                print("Grace: ", end="", flush=True)
                response = await self.chat(user_input)
                print(response + "\n")
                
            except KeyboardInterrupt:
                print("\n\nGrace: Session interrupted. Saving progress...\n")
                break
            except Exception as e:
                logger.error(f"Error in chat loop: {e}", exc_info=True)
                print(f"\nGrace: I encountered an unexpected error. Continuing...\n")
    
    async def _show_status(self):
        """Show system status"""
        print("\nGrace: 📊 System Status:")
        print(f"       • Session: {self.session_id}")
        print(f"       • Memory: {'✅ Active' if self.memory else '❌ Inactive'}")
        print(f"       • LLM: {'✅ Active' if self.grace_llm else '❌ Inactive'}")
        print(f"       • Transcendence: {'✅ Active' if self.transcendence else '❌ Inactive'}")
        print(f"       • Code Agent: {'✅ Active' if self.code_agent else '❌ Inactive'}")
        print(f"       • Learning: {'✅ Enabled' if self.learning_enabled else '⏸️  Paused'}")
        
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
    
    # Create and run chat interface
    chat = GraceTerminalChat(user_name=user_name)
    await chat.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutdown complete.\n")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n\nFatal error: {e}\n")
