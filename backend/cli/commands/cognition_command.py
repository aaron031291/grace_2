"""
Cognition CLI Commands
Live dashboard and metrics inspection for Grace's cognitive health
"""

import asyncio
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
API_BASE = "http://localhost:8000"


async def status_command():
    """Display current cognition status across all domains"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/api/cognition/status")
            response.raise_for_status()
            data = response.json()
            
            console.print("\n[bold cyan]Grace Cognition Status[/bold cyan]")
            console.print(f"Timestamp: {data['timestamp']}\n")
            
            # Overall metrics
            overall_table = Table(title="Overall Metrics", show_header=True)
            overall_table.add_column("Metric", style="cyan")
            overall_table.add_column("Value", style="green")
            
            overall_table.add_row("Health", f"{data['overall_health']:.1%}")
            overall_table.add_row("Trust", f"{data['overall_trust']:.1%}")
            overall_table.add_row("Confidence", f"{data['overall_confidence']:.1%}")
            overall_table.add_row("SaaS Ready", "✅ Yes" if data['saas_ready'] else "🔧 Building")
            
            console.print(overall_table)
            console.print()
            
            # Domain metrics
            domain_table = Table(title="Domain Performance", show_header=True)
            domain_table.add_column("Domain", style="cyan")
            domain_table.add_column("Health", style="green")
            domain_table.add_column("Trust", style="yellow")
            domain_table.add_column("Confidence", style="magenta")
            
            for domain_id, domain_data in data['domains'].items():
                health_color = _get_health_color(domain_data['health'])
                domain_table.add_row(
                    domain_id.title(),
                    f"[{health_color}]{domain_data['health']:.1%}[/{health_color}]",
                    f"{domain_data['trust']:.1%}",
                    f"{domain_data['confidence']:.1%}"
                )
            
            console.print(domain_table)
            
        except httpx.HTTPError as e:
            console.print(f"[red]Error fetching status: {e}[/red]")


async def readiness_command():
    """Display detailed SaaS readiness report"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/api/cognition/readiness")
            response.raise_for_status()
            data = response.json()
            
            console.print("\n[bold cyan]SaaS Readiness Report[/bold cyan]\n")
            
            # Readiness status
            if data['ready']:
                console.print("[bold green]🚀 READY FOR COMMERCIALIZATION[/bold green]\n")
            else:
                console.print("[bold yellow]🔧 Development Mode[/bold yellow]\n")
            
            # Benchmark table
            bench_table = Table(title="Benchmark Performance", show_header=True)
            bench_table.add_column("Metric", style="cyan")
            bench_table.add_column("Average", style="green")
            bench_table.add_column("Target", style="yellow")
            bench_table.add_column("Sustained", style="magenta")
            bench_table.add_column("Samples", style="blue")
            
            for metric_name, bench_data in data.get('benchmarks', {}).items():
                status = "✅" if bench_data['sustained'] else "🔧"
                bench_table.add_row(
                    metric_name.replace('_', ' ').title(),
                    f"{bench_data['average']:.1%}",
                    f"{bench_data['threshold']:.0%}",
                    status,
                    str(bench_data['sample_count'])
                )
            
            console.print(bench_table)
            console.print()
            
            # Next steps
            next_steps = data.get('next_steps', [])
            if next_steps:
                console.print("[bold cyan]Next Steps:[/bold cyan]")
                for i, step in enumerate(next_steps[:5], 1):
                    console.print(f"  {i}. {step}")
            
        except httpx.HTTPError as e:
            console.print(f"[red]Error fetching readiness: {e}[/red]")


async def domain_metrics_command(domain: str):
    """Display metrics for a specific domain"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/api/cognition/status")
            response.raise_for_status()
            data = response.json()
            
            domains = data.get('domains', {})
            
            if domain not in domains:
                console.print(f"[red]Domain '{domain}' not found[/red]")
                console.print(f"Available domains: {', '.join(domains.keys())}")
                return
            
            domain_data = domains[domain]
            
            console.print(f"\n[bold cyan]{domain.title()} Domain Metrics[/bold cyan]\n")
            
            # Main metrics
            main_table = Table(show_header=False)
            main_table.add_column("Metric", style="cyan")
            main_table.add_column("Value", style="green")
            
            main_table.add_row("Health", f"{domain_data['health']:.1%}")
            main_table.add_row("Trust", f"{domain_data['trust']:.1%}")
            main_table.add_row("Confidence", f"{domain_data['confidence']:.1%}")
            main_table.add_row("Last Updated", domain_data['last_updated'])
            
            console.print(main_table)
            console.print()
            
            # KPIs
            kpis = domain_data.get('kpis', {})
            if kpis:
                kpi_table = Table(title="KPIs", show_header=True)
                kpi_table.add_column("KPI", style="cyan")
                kpi_table.add_column("Value", style="green")
                
                for kpi_name, kpi_value in kpis.items():
                    if isinstance(kpi_value, float):
                        if kpi_value <= 1.0:
                            display_value = f"{kpi_value:.1%}"
                        else:
                            display_value = f"{kpi_value:.3f}"
                    else:
                        display_value = str(kpi_value)
                    
                    kpi_table.add_row(kpi_name.replace('_', ' ').title(), display_value)
                
                console.print(kpi_table)
            
        except httpx.HTTPError as e:
            console.print(f"[red]Error fetching domain metrics: {e}[/red]")


async def watch_command(interval: int = 5):
    """Watch cognition status with live updates"""
    console.print("[bold cyan]Grace Cognition Live Dashboard[/bold cyan]")
    console.print(f"Updating every {interval} seconds. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            await status_command()
            console.print(f"\n[dim]Next update in {interval}s...[/dim]")
            await asyncio.sleep(interval)
            console.clear()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped watching[/yellow]")


async def generate_report_command():
    """Generate and save SaaS readiness report"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            console.print("[cyan]Generating readiness report...[/cyan]")
            
            response = await client.post(f"{API_BASE}/api/cognition/report/generate")
            response.raise_for_status()
            data = response.json()
            
            console.print(f"[green]✓ Report generated successfully[/green]")
            console.print(f"  Path: {data['report_path']}")
            console.print(f"  Time: {data['timestamp']}")
            
        except httpx.HTTPError as e:
            console.print(f"[red]Error generating report: {e}[/red]")


async def view_report_command():
    """View the latest readiness report"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{API_BASE}/api/cognition/report/latest")
            response.raise_for_status()
            data = response.json()
            
            console.print(Panel(data['content'], title="Grace SaaS Readiness Report", border_style="cyan"))
            
        except httpx.HTTPError as e:
            console.print(f"[red]Error viewing report: {e}[/red]")


def _get_health_color(health: float) -> str:
    """Get color based on health score"""
    if health >= 0.9:
        return "green"
    elif health >= 0.7:
        return "yellow"
    else:
        return "red"


# CLI entry points
def cognition_status():
    """Entry point for 'grace cognition status'"""
    asyncio.run(status_command())


def cognition_readiness():
    """Entry point for 'grace cognition readiness'"""
    asyncio.run(readiness_command())


def cognition_watch(interval: int = 5):
    """Entry point for 'grace cognition watch'"""
    asyncio.run(watch_command(interval))


def domain_metrics(domain: str):
    """Entry point for 'grace <domain> metrics'"""
    asyncio.run(domain_metrics_command(domain))


def generate_report():
    """Entry point for 'grace cognition readiness-report'"""
    asyncio.run(generate_report_command())


def view_report():
    """Entry point for 'grace cognition view-report'"""
    asyncio.run(view_report_command())
