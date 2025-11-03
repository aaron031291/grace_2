#!/usr/bin/env python3
"""
Enhanced Grace CLI - Full-featured terminal interface with backend integration
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from grace_client import GraceAPIClient
from config import get_config, ConfigManager
from plugin_manager import PluginManager

from commands import (
    ChatCommand,
    IDECommand,
    TasksCommand,
    VoiceCommand,
    KnowledgeCommand,
    HunterCommand,
    GovernanceCommand,
    VerificationCommand,
)

console = Console()


class EnhancedGraceCLI:
    """Enhanced Grace CLI with full backend integration"""
    
    def __init__(self):
        self.config_manager = get_config()
        self.config = self.config_manager.load()
        
        self.client = GraceAPIClient(base_url=self.config.backend_url)
        self.plugin_manager: Optional[PluginManager] = None
        
        # Commands
        self.commands = {}
        self._init_commands()
        
        # State
        self.running = True
    
    def _init_commands(self):
        """Initialize command handlers"""
        self.commands = {
            'chat': ChatCommand(self.client, console),
            'ide': IDECommand(self.client, console),
            'tasks': TasksCommand(self.client, console),
            'voice': VoiceCommand(self.client, console),
            'knowledge': KnowledgeCommand(self.client, console),
            'hunter': HunterCommand(self.client, console),
            'governance': GovernanceCommand(self.client, console),
            'verification': VerificationCommand(self.client, console),
        }
    
    async def start(self):
        """Start the CLI application"""
        console.clear()
        self.show_banner()
        
        # Connect to backend
        await self.client.connect()
        
        # Check health
        health = await self.client.health_check()
        if not health.success:
            console.print(f"[red]⚠ Backend not available: {self.config.backend_url}[/red]")
            console.print("[yellow]Make sure Grace backend is running[/yellow]")
            
            if not Confirm.ask("Continue anyway?"):
                return
        else:
            console.print(f"[green]✓ Connected to Grace backend[/green]")
        
        # Auto-login if configured
        if self.config.auto_login:
            await self.auto_login()
        else:
            await self.login_or_register()
        
        # Load plugins
        if self.config.plugins_enabled:
            await self.load_plugins()
        
        # Main loop
        await self.main_loop()
        
        # Cleanup
        await self.client.disconnect()
    
    def show_banner(self):
        """Show welcome banner"""
        banner = """
        ╔═══════════════════════════════════════╗
        ║                                       ║
        ║     GRACE AI - Terminal Interface    ║
        ║                                       ║
        ║     Governance • Reflection          ║
        ║     Autonomy • Cognition • Ethics    ║
        ║                                       ║
        ╚═══════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold cyan"))
    
    async def auto_login(self):
        """Attempt auto-login with saved credentials"""
        session = self.config_manager.restore_session()
        
        if session:
            self.client.token = session['token']
            self.client.username = session['username']
            
            # Verify token still valid
            health = await self.client.health_check()
            if health.success:
                console.print(f"[green]✓ Logged in as {session['username']}[/green]\n")
                return
        
        # Fallback to manual login
        await self.login_or_register()
    
    async def login_or_register(self):
        """Login or register user"""
        console.print("\n[bold]Authentication Required[/bold]\n")
        
        choice = Prompt.ask(
            "Choose action",
            choices=["login", "register", "skip"],
            default="login"
        )
        
        if choice == "skip":
            console.print("[yellow]Continuing without authentication (limited features)[/yellow]")
            return
        
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)
        
        if choice == "register":
            response = await self.client.register(username, password)
            if response.success:
                console.print("[green]✓ Registration successful[/green]")
                self.config_manager.save_session(username, self.client.token)
            else:
                console.print(f"[red]Registration failed: {response.error}[/red]")
                await asyncio.sleep(2)
        else:
            response = await self.client.login(username, password)
            if response.success:
                console.print("[green]✓ Login successful[/green]")
                self.config_manager.save_session(username, self.client.token)
            else:
                console.print(f"[red]Login failed: {response.error}[/red]")
                await asyncio.sleep(2)
        
        console.print()
    
    async def load_plugins(self):
        """Load CLI plugins"""
        plugin_dir = self.config_manager.get_plugin_dir()
        self.plugin_manager = PluginManager(plugin_dir, console, self.client)
        
        await self.plugin_manager.load_all()
    
    async def main_loop(self):
        """Main command loop"""
        while self.running:
            try:
                await self.show_main_menu()
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'quit' to exit[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                await asyncio.sleep(1)
    
    async def show_main_menu(self):
        """Show main menu"""
        console.clear()
        
        # Header
        user_text = f"👤 {self.client.username}" if self.client.username else "👤 Guest"
        console.print(Panel(
            Text(user_text, style="bold cyan", justify="center"),
            style="cyan"
        ))
        
        # Menu options
        console.print("\n[bold magenta]Grace AI - Main Menu[/bold magenta]\n")
        
        menu_items = [
            ("chat", "💬 Chat with Grace"),
            ("tasks", "📋 Task Management"),
            ("knowledge", "📚 Knowledge Base"),
            ("hunter", "🛡️ Security Alerts"),
            ("governance", "⚖️ Governance"),
            ("verification", "🔍 Verification Logs"),
            ("ide", "💻 File Explorer"),
            ("voice", "🎤 Voice Interface"),
            ("plugins", "🔌 Plugins"),
            ("settings", "⚙️ Settings"),
            ("help", "❓ Help"),
            ("quit", "🚪 Exit"),
        ]
        
        for i, (cmd, desc) in enumerate(menu_items, 1):
            console.print(f"{i:2}. {desc}")
        
        console.print()
        choice = await asyncio.to_thread(console.input, "[bold cyan]Choice:[/bold cyan] ")
        
        # Map number to command
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(menu_items):
                choice = menu_items[idx][0]
        
        await self.handle_command(choice)
    
    async def handle_command(self, command: str):
        """Handle user command"""
        command = command.strip().lower()
        
        if not command:
            return
        
        # Special commands
        if command in ['quit', 'exit', 'q']:
            self.running = False
            console.print("\n[bold green]Goodbye! Grace CLI shutting down...[/bold green]")
            return
        
        if command == 'help':
            await self.show_help()
            return
        
        if command == 'settings':
            await self.show_settings()
            return
        
        if command == 'plugins':
            await self.manage_plugins()
            return
        
        # Check if plugin can handle command
        if self.plugin_manager:
            parts = command.split(maxsplit=1)
            cmd = parts[0]
            args = parts[1].split() if len(parts) > 1 else []
            
            if await self.plugin_manager.handle_command(cmd, args):
                return
        
        # Built-in commands
        if command in self.commands:
            try:
                await self.commands[command].execute()
            except Exception as e:
                console.print(f"[red]Command error: {e}[/red]")
                await asyncio.to_thread(console.input, "\nPress Enter to continue...")
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            await asyncio.sleep(1)
    
    async def show_help(self):
        """Show help information"""
        console.clear()
        
        help_table = Table(title="Grace CLI - Command Reference", show_header=True)
        help_table.add_column("Command", style="cyan", width=20)
        help_table.add_column("Description", style="white")
        
        commands = [
            ("chat", "Interactive chat with Grace AI"),
            ("tasks", "Manage tasks (create, list, complete)"),
            ("knowledge", "Ingest and search knowledge base"),
            ("hunter", "View security alerts dashboard"),
            ("governance", "Manage approval requests"),
            ("verification", "View audit logs and statistics"),
            ("ide", "Browse files and view code"),
            ("voice", "Record audio and text-to-speech"),
            ("plugins", "Manage CLI plugins"),
            ("settings", "Configure CLI settings"),
            ("help", "Show this help message"),
            ("quit", "Exit Grace CLI"),
        ]
        
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
        
        console.print(help_table)
        
        console.print("\n[dim]For detailed command help, type the command name[/dim]")
        await asyncio.to_thread(console.input, "\nPress Enter to continue...")
    
    async def show_settings(self):
        """Show and modify settings"""
        console.clear()
        
        while True:
            console.print("[bold]Settings[/bold]\n")
            
            settings_table = Table(show_header=True)
            settings_table.add_column("Setting", style="cyan")
            settings_table.add_column("Value", style="white")
            
            settings_table.add_row("Backend URL", self.config.backend_url)
            settings_table.add_row("Theme", self.config.theme)
            settings_table.add_row("Auto Login", "✓" if self.config.auto_login else "✗")
            settings_table.add_row("WebSocket", "✓" if self.config.websocket_enabled else "✗")
            settings_table.add_row("Plugins", "✓" if self.config.plugins_enabled else "✗")
            
            console.print(settings_table)
            
            console.print("\n1. Change backend URL")
            console.print("2. Toggle auto-login")
            console.print("3. Toggle WebSocket")
            console.print("4. Toggle plugins")
            console.print("0. Back")
            
            choice = await asyncio.to_thread(console.input, "\nChoice: ")
            
            if choice == "1":
                new_url = await asyncio.to_thread(
                    Prompt.ask,
                    "Backend URL",
                    default=self.config.backend_url
                )
                self.config_manager.update(backend_url=new_url)
                self.config = self.config_manager.load()
            elif choice == "2":
                self.config_manager.update(auto_login=not self.config.auto_login)
                self.config = self.config_manager.load()
            elif choice == "3":
                self.config_manager.update(websocket_enabled=not self.config.websocket_enabled)
                self.config = self.config_manager.load()
            elif choice == "4":
                self.config_manager.update(plugins_enabled=not self.config.plugins_enabled)
                self.config = self.config_manager.load()
            elif choice == "0":
                break
            
            console.clear()
    
    async def manage_plugins(self):
        """Manage plugins"""
        if not self.plugin_manager:
            console.print("[yellow]Plugins are disabled[/yellow]")
            await asyncio.sleep(1)
            return
        
        console.clear()
        
        plugins = self.plugin_manager.list_plugins()
        
        console.print("[bold]Loaded Plugins[/bold]\n")
        
        if plugins:
            plugin_table = Table(show_header=True)
            plugin_table.add_column("Name", style="cyan")
            plugin_table.add_column("Version", style="white")
            plugin_table.add_column("Author", style="blue")
            plugin_table.add_column("Description", style="dim")
            
            for plugin in plugins:
                plugin_table.add_row(
                    plugin.name,
                    plugin.version,
                    plugin.author,
                    plugin.description
                )
            
            console.print(plugin_table)
        else:
            console.print("[dim]No plugins loaded[/dim]")
        
        await asyncio.to_thread(console.input, "\nPress Enter to continue...")


async def main():
    """Main entry point"""
    cli = EnhancedGraceCLI()
    await cli.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        sys.exit(1)
