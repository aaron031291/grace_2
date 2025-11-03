#!/usr/bin/env python3
"""
Real-time Cognition Status Display
Shows Grace's cognitive state across all 10 domains with live metrics
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich import box
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import httpx

console = Console()

DOMAINS = {
    "core": {
        "name": "Platform Core",
        "icon": "💓",
        "endpoints": ["heartbeat", "governance", "self_healing"],
        "kpis": ["uptime", "governance_score", "healing_actions"]
    },
    "transcendence": {
        "name": "Agentic Dev",
        "icon": "🧠",
        "endpoints": ["task_planner", "code_gen", "memory"],
        "kpis": ["task_success", "code_quality", "memory_recall"]
    },
    "knowledge": {
        "name": "Knowledge & BI",
        "icon": "📚",
        "endpoints": ["ingestion", "trust_scoring", "search"],
        "kpis": ["trust_score", "ingestion_rate", "recall_accuracy"]
    },
    "security": {
        "name": "Hunter Security",
        "icon": "🛡️",
        "endpoints": ["hunter", "scans", "quarantine"],
        "kpis": ["threats_detected", "scan_coverage", "response_time"]
    },
    "ml": {
        "name": "ML Platform",
        "icon": "🤖",
        "endpoints": ["training", "deployment", "inference"],
        "kpis": ["model_accuracy", "deployment_success", "inference_latency"]
    },
    "temporal": {
        "name": "Causal & Forecasting",
        "icon": "⏰",
        "endpoints": ["causal_graph", "temporal_analysis", "simulation"],
        "kpis": ["prediction_accuracy", "graph_completeness", "sim_quality"]
    },
    "parliament": {
        "name": "Governance & Meta",
        "icon": "🏛️",
        "endpoints": ["voting", "meta_loop", "compliance"],
        "kpis": ["vote_participation", "recommendation_adoption", "compliance_score"]
    },
    "federation": {
        "name": "External Integration",
        "icon": "🌐",
        "endpoints": ["connectors", "secrets", "api_gateway"],
        "kpis": ["connector_health", "api_success", "secret_rotation"]
    }
}


class CognitionMonitor:
    """Monitor Grace's real-time cognition across all domains"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.metrics: Dict[str, Any] = {}
        self.overall_health = 0.0
        self.overall_trust = 0.0
        self.overall_confidence = 0.0
        self.saas_ready = False
        
    async def fetch_metrics(self):
        """Fetch latest metrics from all domains"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.backend_url}/api/cognition/status", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    self.metrics = data.get("domains", {})
                    self.overall_health = data.get("overall_health", 0.0)
                    self.overall_trust = data.get("overall_trust", 0.0)
                    self.overall_confidence = data.get("overall_confidence", 0.0)
                    self.saas_ready = data.get("saas_ready", False)
            except Exception as e:
                console.print(f"[red]Error fetching metrics: {e}[/red]")
    
    def render_overall_status(self) -> Panel:
        """Render overall Grace cognition status"""
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Metric", style="bold cyan")
        table.add_column("Value", style="bold")
        table.add_column("Bar", style="")
        
        def get_color(value: float) -> str:
            if value >= 0.9: return "green"
            if value >= 0.7: return "yellow"
            return "red"
        
        def render_bar(value: float, width: int = 20) -> str:
            filled = int(value * width)
            bar = "█" * filled + "░" * (width - filled)
            color = get_color(value)
            return f"[{color}]{bar}[/{color}]"
        
        table.add_row(
            "Health",
            f"{self.overall_health:.1%}",
            render_bar(self.overall_health)
        )
        table.add_row(
            "Trust",
            f"{self.overall_trust:.1%}",
            render_bar(self.overall_trust)
        )
        table.add_row(
            "Confidence",
            f"{self.overall_confidence:.1%}",
            render_bar(self.overall_confidence)
        )
        
        status_text = "🚀 [bold green]SaaS Ready[/bold green]" if self.saas_ready else "🔧 [yellow]Development Mode[/yellow]"
        table.add_row("Status", status_text, "")
        
        title = "Grace Overall Cognition"
        if self.saas_ready:
            title += " [bold green]● READY FOR COMMERCIALIZATION[/bold green]"
        
        return Panel(table, title=title, border_style="magenta")
    
    def render_domain_grid(self) -> Layout:
        """Render grid of all 10 domains with their metrics"""
        
        layout = Layout()
        
        rows = []
        row = []
        
        for domain_id, domain_info in DOMAINS.items():
            metrics = self.metrics.get(domain_id, {})
            
            table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
            table.add_column("", style="dim")
            table.add_column("", justify="right")
            
            kpis = domain_info.get("kpis", [])
            for kpi in kpis[:3]:
                value = metrics.get(kpi, 0.0)
                if isinstance(value, float) and value <= 1.0:
                    display = f"{value:.1%}"
                else:
                    display = str(value)
                table.add_row(kpi[:15], display)
            
            health = metrics.get("health", 0.0)
            color = "green" if health >= 0.9 else "yellow" if health >= 0.7 else "red"
            
            panel = Panel(
                table,
                title=f"{domain_info['icon']} {domain_info['name']}",
                border_style=color,
                subtitle=f"[{color}]{health:.0%}[/{color}]"
            )
            
            row.append(panel)
            
            if len(row) == 2:
                rows.append(row)
                row = []
        
        if row:
            rows.append(row)
        
        layout.split_column(*[Layout(name=f"row_{i}") for i in range(len(rows))])
        
        for i, row_panels in enumerate(rows):
            layout[f"row_{i}"].split_row(*[Layout(renderable=p) for p in row_panels])
        
        return layout
    
    def render_notifications(self) -> Panel:
        """Render system notifications and alerts"""
        
        notifications = []
        
        if self.overall_health >= 0.9 and self.overall_trust >= 0.9 and self.overall_confidence >= 0.9:
            notifications.append("🎉 [bold green]All systems operational at 90%+ - Ready for SaaS elevation![/bold green]")
        
        for domain_id, metrics in self.metrics.items():
            if metrics.get("health", 0) < 0.5:
                domain_name = DOMAINS.get(domain_id, {}).get("name", domain_id)
                notifications.append(f"⚠️  [yellow]{domain_name} needs attention[/yellow]")
        
        if not notifications:
            notifications.append("[dim]No alerts[/dim]")
        
        text = "\n".join(notifications)
        return Panel(text, title="Notifications", border_style="blue")
    
    async def live_display(self, refresh_rate: float = 2.0):
        """Display live cognition monitor"""
        
        def generate_display():
            main_layout = Layout()
            main_layout.split_column(
                Layout(self.render_overall_status(), size=8),
                Layout(self.render_domain_grid(), name="domains"),
                Layout(self.render_notifications(), size=5)
            )
            return main_layout
        
        with Live(generate_display(), refresh_per_second=1, console=console) as live:
            try:
                while True:
                    await self.fetch_metrics()
                    live.update(generate_display())
                    await asyncio.sleep(refresh_rate)
            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped[/yellow]")


async def show_cognition_status(backend_url: str = "http://localhost:8000"):
    """Entry point for cognition status display"""
    monitor = CognitionMonitor(backend_url)
    await monitor.live_display()


def main():
    """CLI entry point"""
    import sys
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    asyncio.run(show_cognition_status(backend_url))


if __name__ == "__main__":
    main()
