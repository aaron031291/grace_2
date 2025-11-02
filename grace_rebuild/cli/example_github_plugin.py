"""
Example Plugin: GitHub Integration

This plugin demonstrates how to create a custom Grace CLI plugin.
It adds GitHub-related commands to the CLI.

To install:
1. Copy this file to ~/.grace/plugins/
2. Restart Grace CLI
3. Use 'github' commands
"""

import asyncio
from plugin_manager import Plugin, PluginMetadata


class GitHubPlugin(Plugin):
    """GitHub integration plugin"""
    
    def __init__(self, console, client):
        super().__init__(console, client)
        
        # Plugin metadata
        self.metadata = PluginMetadata(
            name="GitHubIntegration",
            version="1.0.0",
            author="Grace AI Team",
            description="GitHub repository integration",
            commands=["github", "gh"]
        )
        
        # Plugin state
        self.github_token = None
    
    async def on_load(self):
        """Called when plugin is loaded"""
        self.console.print("[green]✓ GitHub plugin loaded[/green]")
        self.console.print("[dim]Commands: github repos, github issues, github status[/dim]")
    
    async def on_unload(self):
        """Called when plugin is unloaded"""
        self.console.print("[yellow]GitHub plugin unloaded[/yellow]")
    
    async def on_command(self, command: str, args: list) -> bool:
        """
        Handle GitHub commands
        
        Returns True if command was handled
        """
        if command not in ["github", "gh"]:
            return False
        
        if not args:
            await self.show_help()
            return True
        
        subcommand = args[0].lower()
        
        if subcommand == "repos":
            await self.list_repositories(args[1] if len(args) > 1 else None)
        elif subcommand == "issues":
            await self.list_issues(args[1] if len(args) > 1 else None)
        elif subcommand == "status":
            await self.show_status()
        elif subcommand == "auth":
            await self.authenticate(args[1] if len(args) > 1 else None)
        else:
            self.console.print(f"[red]Unknown GitHub command: {subcommand}[/red]")
            await self.show_help()
        
        return True
    
    async def on_message(self, role: str, content: str):
        """
        React to chat messages
        
        This could be used to detect GitHub URLs and offer to ingest them
        """
        if "github.com" in content.lower():
            self.console.print("[dim]💡 Tip: Use 'github repos' to view repositories[/dim]")
    
    async def on_event(self, event_type: str, data: dict):
        """React to system events"""
        if event_type == "task_created":
            # Could automatically create GitHub issues from tasks
            pass
    
    # Command implementations
    
    async def show_help(self):
        """Show GitHub plugin help"""
        from rich.table import Table
        
        table = Table(title="GitHub Plugin Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        
        table.add_row("github auth <token>", "Authenticate with GitHub token")
        table.add_row("github repos [user]", "List repositories")
        table.add_row("github issues [repo]", "List issues")
        table.add_row("github status", "Show connection status")
        
        self.console.print(table)
    
    async def authenticate(self, token: str = None):
        """Authenticate with GitHub"""
        if not token:
            token = await asyncio.to_thread(
                self.console.input,
                "GitHub token: "
            )
        
        if token:
            self.github_token = token
            self.console.print("[green]✓ GitHub token saved[/green]")
            self.console.print("[dim]Token is stored in memory only[/dim]")
        else:
            self.console.print("[yellow]Cancelled[/yellow]")
    
    async def list_repositories(self, username: str = None):
        """List GitHub repositories"""
        if not self.github_token:
            self.console.print("[yellow]Please authenticate first: github auth <token>[/yellow]")
            return
        
        username = username or "user"
        
        self.console.print(f"[cyan]Fetching repositories for {username}...[/cyan]")
        
        # Mock data for demonstration
        # In real implementation, use httpx to call GitHub API
        repos = [
            {"name": "grace", "stars": 42, "language": "Python"},
            {"name": "awesome-ai", "stars": 123, "language": "JavaScript"},
            {"name": "ml-toolkit", "stars": 89, "language": "Python"},
        ]
        
        from rich.table import Table
        
        table = Table(title=f"Repositories - {username}")
        table.add_column("Name", style="cyan")
        table.add_column("Stars", style="yellow", justify="right")
        table.add_column("Language", style="green")
        
        for repo in repos:
            table.add_row(
                repo["name"],
                f"⭐ {repo['stars']}",
                repo["language"]
            )
        
        self.console.print(table)
    
    async def list_issues(self, repo: str = None):
        """List GitHub issues"""
        if not self.github_token:
            self.console.print("[yellow]Please authenticate first: github auth <token>[/yellow]")
            return
        
        repo = repo or "grace"
        
        self.console.print(f"[cyan]Fetching issues for {repo}...[/cyan]")
        
        # Mock data
        issues = [
            {"number": 42, "title": "Add feature X", "state": "open"},
            {"number": 43, "title": "Fix bug Y", "state": "open"},
            {"number": 44, "title": "Improve docs", "state": "closed"},
        ]
        
        from rich.table import Table
        
        table = Table(title=f"Issues - {repo}")
        table.add_column("#", style="cyan", width=6)
        table.add_column("Title", style="white")
        table.add_column("State", style="yellow")
        
        for issue in issues:
            state_emoji = "🟢" if issue["state"] == "open" else "🔴"
            table.add_row(
                str(issue["number"]),
                issue["title"],
                f"{state_emoji} {issue['state']}"
            )
        
        self.console.print(table)
    
    async def show_status(self):
        """Show GitHub connection status"""
        from rich.panel import Panel
        
        if self.github_token:
            status = "[green]✓ Connected[/green]\n"
            status += f"[dim]Token: {self.github_token[:10]}...[/dim]"
        else:
            status = "[yellow]⚠ Not authenticated[/yellow]\n"
            status += "[dim]Use: github auth <token>[/dim]"
        
        self.console.print(Panel(status, title="GitHub Status", border_style="cyan"))


# Note: This file should be copied to ~/.grace/plugins/ to be loaded by the CLI
