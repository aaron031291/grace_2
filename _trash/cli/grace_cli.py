#!/usr/bin/env python3
"""
Grace CLI - Modern Terminal Interface for Grace AI System

A rich, multi-panel TUI that routes all commands through Grace's
cognition systems: reflection, governance, hunter, verification.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.syntax import Syntax
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML

console = Console()

class GraceCLI:
    """Main CLI application with multi-panel TUI"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.ws_url = backend_url.replace("http", "ws")
        
        # State
        self.current_user = None
        self.auth_token = None
        self.current_workspace = Path.cwd()
        self.chat_history = []
        self.tasks = []
        self.alerts = []
        self.reflections = []
        
        # UI Components
        self.layout = self._create_layout()
        self.session = None
        
        # WebSocket connections
        self.ws_connections = {}
        
        console.print("[bold green]Grace CLI v1.0[/bold green] - Initializing...\n")
    
    def _create_layout(self) -> Layout:
        """Create multi-panel layout"""
        
        layout = Layout(name="root")
        
        # Split into header, body, footer
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Split body into left sidebar and main content
        layout["body"].split_row(
            Layout(name="sidebar", ratio=1),
            Layout(name="main", ratio=3)
        )
        
        # Split main into chat and console
        layout["main"].split(
            Layout(name="chat", ratio=2),
            Layout(name="console", ratio=1)
        )
        
        # Split sidebar into navigation and tasks
        layout["sidebar"].split(
            Layout(name="nav", ratio=1),
            Layout(name="tasks", ratio=1)
        )
        
        return layout
    
    def _render_header(self) -> Panel:
        """Render header with user info and status"""
        
        user_text = f"👤 {self.current_user or 'Guest'}" if self.current_user else "👤 Not logged in"
        workspace_text = f"📁 {self.current_workspace.name}"
        time_text = datetime.now().strftime("%H:%M:%S")
        
        header = Table.grid(padding=1)
        header.add_column(justify="left", ratio=1)
        header.add_column(justify="center", ratio=1)
        header.add_column(justify="right", ratio=1)
        
        header.add_row(
            Text(user_text, style="bold cyan"),
            Text("GRACE AI SYSTEM", style="bold magenta"),
            Text(f"🕐 {time_text}", style="dim")
        )
        
        return Panel(header, style="bold blue")
    
    def _render_nav(self) -> Panel:
        """Render navigation menu"""
        
        nav_table = Table(show_header=False, box=None)
        nav_table.add_column("Item", style="cyan")
        
        nav_items = [
            "💬 Chat",
            "💻 IDE",
            "📚 Knowledge",
            "🛡️ Hunter",
            "⚖️ Governance",
            "📋 Tasks",
            "🔍 Verification",
            "🎤 Voice"
        ]
        
        for item in nav_items:
            nav_table.add_row(item)
        
        return Panel(nav_table, title="[bold]Navigation[/bold]", border_style="green")
    
    def _render_tasks(self) -> Panel:
        """Render tasks panel"""
        
        if not self.tasks:
            content = Text("No active tasks", style="dim")
        else:
            task_table = Table(show_header=False, box=None)
            task_table.add_column("Task", style="yellow")
            
            for task in self.tasks[:5]:  # Show top 5
                status = "✓" if task.get("status") == "completed" else "○"
                task_table.add_row(f"{status} {task.get('title', 'Untitled')[:30]}")
            
            content = task_table
        
        return Panel(content, title="[bold]Tasks[/bold]", border_style="yellow")
    
    def _render_chat(self) -> Panel:
        """Render chat history"""
        
        if not self.chat_history:
            content = Text("Start chatting with Grace...", style="dim italic")
        else:
            chat_text = Text()
            for msg in self.chat_history[-10:]:  # Last 10 messages
                role = msg.get("role", "user")
                text = msg.get("content", "")
                timestamp = msg.get("timestamp", "")
                
                if role == "user":
                    chat_text.append(f"\n[{timestamp}] You: ", style="bold cyan")
                else:
                    chat_text.append(f"\n[{timestamp}] Grace: ", style="bold magenta")
                
                chat_text.append(f"{text}\n")
            
            content = chat_text
        
        return Panel(content, title="[bold]Chat[/bold]", border_style="cyan", padding=(1, 2))
    
    def _render_console(self) -> Panel:
        """Render console output"""
        
        console_text = Text()
        console_text.append("Console output will appear here...\n", style="dim")
        console_text.append("Ready for commands.\n", style="green")
        
        return Panel(console_text, title="[bold]Console[/bold]", border_style="blue")
    
    def _render_footer(self) -> Panel:
        """Render footer with help text"""
        
        footer = Table.grid(padding=1)
        footer.add_column(justify="left")
        
        help_text = (
            "[bold cyan]Commands:[/bold cyan] "
            "/chat [dim]|[/dim] /ide [dim]|[/dim] /tasks [dim]|[/dim] /voice [dim]|[/dim] "
            "/help [dim]|[/dim] /quit    "
            "[dim]Ctrl+P: Command Palette[/dim]"
        )
        
        footer.add_row(Text.from_markup(help_text))
        
        return Panel(footer, style="dim")
    
    def render(self):
        """Render the entire UI"""
        
        self.layout["header"].update(self._render_header())
        self.layout["nav"].update(self._render_nav())
        self.layout["tasks"].update(self._render_tasks())
        self.layout["chat"].update(self._render_chat())
        self.layout["console"].update(self._render_console())
        self.layout["footer"].update(self._render_footer())
        
        return self.layout
    
    async def start(self):
        """Start the CLI application"""
        
        console.print("[bold green]Grace CLI started![/bold green]\n")
        console.print("Type [bold cyan]/help[/bold cyan] for commands or [bold cyan]/quit[/bold cyan] to exit.\n")
        
        # Create prompt session
        self.session = PromptSession()
        
        # Main loop
        try:
            while True:
                # Render UI
                console.clear()
                console.print(self.render())
                
                # Get user input
                try:
                    user_input = await self.session.prompt_async(
                        HTML('<ansicyan><b>grace></b></ansicyan> ')
                    )
                    
                    if not user_input:
                        continue
                    
                    # Process command
                    await self.process_command(user_input)
                    
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use /quit to exit[/yellow]")
                except EOFError:
                    break
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        finally:
            console.print("\n[bold green]Goodbye! Grace CLI shutting down...[/bold green]")
    
    async def process_command(self, command: str):
        """Process user command"""
        
        if command.startswith("/"):
            # CLI command
            await self.handle_cli_command(command)
        else:
            # Chat message
            await self.handle_chat_message(command)
    
    async def handle_cli_command(self, command: str):
        """Handle CLI commands like /help, /tasks, etc."""
        
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "/help":
            await self.show_help()
        elif cmd == "/quit" or cmd == "/exit":
            raise EOFError
        elif cmd == "/chat":
            console.print("[green]Already in chat mode[/green]")
        elif cmd == "/tasks":
            await self.show_tasks()
        elif cmd == "/ide":
            await self.open_ide()
        elif cmd == "/voice":
            await self.start_voice_session()
        elif cmd == "/knowledge":
            await self.ingest_knowledge(args)
        elif cmd == "/hunter":
            await self.show_hunter_alerts()
        elif cmd == "/governance":
            await self.show_governance_requests()
        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            console.print("[dim]Type /help for available commands[/dim]")
    
    async def handle_chat_message(self, message: str):
        """Handle chat message to Grace"""
        
        timestamp = datetime.now().strftime("%H:%M")
        
        # Add to history
        self.chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": timestamp
        })
        
        # TODO: Send to backend and get response
        # For now, mock response
        await asyncio.sleep(0.5)
        
        response = f"You said: {message}"
        
        self.chat_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": timestamp
        })
    
    async def show_help(self):
        """Show help information"""
        
        help_table = Table(title="Grace CLI Commands", show_header=True)
        help_table.add_column("Command", style="cyan", width=20)
        help_table.add_column("Description", style="white")
        
        commands = [
            ("/chat", "Start chat with Grace"),
            ("/ide", "Open code editor"),
            ("/tasks", "View and manage tasks"),
            ("/voice", "Start voice session"),
            ("/knowledge <url>", "Ingest knowledge from URL"),
            ("/hunter", "View security alerts"),
            ("/governance", "View approval requests"),
            ("/help", "Show this help"),
            ("/quit", "Exit Grace CLI"),
        ]
        
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
        
        console.print(help_table)
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    async def show_tasks(self):
        """Show tasks view"""
        console.print("[yellow]Tasks feature coming soon...[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    async def open_ide(self):
        """Open IDE view"""
        console.print("[yellow]IDE feature coming soon...[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    async def start_voice_session(self):
        """Start voice session"""
        console.print("[yellow]Voice feature coming soon...[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    async def ingest_knowledge(self, url: str):
        """Ingest knowledge from URL"""
        if not url:
            console.print("[red]Please provide a URL[/red]")
        else:
            console.print(f"[yellow]Ingesting knowledge from: {url}[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    async def show_hunter_alerts(self):
        """Show Hunter security alerts"""
        console.print("[yellow]Hunter alerts feature coming soon...[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    async def show_governance_requests(self):
        """Show governance approval requests"""
        console.print("[yellow]Governance feature coming soon...[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")


async def main():
    """Main entry point"""
    cli = GraceCLI()
    await cli.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        sys.exit(1)
