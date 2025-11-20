"""
Knowledge command - URL ingestion with trust scoring
"""

import asyncio
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..grace_client import GraceAPIClient


class KnowledgeCommand:
    """Knowledge base management"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
    
    async def execute(self, action: Optional[str] = None, *args):
        """Execute knowledge command"""
        if not self.client.is_authenticated():
            self.console.print("[red]Please login first[/red]")
            return
        
        if action == "ingest":
            url = args[0] if args else None
            trust_score = float(args[1]) if len(args) > 1 else None
            await self.ingest_url(url, trust_score)
        elif action == "search":
            query = " ".join(args) if args else None
            await self.search_knowledge(query)
        elif action == "list":
            await self.list_knowledge()
        else:
            await self.interactive_menu()
    
    async def ingest_url(self, url: Optional[str] = None, trust_score: Optional[float] = None):
        """Ingest knowledge from URL"""
        if not url:
            url = await asyncio.to_thread(Prompt.ask, "URL to ingest")
        
        if not url:
            self.console.print("[yellow]Cancelled[/yellow]")
            return
        
        if trust_score is None:
            trust_input = await asyncio.to_thread(
                Prompt.ask,
                "Trust score (0.0-1.0, or press Enter to auto-calculate)",
                default=""
            )
            if trust_input:
                try:
                    trust_score = float(trust_input)
                    if not 0 <= trust_score <= 1:
                        self.console.print("[red]Trust score must be between 0.0 and 1.0[/red]")
                        return
                except ValueError:
                    self.console.print("[red]Invalid trust score[/red]")
                    return
        
        self.console.print(f"\n[cyan]Ingesting:[/cyan] {url}")
        if trust_score is not None:
            self.console.print(f"[cyan]Trust score:[/cyan] {trust_score:.2f}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Downloading and processing...", total=None)
            
            response = await self.client.ingest_url(url, trust_score)
            
            progress.update(task, completed=True)
        
        if response.success:
            data = response.data
            self.console.print("\n[green]✓ Successfully ingested knowledge[/green]")
            
            # Show details
            details = Table(show_header=False, box=None)
            details.add_column("Key", style="cyan")
            details.add_column("Value", style="white")
            
            if "knowledge_item" in data:
                item = data["knowledge_item"]
                details.add_row("ID", str(item.get("id", "N/A")))
                details.add_row("Title", item.get("title", "N/A"))
                details.add_row("Trust Score", f"{item.get('trust_score', 0):.2f}")
                details.add_row("Content Size", f"{len(item.get('content', ''))} chars")
            
            if "embedding_id" in data:
                details.add_row("Embedding ID", str(data["embedding_id"]))
            
            self.console.print(Panel(details, title="Ingestion Details", border_style="green"))
        else:
            self.console.print(f"[red]✗ Error: {response.error}[/red]")
    
    async def search_knowledge(self, query: Optional[str] = None):
        """Search knowledge base"""
        if not query:
            query = await asyncio.to_thread(Prompt.ask, "Search query")
        
        if not query:
            self.console.print("[yellow]Cancelled[/yellow]")
            return
        
        with self.console.status(f"Searching for: {query}", spinner="dots"):
            response = await self.client.search_knowledge(query, limit=20)
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        results = response.data.get("results", [])
        
        if not results:
            self.console.print("[dim]No results found[/dim]")
            return
        
        self.console.print(f"\n[bold]Search Results:[/bold] {len(results)} items\n")
        
        for i, result in enumerate(results, 1):
            # Trust score indicator
            trust = result.get("trust_score", 0)
            trust_color = "green" if trust >= 0.7 else "yellow" if trust >= 0.4 else "red"
            trust_bar = "█" * int(trust * 10)
            
            self.console.print(f"[bold]{i}. {result.get('title', 'Untitled')}[/bold]")
            self.console.print(f"   [dim]Source:[/dim] {result.get('source', 'Unknown')}")
            self.console.print(f"   [dim]Trust:[/dim] [{trust_color}]{trust_bar}[/{trust_color}] {trust:.2f}")
            
            # Show snippet
            content = result.get("content", "")
            snippet = content[:200] + "..." if len(content) > 200 else content
            self.console.print(f"   {snippet}\n")
    
    async def list_knowledge(self):
        """List all knowledge items"""
        with self.console.status("Loading knowledge items...", spinner="dots"):
            response = await self.client.get_knowledge_items(limit=50)
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        items = response.data.get("items", [])
        
        if not items:
            self.console.print("[dim]No knowledge items found[/dim]")
            return
        
        table = Table(title="Knowledge Base", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Title", style="white", width=40)
        table.add_column("Source", style="blue", width=30)
        table.add_column("Trust", style="green", width=10)
        table.add_column("Created", style="dim", width=16)
        
        for item in items:
            trust = item.get("trust_score", 0)
            trust_display = f"{trust:.2f}"
            
            table.add_row(
                str(item.get("id")),
                item.get("title", "Untitled")[:40],
                item.get("source", "Unknown")[:30],
                trust_display,
                item.get("created_at", "")[:16] if item.get("created_at") else ""
            )
        
        self.console.print(table)
    
    async def interactive_menu(self):
        """Interactive knowledge management menu"""
        while True:
            self.console.clear()
            self.console.print("[bold magenta]Knowledge Management[/bold magenta]\n")
            
            self.console.print("1. Ingest URL")
            self.console.print("2. Search knowledge")
            self.console.print("3. List all items")
            self.console.print("0. Back to main menu")
            
            choice = await asyncio.to_thread(self.console.input, "\nChoice: ")
            
            if choice == "1":
                await self.ingest_url()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "2":
                await self.search_knowledge()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "3":
                await self.list_knowledge()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "0":
                break
