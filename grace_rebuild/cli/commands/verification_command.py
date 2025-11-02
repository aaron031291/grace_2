"""
Verification command - Audit log viewer
"""

import asyncio
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from ..grace_client import GraceAPIClient


class VerificationCommand:
    """Verification and audit log management"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
    
    async def execute(self, action: Optional[str] = None, *args):
        """Execute verification command"""
        if not self.client.is_authenticated():
            self.console.print("[red]Please login first[/red]")
            return
        
        if action == "audit":
            await self.show_audit_log()
        elif action == "stats":
            await self.show_statistics()
        elif action == "failed":
            await self.show_failed_verifications()
        else:
            await self.interactive_menu()
    
    async def show_audit_log(self, limit: int = 50, hours_back: int = 24):
        """Show verification audit log"""
        with self.console.status("Loading audit log...", spinner="dots"):
            response = await self.client.get_audit_log(
                limit=limit,
                hours_back=hours_back
            )
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        audit_log = response.data.get("audit_log", [])
        
        if not audit_log:
            self.console.print("[dim]No audit log entries found[/dim]")
            return
        
        table = Table(
            title=f"Verification Audit Log (Last {hours_back}h)",
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Time", style="dim", width=16)
        table.add_column("Actor", style="cyan", width=15)
        table.add_column("Action", style="yellow", width=20)
        table.add_column("Status", style="white", width=10)
        table.add_column("Details", style="white", width=50)
        
        for entry in audit_log:
            status = entry.get("status", "unknown")
            status_emoji = {
                "success": "✓",
                "failed": "✗",
                "pending": "⏳"
            }.get(status, "○")
            
            status_style = {
                "success": "green",
                "failed": "red",
                "pending": "yellow"
            }.get(status, "white")
            
            table.add_row(
                entry.get("timestamp", "")[:16] if entry.get("timestamp") else "",
                entry.get("actor", "Unknown"),
                entry.get("action_type", "Unknown"),
                f"[{status_style}]{status_emoji} {status}[/{status_style}]",
                entry.get("details", "No details")[:50]
            )
        
        self.console.print(table)
    
    async def show_statistics(self, hours_back: int = 24):
        """Show verification statistics"""
        with self.console.status("Loading statistics...", spinner="dots"):
            response = await self.client.get_verification_stats(hours_back=hours_back)
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        stats = response.data
        
        # Create stat panels
        panels = []
        
        # Total verifications
        total = stats.get("total_verifications", 0)
        success = stats.get("successful_verifications", 0)
        failed = stats.get("failed_verifications", 0)
        success_rate = (success / total * 100) if total > 0 else 0
        
        total_text = f"[bold]{total}[/bold]\n"
        total_text += f"[green]✓ {success} success[/green]\n"
        total_text += f"[red]✗ {failed} failed[/red]\n"
        total_text += f"[dim]Success rate: {success_rate:.1f}%[/dim]"
        
        panels.append(Panel(
            total_text,
            title="[bold]Total Verifications[/bold]",
            border_style="cyan"
        ))
        
        # By action type
        by_action = stats.get("by_action_type", {})
        if by_action:
            action_text = ""
            for action, count in sorted(by_action.items(), key=lambda x: x[1], reverse=True)[:5]:
                action_text += f"{action}: [bold]{count}[/bold]\n"
            
            panels.append(Panel(
                action_text.strip(),
                title="[bold]Top Actions[/bold]",
                border_style="yellow"
            ))
        
        # By actor
        by_actor = stats.get("by_actor", {})
        if by_actor:
            actor_text = ""
            for actor, count in sorted(by_actor.items(), key=lambda x: x[1], reverse=True)[:5]:
                actor_text += f"{actor}: [bold]{count}[/bold]\n"
            
            panels.append(Panel(
                actor_text.strip(),
                title="[bold]Top Actors[/bold]",
                border_style="blue"
            ))
        
        self.console.print(Columns(panels, equal=True, expand=True))
    
    async def show_failed_verifications(self, limit: int = 50, hours_back: int = 24):
        """Show failed verifications"""
        with self.console.status("Loading failed verifications...", spinner="dots"):
            response = await self.client.get_failed_verifications(
                limit=limit,
                hours_back=hours_back
            )
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        failures = response.data.get("failed_verifications", [])
        
        if not failures:
            self.console.print("[green]✓ No failed verifications[/green]")
            return
        
        table = Table(
            title=f"Failed Verifications (Last {hours_back}h)",
            show_header=True,
            header_style="bold red"
        )
        table.add_column("Time", style="dim", width=16)
        table.add_column("Actor", style="cyan", width=15)
        table.add_column("Action", style="yellow", width=20)
        table.add_column("Reason", style="red", width=50)
        
        for failure in failures:
            table.add_row(
                failure.get("timestamp", "")[:16] if failure.get("timestamp") else "",
                failure.get("actor", "Unknown"),
                failure.get("action_type", "Unknown"),
                failure.get("failure_reason", "No reason provided")[:50]
            )
        
        self.console.print(table)
    
    async def interactive_menu(self):
        """Interactive verification menu"""
        while True:
            self.console.clear()
            
            # Show quick stats
            with self.console.status("Loading statistics...", spinner="dots"):
                stats_response = await self.client.get_verification_stats(hours_back=24)
            
            if stats_response.success:
                stats = stats_response.data
                total = stats.get("total_verifications", 0)
                success = stats.get("successful_verifications", 0)
                failed = stats.get("failed_verifications", 0)
                
                self.console.print(f"[bold cyan]Last 24 hours:[/bold cyan] {total} verifications")
                self.console.print(f"[green]✓ {success} success[/green]  [red]✗ {failed} failed[/red]\n")
            
            self.console.print("[bold cyan]Verification System[/bold cyan]\n")
            self.console.print("1. View audit log")
            self.console.print("2. View statistics")
            self.console.print("3. View failed verifications")
            self.console.print("4. Custom time range")
            self.console.print("0. Back to main menu")
            
            choice = await asyncio.to_thread(self.console.input, "\nChoice: ")
            
            if choice == "1":
                await self.show_audit_log()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "2":
                await self.show_statistics()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "3":
                await self.show_failed_verifications()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "4":
                hours = await asyncio.to_thread(
                    self.console.input,
                    "Hours back (default: 24): "
                )
                hours_back = int(hours) if hours.isdigit() else 24
                await self.show_audit_log(hours_back=hours_back)
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "0":
                break
