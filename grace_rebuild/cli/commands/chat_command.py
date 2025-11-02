"""
Chat command - Interactive chat with Grace using streaming
"""

import asyncio
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from ..grace_client import GraceAPIClient


class ChatCommand:
    """Chat with Grace AI"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
        self.history = []
    
    async def execute(self, message: Optional[str] = None):
        """Execute chat command"""
        if not self.client.is_authenticated():
            self.console.print("[red]Please login first[/red]")
            return
        
        if message:
            # Single message mode
            await self.send_message(message)
        else:
            # Interactive chat mode
            await self.interactive_mode()
    
    async def send_message(self, message: str):
        """Send a single message to Grace"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Display user message
        self.console.print(f"\n[bold cyan]You ({timestamp}):[/bold cyan]")
        self.console.print(Panel(message, border_style="cyan"))
        
        # Show loading indicator
        with self.console.status("[bold magenta]Grace is thinking...", spinner="dots"):
            response = await self.client.chat(message)
        
        if response.success:
            # Display Grace's response
            response_text = response.data.get("response", "No response")
            self.console.print(f"\n[bold magenta]Grace ({timestamp}):[/bold magenta]")
            
            # Render as markdown if it looks like markdown
            if any(marker in response_text for marker in ['#', '*', '`', '-', '1.']):
                self.console.print(Panel(Markdown(response_text), border_style="magenta"))
            else:
                self.console.print(Panel(response_text, border_style="magenta"))
            
            # Add to history
            self.history.append({
                "role": "user",
                "content": message,
                "timestamp": timestamp
            })
            self.history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": timestamp
            })
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def interactive_mode(self):
        """Interactive chat session"""
        self.console.print("\n[bold green]Interactive Chat Mode[/bold green]")
        self.console.print("[dim]Type your message and press Enter. Type 'exit' to return.[/dim]\n")
        
        while True:
            try:
                # Get user input
                user_input = await asyncio.to_thread(
                    self.console.input,
                    "[bold cyan]You:[/bold cyan] "
                )
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    break
                
                if user_input.lower() == 'history':
                    await self.show_history()
                    continue
                
                if user_input.lower() == 'clear':
                    self.console.clear()
                    continue
                
                # Send message
                await self.send_message(user_input)
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Type 'exit' to return to main menu[/yellow]")
            except EOFError:
                break
    
    async def show_history(self):
        """Show chat history"""
        if not self.history:
            self.console.print("[dim]No chat history[/dim]")
            return
        
        self.console.print("\n[bold]Chat History:[/bold]")
        for msg in self.history[-20:]:  # Last 20 messages
            role = msg["role"]
            timestamp = msg["timestamp"]
            content = msg["content"]
            
            if role == "user":
                self.console.print(f"\n[cyan]{timestamp} You:[/cyan] {content}")
            else:
                self.console.print(f"\n[magenta]{timestamp} Grace:[/magenta] {content}")
        
        self.console.print()
    
    async def stream_response(self, message: str):
        """Stream response from Grace (for future WebSocket implementation)"""
        # TODO: Implement WebSocket streaming
        pass
