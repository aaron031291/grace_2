"""
Hunter command - Security alerts dashboard
"""

import asyncio
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from ..grace_client import GraceAPIClient


class HunterCommand:
    """Security alerts and monitoring"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
    
    async def execute(self, action: Optional[str] = None, *args):
        """Execute hunter command"""
        if not self.client.is_authenticated():
            self.console.print("[red]Please login first[/red]")
            return
        
        if action == "list":
            severity = args[0] if args else None
            await self.list_alerts(severity)
        elif action == "ack":
            alert_id = int(args[0]) if args else None
            if alert_id:
                await self.acknowledge_alert(alert_id)
        elif action == "dashboard":
            await self.show_dashboard()
        else:
            await self.interactive_dashboard()
    
    async def list_alerts(self, severity: Optional[str] = None):
        """List security alerts"""
        with self.console.status("Loading alerts...", spinner="dots"):
            response = await self.client.get_alerts(severity=severity, limit=50)
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        alerts = response.data.get("alerts", [])
        
        if not alerts:
            self.console.print("[green]✓ No active alerts[/green]")
            return
        
        table = Table(
            title="Security Alerts",
            show_header=True,
            header_style="bold red"
        )
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Severity", style="red", width=12)
        table.add_column("Type", style="yellow", width=20)
        table.add_column("Message", style="white", width=50)
        table.add_column("Time", style="dim", width=16)
        
        for alert in alerts:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
                "info": "🔵"
            }.get(alert.get("severity", "info"), "⚪")
            
            severity_style = {
                "critical": "bold red",
                "high": "red",
                "medium": "yellow",
                "low": "green",
                "info": "blue"
            }.get(alert.get("severity", "info"), "white")
            
            table.add_row(
                str(alert.get("id")),
                f"{severity_emoji} [{severity_style}]{alert.get('severity', 'info')}[/{severity_style}]",
                alert.get("alert_type", "Unknown"),
                alert.get("message", "No message")[:50],
                alert.get("timestamp", "")[:16] if alert.get("timestamp") else ""
            )
        
        self.console.print(table)
    
    async def show_dashboard(self):
        """Show security dashboard with stats"""
        with self.console.status("Loading dashboard...", spinner="dots"):
            alerts_response = await self.client.get_alerts(limit=100)
        
        if not alerts_response.success:
            self.console.print(f"[red]Error: {alerts_response.error}[/red]")
            return
        
        alerts = alerts_response.data.get("alerts", [])
        
        # Calculate statistics
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        type_counts = {}
        recent_alerts = []
        
        for alert in alerts:
            severity = alert.get("severity", "info")
            alert_type = alert.get("alert_type", "unknown")
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            
            if len(recent_alerts) < 5:
                recent_alerts.append(alert)
        
        # Create dashboard panels
        panels = []
        
        # Severity summary
        severity_table = Table(show_header=False, box=None)
        severity_table.add_column("Severity", style="bold")
        severity_table.add_column("Count", justify="right")
        
        severity_table.add_row("🔴 Critical", f"[bold red]{severity_counts['critical']}[/bold red]")
        severity_table.add_row("🟠 High", f"[red]{severity_counts['high']}[/red]")
        severity_table.add_row("🟡 Medium", f"[yellow]{severity_counts['medium']}[/yellow]")
        severity_table.add_row("🟢 Low", f"[green]{severity_counts['low']}[/green]")
        severity_table.add_row("🔵 Info", f"[blue]{severity_counts['info']}[/blue]")
        
        panels.append(Panel(severity_table, title="[bold]By Severity[/bold]", border_style="red"))
        
        # Type summary
        type_table = Table(show_header=False, box=None)
        type_table.add_column("Type", style="bold")
        type_table.add_column("Count", justify="right")
        
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for alert_type, count in sorted_types:
            type_table.add_row(alert_type.replace("_", " ").title(), str(count))
        
        panels.append(Panel(type_table, title="[bold]By Type[/bold]", border_style="yellow"))
        
        # Overall status
        total = len(alerts)
        critical_count = severity_counts['critical'] + severity_counts['high']
        
        if critical_count == 0:
            status_text = "[bold green]✓ System Secure[/bold green]\n"
            status_text += f"[dim]{total} total alerts, no critical issues[/dim]"
            status_style = "green"
        elif critical_count <= 3:
            status_text = "[bold yellow]⚠ Attention Required[/bold yellow]\n"
            status_text += f"[dim]{critical_count} high-priority alerts[/dim]"
            status_style = "yellow"
        else:
            status_text = "[bold red]🚨 Security Alert[/bold red]\n"
            status_text += f"[dim]{critical_count} high-priority alerts[/dim]"
            status_style = "red"
        
        panels.append(Panel(status_text, title="[bold]Status[/bold]", border_style=status_style))
        
        self.console.print(Columns(panels, equal=True, expand=True))
        
        # Recent alerts
        if recent_alerts:
            self.console.print("\n[bold]Recent Alerts:[/bold]")
            for alert in recent_alerts:
                severity = alert.get("severity", "info")
                severity_emoji = {
                    "critical": "🔴", "high": "🟠", "medium": "🟡",
                    "low": "🟢", "info": "🔵"
                }.get(severity, "⚪")
                
                self.console.print(
                    f"{severity_emoji} [{alert.get('id')}] "
                    f"{alert.get('alert_type', 'Unknown')}: {alert.get('message', 'No message')}"
                )
    
    async def acknowledge_alert(self, alert_id: int):
        """Acknowledge an alert"""
        with self.console.status(f"Acknowledging alert #{alert_id}...", spinner="dots"):
            response = await self.client.acknowledge_alert(alert_id)
        
        if response.success:
            self.console.print(f"[green]✓ Alert #{alert_id} acknowledged[/green]")
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def interactive_dashboard(self):
        """Interactive security dashboard"""
        while True:
            self.console.clear()
            await self.show_dashboard()
            
            self.console.print("\n[bold]Security Dashboard[/bold]")
            self.console.print("1. List all alerts")
            self.console.print("2. Filter by severity")
            self.console.print("3. Acknowledge alert")
            self.console.print("4. Refresh")
            self.console.print("0. Back to main menu")
            
            choice = await asyncio.to_thread(self.console.input, "\nChoice: ")
            
            if choice == "1":
                await self.list_alerts()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "2":
                severity = await asyncio.to_thread(
                    self.console.input,
                    "Severity (critical/high/medium/low/info): "
                )
                await self.list_alerts(severity)
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "3":
                alert_id = await asyncio.to_thread(self.console.input, "Alert ID: ")
                if alert_id.isdigit():
                    await self.acknowledge_alert(int(alert_id))
                    await asyncio.sleep(1)
            elif choice == "4":
                continue
            elif choice == "0":
                break
