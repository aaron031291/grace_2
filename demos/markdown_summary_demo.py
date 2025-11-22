# demos/markdown_summary_demo.py
import asyncio
import sys
import os
import json

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_core import GraceAgent
from memory_buffer import MemoryBuffer

class MockLLM:
    async def generate(self, prompt: str) -> dict:
        print(f"\n[MockLLM] Received prompt: {prompt[:50]}...")
        
        if "Decompose the following goal" in prompt:
            return {"steps": ["Search for 'Grace AI'", "Read the first result", "Write summary to summary.md"]}
        
        if "Current Sub-Goal: Search for 'Grace AI'" in prompt:
            return {"tool": "search_web", "args": {"query": "Grace AI"}}
        
        if "Current Sub-Goal: Read the first result" in prompt:
            return {"tool": "read_file", "args": {"path": "README.md"}} # Mocking read of a local file for simplicity
        
        if "Current Sub-Goal: Write summary to summary.md" in prompt:
            return {"tool": "write_file", "args": {"path": "summary.md", "content": "# Grace AI Summary\nGrace is an agentic AI system."}}
        
        if "Summarize what you learned" in prompt:
            return {"reflection": "I successfully executed a step towards the goal."}
            
        # Default fallback
        return {"tool": "run_command", "args": {"command": "echo 'No action determined'"}}

async def main():
    print("=== Starting Markdown Summary Demo ===")
    
    # Initialize components
    memory = MemoryBuffer()
    llm = MockLLM()
    agent = GraceAgent(llm, memory)
    
    goal = "Create a markdown summary of Grace AI"
    print(f"Goal: {goal}")
    
    # Run agent
    history = await agent.run(goal)
    
    print("\n=== Execution History ===")
    for step in history:
        print(f"Action: {step['action']}")
        print(f"Result: {step['result']}")
    
    # Verify output
    if os.path.exists("summary.md"):
        with open("summary.md", "r") as f:
            content = f.read()
            print("\n=== Generated Summary ===")
            print(content)
            print("\n[SUCCESS] Summary file created.")
    else:
        print("\n[FAIL] Summary file not found.")

if __name__ == "__main__":
    asyncio.run(main())
