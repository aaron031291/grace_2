"""
Governance command - Approval workflow management
"""

import asyncio
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from ..grace_client import GraceAPIClient


class GovernanceCommand:
    """Governance and approval management"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
    
    async def execute(self, action: Optional[str] = None, *args):
        """Execute governance command"""
        if not self.client.is_authenticated():
            self.console.print("[red]Please login first[/red]")
            return
        
        if action == "list":
            status = args[0] if args else None
            await self.list_requests(status)
        elif action == "approve":
            request_id = int(args[0]) if args else None
            if request_id:
                await self.approve_request(request_id)
        elif action == "reject":
            request_id = int(args[0]) if args else None
            if request_id:
                await self.reject_request(request_id)
        else:
            await self.interactive_menu()
    
    async def list_requests(self, status: Optional[str] = None):
        """List approval requests"""
        with self.console.status("Loading requests...", spinner="dots"):
            response = await self.client.get_approval_requests(status=status)
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        requests = response.data.get("requests", [])
        
        if not requests:
            self.console.print("[dim]No approval requests found[/dim]")
            return
        
        table = Table(
            title="Governance Requests",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Type", style="white", width=20)
        table.add_column("Requester", style="blue", width=15)
        table.add_column("Description", style="white", width=40)
        table.add_column("Created", style="dim", width=16)
        
        for req in requests:
            status_emoji = {
                "pending": "⏳",
                "approved": "✅",
                "rejected": "❌",
                "expired": "⏰"
            }.get(req.get("status", "pending"), "○")
            
            status_style = {
                "pending": "yellow",
                "approved": "green",
                "rejected": "red",
                "expired": "dim"
            }.get(req.get("status", "pending"), "white")
            
            table.add_row(
                str(req.get("id")),
                f"{status_emoji} [{status_style}]{req.get('status', 'pending')}[/{status_style}]",
                req.get("request_type", "Unknown"),
                req.get("requester", "Unknown"),
                req.get("description", "No description")[:40],
                req.get("created_at", "")[:16] if req.get("created_at") else ""
            )
        
        self.console.print(table)
    
    async def approve_request(self, request_id: int, comment: Optional[str] = None):
        """Approve a request"""
        if comment is None:
            comment = await asyncio.to_thread(
                Prompt.ask,
                "Approval comment (optional)",
                default=""
            )
        
        confirm = await asyncio.to_thread(
            Confirm.ask,
            f"Approve request #{request_id}?"
        )
        
        if not confirm:
            self.console.print("[yellow]Cancelled[/yellow]")
            return
        
        with self.console.status(f"Approving request #{request_id}...", spinner="dots"):
            response = await self.client.approve_request(request_id, comment)
        
        if response.success:
            self.console.print(f"[green]✓ Request #{request_id} approved[/green]")
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def reject_request(self, request_id: int, reason: Optional[str] = None):
        """Reject a request"""
        if reason is None:
            reason = await asyncio.to_thread(
                Prompt.ask,
                "Rejection reason (required)"
            )
        
        if not reason:
            self.console.print("[yellow]Rejection reason required[/yellow]")
            return
        
        confirm = await asyncio.to_thread(
            Confirm.ask,
            f"Reject request #{request_id}?"
        )
        
        if not confirm:
            self.console.print("[yellow]Cancelled[/yellow]")
            return
        
        with self.console.status(f"Rejecting request #{request_id}...", spinner="dots"):
            response = await self.client.reject_request(request_id, reason)
        
        if response.success:
            self.console.print(f"[green]✓ Request #{request_id} rejected[/green]")
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def show_request_details(self, request_id: int):
        """Show detailed request information"""
        # This would fetch detailed request info
        self.console.print(f"[dim]Request details for #{request_id} - Coming soon[/dim]")
    
    async def interactive_menu(self):
        """Interactive governance menu"""
        while True:
            self.console.clear()
            
            # Show pending requests
            with self.console.status("Loading requests...", spinner="dots"):
                response = await self.client.get_approval_requests(status="pending")
            
            if response.success:
                pending = response.data.get("requests", [])
                pending_count = len(pending)
                
                if pending_count > 0:
                    self.console.print(f"[bold yellow]⚠ {pending_count} pending approval(s)[/bold yellow]\n")
                    
                    # Show first 5 pending requests
                    for req in pending[:5]:
                        self.console.print(
                            f"  [{req.get('id')}] {req.get('request_type', 'Unknown')}: "
                            f"{req.get('description', 'No description')[:50]}"
                        )
                    self.console.print()
                else:
                    self.console.print("[green]✓ No pending approvals[/green]\n")
            
            self.console.print("[bold magenta]Governance Management[/bold magenta]\n")
            self.console.print("1. List all requests")
            self.console.print("2. List pending requests")
            self.console.print("3. Approve request")
            self.console.print("4. Reject request")
            self.console.print("5. Refresh")
            self.console.print("0. Back to main menu")
            
            choice = await asyncio.to_thread(self.console.input, "\nChoice: ")
            
            if choice == "1":
                await self.list_requests()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "2":
                await self.list_requests(status="pending")
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "3":
                request_id = await asyncio.to_thread(self.console.input, "Request ID: ")
                if request_id.isdigit():
                    await self.approve_request(int(request_id))
                    await asyncio.sleep(1)
            elif choice == "4":
                request_id = await asyncio.to_thread(self.console.input, "Request ID: ")
                if request_id.isdigit():
                    await self.reject_request(int(request_id))
                    await asyncio.sleep(1)
            elif choice == "5":
                continue
            elif choice == "0":
                break
